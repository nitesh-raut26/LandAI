"""Auth + API-key + quota business logic (framework-agnostic)."""
from __future__ import annotations

import hashlib
import re
import secrets
import time
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..metrics import METRICS
from .models import ApiKey, UsageLog, User
from .password import hash_password, verify_password
from .tiers import get_tier

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
API_KEY_PREFIX = "lk_live_"  # LandAI key

# ── in-process login brute-force throttle (per email+ip) ────────────────────
_FAILS: dict[str, list[float]] = {}
_MAX_FAILS = 5
_WINDOW = 300  # seconds


class AuthError(Exception):
    def __init__(self, status: int, detail: str) -> None:
        super().__init__(detail)
        self.status = status
        self.detail = detail


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def valid_email(email: str) -> bool:
    return bool(_EMAIL_RE.match(email or ""))


def register(db: Session, email: str, password: str) -> User:
    email = (email or "").strip().lower()
    if not valid_email(email):
        raise AuthError(422, "Invalid email address.")
    if len(password or "") < 8:
        raise AuthError(422, "Password must be at least 8 characters.")
    if db.scalar(select(User).where(User.email == email)):
        raise AuthError(409, "Email already registered.")
    user = User(email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    METRICS.incr("auth_signups")
    return user


def _key(email: str, ip: str) -> str:
    return f"{email}|{ip}"


def _recent_fails(k: str) -> list[float]:
    now = time.monotonic()
    arr = [t for t in _FAILS.get(k, []) if now - t < _WINDOW]
    _FAILS[k] = arr
    return arr


def authenticate(db: Session, email: str, password: str, ip: str = "unknown") -> User:
    email = (email or "").strip().lower()
    k = _key(email, ip)
    if len(_recent_fails(k)) >= _MAX_FAILS:
        METRICS.incr("auth_lockouts")
        raise AuthError(429, "Too many failed attempts. Try again in a few minutes.")

    user = db.scalar(select(User).where(User.email == email))
    if not user or not verify_password(password, user.password_hash):
        _FAILS.setdefault(k, []).append(time.monotonic())
        METRICS.incr("auth_login_failures")
        raise AuthError(401, "Invalid email or password.")
    if not user.is_active:
        raise AuthError(403, "Account is disabled.")

    user.last_login = datetime.now(timezone.utc)
    db.commit()
    _FAILS.pop(k, None)
    METRICS.incr("auth_logins")
    return user


# ── API keys ────────────────────────────────────────────────────────────────
def _hash_key(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def create_api_key(db: Session, user: User, name: str = "default") -> tuple[ApiKey, str]:
    full = API_KEY_PREFIX + secrets.token_urlsafe(24)
    key = ApiKey(user_id=user.id, name=(name or "default")[:80], prefix=full[:12], key_hash=_hash_key(full))
    db.add(key)
    db.commit()
    db.refresh(key)
    METRICS.incr("auth_api_keys_created")
    return key, full  # full secret returned ONCE


def resolve_api_key(db: Session, raw: str) -> tuple[User, ApiKey] | None:
    if not raw or not raw.startswith(API_KEY_PREFIX):
        return None
    key = db.scalar(select(ApiKey).where(ApiKey.key_hash == _hash_key(raw), ApiKey.revoked.is_(False)))
    if not key:
        return None
    user = db.get(User, key.user_id)
    if not user or not user.is_active:
        return None
    return user, key


def revoke_api_key(db: Session, user: User, key_id: int) -> bool:
    key = db.scalar(select(ApiKey).where(ApiKey.id == key_id, ApiKey.user_id == user.id))
    if not key:
        return False
    key.revoked = True
    db.commit()
    return True


# ── quota ───────────────────────────────────────────────────────────────────
def check_and_consume_quota(db: Session, user: User, key: ApiKey, path: str) -> dict:
    tier = get_tier(user.subscription_tier)
    today = _today()
    if user.quota_period != today:  # daily reset
        user.quota_period = today
        user.quota_used = 0

    allowed = user.quota_used < tier.daily_quota
    if allowed:
        user.quota_used += 1
        key.last_used = datetime.now(timezone.utc)
        db.add(UsageLog(user_id=user.id, api_key_id=key.id, path=path[:255], status=200))
        METRICS.incr("auth_api_requests")
    else:
        METRICS.incr("auth_quota_exceeded")
    db.commit()
    return {
        "tier": tier.key,
        "daily_quota": tier.daily_quota,
        "quota_used": user.quota_used,
        "quota_remaining": max(0, tier.daily_quota - user.quota_used),
        "rate_per_minute": tier.rate_per_minute,
        "allowed": allowed,
    }

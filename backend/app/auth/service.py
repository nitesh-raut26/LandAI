"""Auth + API-key + quota business logic (framework-agnostic)."""
from __future__ import annotations

import hashlib
import re
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import store
from ..metrics import METRICS
from .jwt import ACCESS_TTL_MIN, REFRESH_TTL_DAYS, new_family, new_jti
from .models import ApiKey, RefreshSession, UsageLog, User
from .password import hash_password, verify_password
from .tiers import get_tier

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
API_KEY_PREFIX = "lk_live_"  # LandAI key

# ── login brute-force throttle (per email+ip), backed by the shared store ────
# (Redis when configured, in-process fallback otherwise — see app.store.)
_MAX_FAILS = 5
_WINDOW = 300  # seconds
ACCESS_DENYLIST_TTL = ACCESS_TTL_MIN * 60


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


def _bf_key(email: str, ip: str) -> str:
    return f"bf:{email}:{ip}"


def authenticate(db: Session, email: str, password: str, ip: str = "unknown") -> User:
    email = (email or "").strip().lower()
    bf = _bf_key(email, ip)
    if store.get_int(bf) >= _MAX_FAILS:
        METRICS.incr("auth_lockouts")
        raise AuthError(429, "Too many failed attempts. Try again in a few minutes.")

    user = db.scalar(select(User).where(User.email == email))
    if not user or not verify_password(password, user.password_hash):
        store.incr(bf, 1, ttl=_WINDOW)
        METRICS.incr("auth_login_failures")
        raise AuthError(401, "Invalid email or password.")
    if not user.is_active:
        raise AuthError(403, "Account is disabled.")

    user.last_login = datetime.now(timezone.utc)
    db.commit()
    store.delete(bf)
    METRICS.incr("auth_logins")
    return user


# ── API keys ────────────────────────────────────────────────────────────────
def _hash_key(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def create_api_key(db: Session, user: User, name: str = "default",
                   scopes: str = "", daily_quota: int | None = None) -> tuple[ApiKey, str]:
    full = API_KEY_PREFIX + secrets.token_urlsafe(24)
    # Normalise scopes: comma-separated, deduped, trimmed; "" means full access.
    clean_scopes = ",".join(sorted({s.strip() for s in (scopes or "").split(",") if s.strip()}))
    key = ApiKey(
        user_id=user.id, name=(name or "default")[:80], prefix=full[:12], key_hash=_hash_key(full),
        scopes=clean_scopes[:255], daily_quota=daily_quota if (daily_quota and daily_quota > 0) else None,
    )
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


# ── quota + per-key rate limiting ────────────────────────────────────────────
def check_and_consume_quota(db: Session, user: User, key: ApiKey, path: str) -> dict:
    """Enforce, in order: per-key per-minute rate (shared store), then the daily
    caps — both the per-user *account ceiling* (tier) and the *per-key* quota.
    Headers/usage reflect the per-key view; the account ceiling is the hard cap."""
    tier = get_tier(user.subscription_tier)
    today = _today()
    if user.quota_period != today:           # per-user (account) daily reset
        user.quota_period, user.quota_used = today, 0
    if key.quota_period != today:            # per-key daily reset
        key.quota_period, key.quota_used = today, 0

    key_limit = key.daily_quota or tier.daily_quota

    def _result(allowed: bool, reason: str, rate_remaining: int) -> dict:
        return {
            "allowed": allowed, "reason": reason, "tier": tier.key,
            "daily_quota": key_limit, "quota_used": key.quota_used,
            "quota_remaining": max(0, key_limit - key.quota_used),
            "rate_per_minute": tier.rate_per_minute, "rate_remaining": rate_remaining,
        }

    # 1) per-key sliding rate (Redis when configured, in-process fallback otherwise)
    rate_ok, rate_remaining = store.rate_allow(f"rl:key:{key.id}", tier.rate_per_minute, 60)
    if not rate_ok:
        METRICS.incr("auth_rate_throttled")
        db.add(UsageLog(user_id=user.id, api_key_id=key.id, path=path[:255], status=429))
        db.commit()
        return _result(False, "rate", 0)

    # 2) daily caps: account ceiling AND per-key quota
    allowed = (user.quota_used < tier.daily_quota) and (key.quota_used < key_limit)
    if allowed:
        user.quota_used += 1
        key.quota_used += 1
        key.last_used = datetime.now(timezone.utc)
        db.add(UsageLog(user_id=user.id, api_key_id=key.id, path=path[:255], status=200))
        METRICS.incr("auth_api_requests")
    else:
        db.add(UsageLog(user_id=user.id, api_key_id=key.id, path=path[:255], status=429))
        METRICS.incr("auth_quota_exceeded")
    db.commit()
    return _result(allowed, "ok" if allowed else "quota", rate_remaining)


# ── refresh-session lifecycle (rotation, revocation, reuse detection) ────────
def _device_label(ua: str) -> str:
    ua = (ua or "").lower()
    if not ua:
        return "Unknown device"
    kind = "Mobile" if any(s in ua for s in ("mobile", "android", "iphone", "ipad")) else "Desktop"
    for tok, name in (("edg", "Edge"), ("chrome", "Chrome"), ("firefox", "Firefox"), ("safari", "Safari")):
        if tok in ua:
            return f"{name} · {kind}"
    return kind


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def create_session(db: Session, user: User, *, ip: str = "", user_agent: str = "", family: str | None = None) -> tuple[str, str]:
    """Persist a refresh session (jti) and return (jti, family_id)."""
    jti, fam = new_jti(), (family or new_family())
    db.add(RefreshSession(
        user_id=user.id, jti=jti, family_id=fam,
        device_label=_device_label(user_agent), ip=(ip or "")[:64], user_agent=(user_agent or "")[:256],
        expires_at=_now() + timedelta(days=REFRESH_TTL_DAYS),
    ))
    db.commit()
    return jti, fam


def get_session(db: Session, jti: str) -> RefreshSession | None:
    return db.scalar(select(RefreshSession).where(RefreshSession.jti == jti))


def session_active(sess: RefreshSession | None) -> bool:
    return bool(sess and sess.revoked_at is None and _aware(sess.expires_at) > _now())


def _denylist_family(fam: str) -> None:
    # Make access tokens carrying this family fail immediately (TTL = access TTL).
    store.mark(f"dl:fam:{fam}", ACCESS_DENYLIST_TTL)


def family_denylisted(fam: str) -> bool:
    return store.is_marked(f"dl:fam:{fam}")


def rotate_session(db: Session, old: RefreshSession, user: User, *, ip: str = "", user_agent: str = "") -> tuple[str, str]:
    """Revoke the presented refresh jti and issue a new one in the same family.
    Does NOT denylist the family — the family stays valid; only this jti rotates."""
    old.revoked_at, old.last_used = _now(), _now()
    db.commit()
    return create_session(db, user, ip=ip, user_agent=user_agent, family=old.family_id)


def revoke_session(db: Session, sess: RefreshSession) -> None:
    """Logout of a single device — revoke the jti and denylist its family."""
    if sess.revoked_at is None:
        sess.revoked_at = _now()
        db.commit()
    _denylist_family(sess.family_id)


def revoke_family(db: Session, family_id: str) -> int:
    """Reuse-detection response — revoke every jti in the family + denylist it."""
    rows = db.scalars(select(RefreshSession).where(
        RefreshSession.family_id == family_id, RefreshSession.revoked_at.is_(None))).all()
    now = _now()
    for r in rows:
        r.revoked_at = now
    db.commit()
    _denylist_family(family_id)
    return len(rows)


def revoke_user_sessions(db: Session, user_id: int) -> int:
    """Logout-all — revoke every active session for a user."""
    rows = db.scalars(select(RefreshSession).where(
        RefreshSession.user_id == user_id, RefreshSession.revoked_at.is_(None))).all()
    now, fams = _now(), set()
    for r in rows:
        r.revoked_at = now
        fams.add(r.family_id)
    db.commit()
    for f in fams:
        _denylist_family(f)
    return len(rows)


def active_sessions(db: Session, user_id: int) -> list[RefreshSession]:
    rows = db.scalars(select(RefreshSession).where(
        RefreshSession.user_id == user_id, RefreshSession.revoked_at.is_(None)
    ).order_by(RefreshSession.id.desc())).all()
    return [s for s in rows if session_active(s)]

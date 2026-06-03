"""FastAPI auth dependencies: JWT bearer user, RBAC guard, API-key + quota."""
from __future__ import annotations

from fastapi import Depends, Header, HTTPException, Request, Response
from sqlalchemy.orm import Session

from ..db import get_db
from . import service
from .jwt import decode_token
from .models import User


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Missing bearer token.")
    payload = decode_token(authorization.split(" ", 1)[1].strip())
    if not payload or payload.get("type") != "access":
        raise HTTPException(401, "Invalid or expired token.")
    # Server-side revocation: a logged-out / revoked session denylists its token
    # family for the access-token TTL. Legacy tokens without `fam` skip this.
    fam = payload.get("fam")
    if fam and service.family_denylisted(fam):
        raise HTTPException(401, "Session has been revoked — please sign in again.")
    user = db.get(User, int(payload.get("sub") or 0))
    if not user or not user.is_active:
        raise HTTPException(401, "User not found or inactive.")
    return user


def get_optional_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User | None:
    if not authorization:
        return None
    try:
        return get_current_user(authorization, db)
    except HTTPException:
        return None


def require_role(*roles: str):
    def _dep(user: User = Depends(get_current_user)) -> User:
        if user.role != "admin" and user.role not in roles:
            raise HTTPException(403, f"Requires role: {', '.join(roles)}.")
        return user

    return _dep


PRO_TIERS = frozenset({"pro", "enterprise"})


def require_pro(user: User = Depends(get_current_user)) -> User:
    """Gate a route behind a paid (Pro/Enterprise) subscription. Admins always pass.

    Tier is read fresh from the DB via ``get_current_user`` (not the token claim),
    so an upgrade takes effect immediately without re-login. Returns a structured
    403 with an upgrade CTA for free-tier users — the monetization gate.
    """
    if user.role != "admin" and user.subscription_tier not in PRO_TIERS:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "pro_required",
                "message": "This feature requires a Pro or Enterprise subscription.",
                "upgrade_url": "/api/billing/checkout",
                "current_tier": user.subscription_tier,
                "required_tier": "pro",
            },
        )
    return user


def _endpoint_scope(path: str) -> str | None:
    """Scope = the path segment after /v1 (e.g. /api/v1/city/pune → 'city')."""
    parts = [p for p in path.split("/") if p]
    if "v1" in parts:
        i = parts.index("v1")
        if i + 1 < len(parts):
            return parts[i + 1]
    return None


def require_api_key(
    request: Request,
    response: Response,
    x_api_key: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    """Authenticate via X-API-Key (or ?api_key=), enforce key scopes, per-key
    rate + daily quota, and stamp X-Quota-* / X-RateLimit-* headers."""
    raw = x_api_key or request.query_params.get("api_key") or ""
    resolved = service.resolve_api_key(db, raw)
    if not resolved:
        raise HTTPException(401, "Invalid or missing API key — send it in the X-API-Key header.")
    user, key = resolved

    # Scope enforcement (empty scopes = full access).
    if key.scopes:
        allowed_scopes = {s.strip() for s in key.scopes.split(",") if s.strip()}
        scope = _endpoint_scope(request.url.path)
        if scope and scope not in allowed_scopes:
            raise HTTPException(
                status_code=403,
                detail={"error": "scope_forbidden", "required_scope": scope, "key_scopes": sorted(allowed_scopes)},
            )

    q = service.check_and_consume_quota(db, user, key, request.url.path)
    response.headers["X-RateLimit-Limit"] = str(q["rate_per_minute"])
    response.headers["X-RateLimit-Remaining"] = str(q["rate_remaining"])
    response.headers["X-Quota-Used"] = str(q["quota_used"])
    response.headers["X-Quota-Remaining"] = str(q["quota_remaining"])
    if not q["allowed"]:
        if q["reason"] == "rate":
            raise HTTPException(
                status_code=429,
                detail={"error": "rate_limit_exceeded", "rate_per_minute": q["rate_per_minute"]},
                headers={"Retry-After": "60", "X-RateLimit-Remaining": "0"},
            )
        raise HTTPException(
            status_code=429,
            detail={"error": "quota_exceeded", "tier": q["tier"], "daily_quota": q["daily_quota"], "quota_used": q["quota_used"]},
        )
    return user

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


def require_api_key(
    request: Request,
    response: Response,
    x_api_key: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    """Authenticate via X-API-Key (or ?api_key=), enforce daily quota, and stamp
    X-Quota-* / X-RateLimit-* headers on the response."""
    raw = x_api_key or request.query_params.get("api_key") or ""
    resolved = service.resolve_api_key(db, raw)
    if not resolved:
        raise HTTPException(401, "Invalid or missing API key — send it in the X-API-Key header.")
    user, key = resolved
    q = service.check_and_consume_quota(db, user, key, request.url.path)
    response.headers["X-Quota-Used"] = str(q["quota_used"])
    response.headers["X-Quota-Remaining"] = str(q["quota_remaining"])
    response.headers["X-RateLimit-Limit"] = str(q["rate_per_minute"])
    if not q["allowed"]:
        raise HTTPException(
            status_code=429,
            detail={"error": "quota_exceeded", "tier": q["tier"], "daily_quota": q["daily_quota"], "quota_used": q["quota_used"]},
        )
    return user

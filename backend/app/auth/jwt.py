"""
JWT access + refresh tokens (python-jose, HS256).

Secret is loaded from ``JWT_SECRET``. In dev (no env secret) an **ephemeral**
per-process secret is generated, so tokens do not survive a restart — fine for
local use, never for production. ``SECRET_IS_EPHEMERAL`` exposes this honestly.
"""
from __future__ import annotations

import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

ALGORITHM = "HS256"
ACCESS_TTL_MIN = int(os.getenv("JWT_ACCESS_TTL_MIN", "30"))
REFRESH_TTL_DAYS = int(os.getenv("JWT_REFRESH_TTL_DAYS", "14"))

SECRET_IS_EPHEMERAL = "JWT_SECRET" not in os.environ
JWT_SECRET = os.getenv("JWT_SECRET") or secrets.token_urlsafe(48)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(sub: str, claims: dict | None = None) -> str:
    payload = {"sub": str(sub), "type": "access", "iat": _now(), "exp": _now() + timedelta(minutes=ACCESS_TTL_MIN)}
    if claims:
        payload.update(claims)
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)


def create_refresh_token(sub: str, jti: str | None = None, family: str | None = None) -> str:
    payload = {
        "sub": str(sub), "type": "refresh",
        "jti": jti or secrets.token_urlsafe(12),
        "fam": family or secrets.token_urlsafe(12),
        "iat": _now(), "exp": _now() + timedelta(days=REFRESH_TTL_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)


def new_jti() -> str:
    return secrets.token_urlsafe(12)


def new_family() -> str:
    return secrets.token_urlsafe(12)


def decode_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    except JWTError:
        return None

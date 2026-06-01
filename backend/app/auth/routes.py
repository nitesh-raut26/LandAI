"""Auth, API-key, and account routes."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from . import service
from .dependencies import get_current_user
from .jwt import ACCESS_TTL_MIN, create_access_token, create_refresh_token, decode_token
from .models import ApiKey, SavedCity, User
from .schemas import (
    ApiKeyCreated, ApiKeyOut, LoginIn, RefreshIn, RegisterIn,
    SavedCityIn, SavedCityOut, TokenOut, UserOut,
)
from .tiers import get_tier, tiers_public

auth_router = APIRouter(prefix="/auth", tags=["auth"])
keys_router = APIRouter(prefix="/keys", tags=["api-keys"])
account_router = APIRouter(prefix="/account", tags=["account"])


def _client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    return xff.split(",")[0].strip() if xff else (request.client.host if request.client else "unknown")


def _tokens(user: User) -> TokenOut:
    access = create_access_token(user.id, {"role": user.role, "tier": user.subscription_tier})
    return TokenOut(access_token=access, refresh_token=create_refresh_token(user.id), expires_in=ACCESS_TTL_MIN * 60)


# ── auth ────────────────────────────────────────────────────────────────────
@auth_router.post("/register", response_model=TokenOut, status_code=201)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    try:
        user = service.register(db, body.email, body.password)
    except service.AuthError as e:
        raise HTTPException(e.status, e.detail)
    return _tokens(user)


@auth_router.post("/login", response_model=TokenOut)
def login(body: LoginIn, request: Request, db: Session = Depends(get_db)):
    try:
        user = service.authenticate(db, body.email, body.password, ip=_client_ip(request))
    except service.AuthError as e:
        raise HTTPException(e.status, e.detail)
    return _tokens(user)


@auth_router.post("/refresh", response_model=TokenOut)
def refresh(body: RefreshIn, db: Session = Depends(get_db)):
    payload = decode_token(body.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(401, "Invalid or expired refresh token.")
    user = db.get(User, int(payload.get("sub") or 0))
    if not user or not user.is_active:
        raise HTTPException(401, "User not found or inactive.")
    return _tokens(user)


@auth_router.post("/logout")
def logout():
    # Stateless JWT: the client discards tokens. A server-side jti denylist for
    # true revocation is the documented next step.
    return {"ok": True, "note": "Discard tokens client-side; server-side revocation is on the roadmap."}


@auth_router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@auth_router.post("/google")
def google_oauth():
    # Env-gated OAuth scaffold — NOT a working Google flow (honest 501).
    raise HTTPException(
        501,
        "Google OAuth is scaffolded but not implemented. Set GOOGLE_CLIENT_ID/SECRET and complete auth/oauth.py.",
    )


@auth_router.get("/tiers")
def list_tiers():
    return {"tiers": tiers_public(), "billing": "architecture only — no live payments"}


# ── API keys ────────────────────────────────────────────────────────────────
@keys_router.get("", response_model=list[ApiKeyOut])
def list_keys(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(select(ApiKey).where(ApiKey.user_id == user.id).order_by(ApiKey.id.desc())).all()


@keys_router.post("", response_model=ApiKeyCreated, status_code=201)
def create_key(name: str = Body("default", embed=True), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    key, full = service.create_api_key(db, user, name)
    return ApiKeyCreated(id=key.id, name=key.name, prefix=key.prefix, api_key=full, created_at=key.created_at)


@keys_router.post("/{key_id}/regenerate", response_model=ApiKeyCreated, status_code=201)
def regenerate_key(key_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    old = db.scalar(select(ApiKey).where(ApiKey.id == key_id, ApiKey.user_id == user.id))
    if not old:
        raise HTTPException(404, "API key not found.")
    old.revoked = True
    key, full = service.create_api_key(db, user, old.name)
    db.commit()
    return ApiKeyCreated(id=key.id, name=key.name, prefix=key.prefix, api_key=full, created_at=key.created_at)


@keys_router.delete("/{key_id}")
def revoke_key(key_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not service.revoke_api_key(db, user, key_id):
        raise HTTPException(404, "API key not found.")
    return {"ok": True, "revoked": key_id}


# ── account (persistent platform features) ──────────────────────────────────
@account_router.get("/usage")
def usage(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tier = get_tier(user.subscription_tier)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    used = user.quota_used if user.quota_period == today else 0
    n_keys = db.scalar(select(func.count(ApiKey.id)).where(ApiKey.user_id == user.id, ApiKey.revoked.is_(False))) or 0
    return {
        "tier": tier.key, "tier_name": tier.name,
        "daily_quota": tier.daily_quota, "quota_used": used,
        "quota_remaining": max(0, tier.daily_quota - used),
        "rate_per_minute": tier.rate_per_minute,
        "features": sorted(tier.features),
        "active_api_keys": n_keys,
        "billing": "not-live (architecture only)",
    }


@account_router.get("/saved-cities", response_model=list[SavedCityOut])
def list_saved(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(select(SavedCity).where(SavedCity.user_id == user.id).order_by(SavedCity.id.desc())).all()


@account_router.post("/saved-cities", response_model=SavedCityOut, status_code=201)
def add_saved(body: SavedCityIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.scalar(select(SavedCity).where(SavedCity.user_id == user.id, SavedCity.city_id == body.city_id))
    if existing:
        return existing
    sc = SavedCity(user_id=user.id, city_id=body.city_id, note=body.note)
    db.add(sc)
    db.commit()
    db.refresh(sc)
    return sc


@account_router.delete("/saved-cities/{city_id}")
def del_saved(city_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sc = db.scalar(select(SavedCity).where(SavedCity.user_id == user.id, SavedCity.city_id == city_id))
    if not sc:
        raise HTTPException(404, "Not in saved list.")
    db.delete(sc)
    db.commit()
    return {"ok": True}

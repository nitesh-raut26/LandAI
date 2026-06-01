"""Auth, API-key, and account routes."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from . import service
from .dependencies import get_current_user
from .jwt import ACCESS_TTL_MIN, create_access_token, create_refresh_token, decode_token
from .models import ApiKey, CompareHistory, SavedCity, SavedSearch, UsageLog, User, WatchlistItem
from .schemas import (
    ApiKeyCreated, ApiKeyOut, CompareIn, CompareOut, LoginIn, RefreshIn, RegisterIn,
    SavedCityIn, SavedCityOut, SavedSearchIn, SavedSearchOut, TokenOut, UserOut,
    WatchItemIn, WatchItemOut,
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


# ── watchlist (server-synced monitored list) ────────────────────────────────
@account_router.get("/watchlist", response_model=list[WatchItemOut])
def list_watchlist(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(select(WatchlistItem).where(WatchlistItem.user_id == user.id).order_by(WatchlistItem.id.desc())).all()


@account_router.post("/watchlist", response_model=WatchItemOut, status_code=201)
def add_watch(body: WatchItemIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.scalar(select(WatchlistItem).where(WatchlistItem.user_id == user.id, WatchlistItem.city_id == body.city_id))
    if existing:
        return existing  # idempotent — safe for client merge-sync
    item = WatchlistItem(user_id=user.id, city_id=body.city_id[:64])
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@account_router.delete("/watchlist/{city_id}")
def del_watch(city_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.scalar(select(WatchlistItem).where(WatchlistItem.user_id == user.id, WatchlistItem.city_id == city_id))
    if not item:
        raise HTTPException(404, "Not in watchlist.")
    db.delete(item)
    db.commit()
    return {"ok": True}


# ── compare history ─────────────────────────────────────────────────────────
@account_router.get("/compare-history", response_model=list[CompareOut])
def list_compares(limit: int = 20, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    limit = max(1, min(limit, 100))
    return db.scalars(
        select(CompareHistory).where(CompareHistory.user_id == user.id)
        .order_by(CompareHistory.id.desc()).limit(limit)
    ).all()


@account_router.post("/compare-history", response_model=CompareOut, status_code=201)
def add_compare(body: CompareIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Collapse an immediate duplicate of the most recent pair (either order).
    last = db.scalar(
        select(CompareHistory).where(CompareHistory.user_id == user.id).order_by(CompareHistory.id.desc())
    )
    pair = {body.city_a, body.city_b}
    if last and {last.city_a, last.city_b} == pair:
        return last
    ch = CompareHistory(user_id=user.id, city_a=body.city_a[:64], city_b=body.city_b[:64])
    db.add(ch)
    db.commit()
    db.refresh(ch)
    return ch


@account_router.delete("/compare-history/{item_id}")
def del_compare(item_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ch = db.scalar(select(CompareHistory).where(CompareHistory.id == item_id, CompareHistory.user_id == user.id))
    if not ch:
        raise HTTPException(404, "Not found.")
    db.delete(ch)
    db.commit()
    return {"ok": True}


# ── saved searches ──────────────────────────────────────────────────────────
def _search_out(s: SavedSearch) -> SavedSearchOut:
    try:
        q = json.loads(s.query) if s.query else {}
    except (ValueError, TypeError):
        q = {}
    return SavedSearchOut(id=s.id, label=s.label, query=q, created_at=s.created_at)


@account_router.get("/saved-searches", response_model=list[SavedSearchOut])
def list_searches(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(SavedSearch).where(SavedSearch.user_id == user.id).order_by(SavedSearch.id.desc())).all()
    return [_search_out(s) for s in rows]


@account_router.post("/saved-searches", response_model=SavedSearchOut, status_code=201)
def add_search(body: SavedSearchIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Only keep known filter keys; ignore anything else the client sends.
    q = {k: body.query[k] for k in ("q", "state", "tier", "phase") if k in body.query and body.query[k] not in (None, "")}
    label = (body.label or q.get("q") or q.get("state") or q.get("phase") or "Saved search")[:120]
    s = SavedSearch(user_id=user.id, label=label, query=json.dumps(q))
    db.add(s)
    db.commit()
    db.refresh(s)
    return _search_out(s)


@account_router.delete("/saved-searches/{item_id}")
def del_search(item_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    s = db.scalar(select(SavedSearch).where(SavedSearch.id == item_id, SavedSearch.user_id == user.id))
    if not s:
        raise HTTPException(404, "Not found.")
    db.delete(s)
    db.commit()
    return {"ok": True}


# ── dashboards ──────────────────────────────────────────────────────────────
@account_router.get("/dashboard")
def dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Aggregate summary for the User Dashboard — counts + recent activity."""
    tier = get_tier(user.subscription_tier)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    used = user.quota_used if user.quota_period == today else 0

    def _count(model, *where):
        return db.scalar(select(func.count(model.id)).where(*where)) or 0

    recent = db.scalars(
        select(CompareHistory).where(CompareHistory.user_id == user.id)
        .order_by(CompareHistory.id.desc()).limit(5)
    ).all()
    watch = db.scalars(select(WatchlistItem.city_id).where(WatchlistItem.user_id == user.id)).all()

    return {
        "tier": tier.key, "tier_name": tier.name,
        "daily_quota": tier.daily_quota, "quota_used": used,
        "quota_remaining": max(0, tier.daily_quota - used),
        "rate_per_minute": tier.rate_per_minute,
        "features": sorted(tier.features),
        "counts": {
            "watchlist": len(watch),
            "saved_cities": _count(SavedCity, SavedCity.user_id == user.id),
            "saved_searches": _count(SavedSearch, SavedSearch.user_id == user.id),
            "api_keys": _count(ApiKey, ApiKey.user_id == user.id, ApiKey.revoked.is_(False)),
            "compares": _count(CompareHistory, CompareHistory.user_id == user.id),
        },
        "watchlist": list(watch),
        "recent_compares": [
            {"id": c.id, "city_a": c.city_a, "city_b": c.city_b, "created_at": c.created_at.isoformat()}
            for c in recent
        ],
        "billing": "not-live (architecture only)",
    }


@account_router.get("/usage-history")
def usage_history(days: int = 30, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Real metered-API usage aggregated from usage_logs (this user's keys only).

    Honest empty state when the user hasn't called the metered ``/api/v1`` surface
    yet — web-app ``/api/*`` calls are intentionally not metered or logged here.
    """
    days = max(1, min(days, 365))
    cutoff = datetime.now(timezone.utc) - timedelta(days=days - 1)
    base = (UsageLog.user_id == user.id, UsageLog.at >= cutoff)

    day = func.date(UsageLog.at)
    by_day = dict(
        db.execute(select(day, func.count(UsageLog.id)).where(*base).group_by(day)).all()
    )
    # Zero-filled day series so the chart shows the real shape, gaps included.
    start = (datetime.now(timezone.utc) - timedelta(days=days - 1)).date()
    series = []
    for i in range(days):
        d = (start + timedelta(days=i)).isoformat()
        series.append({"date": d, "count": int(by_day.get(d, 0))})

    by_endpoint = [
        {"path": p, "count": int(n)}
        for p, n in db.execute(
            select(UsageLog.path, func.count(UsageLog.id)).where(*base)
            .group_by(UsageLog.path).order_by(func.count(UsageLog.id).desc()).limit(8)
        ).all()
    ]
    by_status = {
        str(s): int(n)
        for s, n in db.execute(select(UsageLog.status, func.count(UsageLog.id)).where(*base).group_by(UsageLog.status)).all()
    }
    by_key = [
        {"prefix": prefix, "name": name, "count": int(n)}
        for prefix, name, n in db.execute(
            select(ApiKey.prefix, ApiKey.name, func.count(UsageLog.id))
            .join(ApiKey, ApiKey.id == UsageLog.api_key_id).where(*base)
            .group_by(ApiKey.id).order_by(func.count(UsageLog.id).desc()).limit(10)
        ).all()
    ]
    total = sum(pt["count"] for pt in series)
    return {
        "days": days,
        "total_requests": total,
        "series": series,
        "by_endpoint": by_endpoint,
        "by_key": by_key,
        "by_status": by_status,
        "note": "Metered Developer API usage from your API keys. Web-app calls are not metered.",
    }

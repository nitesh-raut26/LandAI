"""Auth, API-key, and account routes."""
from __future__ import annotations

import json
import os
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from . import audit, oauth, service
from .dependencies import get_current_user
from .jwt import ACCESS_TTL_MIN, create_access_token, create_refresh_token, decode_token
from .models import ApiKey, CompareHistory, RefreshSession, SavedCity, SavedSearch, UsageLog, User, WatchlistItem
from .schemas import (
    ApiKeyCreated, ApiKeyOut, CompareIn, CompareOut, LoginIn, RefreshIn, RegisterIn,
    SavedCityIn, SavedCityOut, SavedSearchIn, SavedSearchOut, SessionOut, TokenOut, UserOut,
    WatchItemIn, WatchItemOut,
)
from .tiers import get_tier, tiers_public

auth_router = APIRouter(prefix="/auth", tags=["auth"])
keys_router = APIRouter(prefix="/keys", tags=["api-keys"])
account_router = APIRouter(prefix="/account", tags=["account"])


def _client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    return xff.split(",")[0].strip() if xff else (request.client.host if request.client else "unknown")


def _tokens_for(user: User, jti: str, fam: str) -> TokenOut:
    access = create_access_token(user.id, {"role": user.role, "tier": user.subscription_tier, "fam": fam})
    refresh = create_refresh_token(user.id, jti=jti, family=fam)
    return TokenOut(access_token=access, refresh_token=refresh, expires_in=ACCESS_TTL_MIN * 60)


def _issue_tokens(db: Session, user: User, request: Request, family: str | None = None) -> TokenOut:
    jti, fam = service.create_session(
        db, user, ip=_client_ip(request), user_agent=request.headers.get("user-agent", ""), family=family,
    )
    return _tokens_for(user, jti, fam)


# ── auth ────────────────────────────────────────────────────────────────────
@auth_router.post("/register", response_model=TokenOut, status_code=201)
def register(body: RegisterIn, request: Request, db: Session = Depends(get_db)):
    try:
        user = service.register(db, body.email, body.password)
    except service.AuthError as e:
        raise HTTPException(e.status, e.detail)
    audit.log_event(db, "signup", user_id=user.id, ip=_client_ip(request))
    return _issue_tokens(db, user, request)


@auth_router.post("/login", response_model=TokenOut)
def login(body: LoginIn, request: Request, db: Session = Depends(get_db)):
    ip = _client_ip(request)
    try:
        user = service.authenticate(db, body.email, body.password, ip=ip)
    except service.AuthError as e:
        audit.log_event(db, "lockout" if e.status == 429 else "login_failed",
                        ip=ip, meta={"email": (body.email or "")[:120]})
        raise HTTPException(e.status, e.detail)
    audit.log_event(db, "login", user_id=user.id, ip=ip)
    return _issue_tokens(db, user, request)


@auth_router.post("/refresh", response_model=TokenOut)
def refresh(body: RefreshIn, request: Request, db: Session = Depends(get_db)):
    payload = decode_token(body.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(401, "Invalid or expired refresh token.")
    sess = service.get_session(db, payload.get("jti") or "")
    if sess is None:
        raise HTTPException(401, "Refresh token not recognized — please sign in again.")
    if sess.revoked_at is not None:
        # Replay of an already-rotated token → assume compromise; burn the family.
        service.revoke_family(db, sess.family_id)
        audit.log_event(db, "reuse_detected", user_id=sess.user_id, ip=_client_ip(request),
                        target_type="session", target_id=sess.id, meta={"family": sess.family_id})
        raise HTTPException(401, "Refresh token reuse detected — all sessions in this family were revoked.")
    if not service.session_active(sess):
        raise HTTPException(401, "Refresh token expired — please sign in again.")
    user = db.get(User, sess.user_id)
    if not user or not user.is_active:
        raise HTTPException(401, "User not found or inactive.")
    jti, fam = service.rotate_session(
        db, sess, user, ip=_client_ip(request), user_agent=request.headers.get("user-agent", ""))
    audit.log_event(db, "refresh_rotated", user_id=user.id, ip=_client_ip(request),
                    target_type="session", target_id=sess.id)
    return _tokens_for(user, jti, fam)


@auth_router.post("/logout")
def logout(request: Request, body: RefreshIn | None = None, db: Session = Depends(get_db)):
    """Real server-side logout: revoke the presented refresh session and denylist
    its token family so the matching access token dies immediately. Idempotent."""
    if body and body.refresh_token:
        payload = decode_token(body.refresh_token)
        if payload and payload.get("type") == "refresh":
            sess = service.get_session(db, payload.get("jti") or "")
            if sess:
                service.revoke_session(db, sess)
                audit.log_event(db, "logout", user_id=sess.user_id, ip=_client_ip(request),
                                target_type="session", target_id=sess.id)
    return {"ok": True}


@auth_router.post("/logout-all")
def logout_all(request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Revoke every active session for the user (sign out on all devices)."""
    n = service.revoke_user_sessions(db, user.id)
    audit.log_event(db, "logout_all", user_id=user.id, ip=_client_ip(request), meta={"revoked": n})
    return {"ok": True, "revoked_sessions": n}


@auth_router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@auth_router.post("/google", response_model=TokenOut)
def google_oauth(
    request: Request,
    credential: str = Body(..., embed=True, description="Google ID token from Google Identity Services"),
    db: Session = Depends(get_db),
):
    """Sign in with Google (Identity Services). The SPA obtains an ID-token
    ``credential`` from the Google button and posts it here; we verify it against
    Google's JWKS, find-or-create the user, and issue our own JWTs."""
    if not oauth.enabled():
        raise HTTPException(501, "Google OAuth is not configured. Set GOOGLE_CLIENT_ID to enable it.")
    claims = oauth.verify_id_token(credential)
    if not claims:
        raise HTTPException(401, "Invalid Google credential.")
    user = service.get_or_create_oauth_user(db, claims["email"])
    audit.log_event(db, "login", user_id=user.id, ip=_client_ip(request), meta={"via": "google"})
    return _issue_tokens(db, user, request)


@auth_router.get("/google/login")
def google_login():
    """Begin the Google authorization-code redirect flow. Returns the consent URL
    + a CSRF ``state`` the client should echo back. Needs GOOGLE_CLIENT_SECRET."""
    if not oauth.code_flow_enabled():
        raise HTTPException(501, "Google OAuth code flow not configured (need GOOGLE_CLIENT_ID + SECRET).")
    state = secrets.token_urlsafe(16)
    return {"authorize_url": oauth.authorization_url(state), "state": state}


@auth_router.get("/google/callback")
def google_callback(request: Request, code: str = "", state: str = "", db: Session = Depends(get_db)):
    """OAuth redirect target: exchange the code, verify the ID token, issue our
    JWTs, and bounce back to the SPA with tokens in the URL fragment."""
    if not oauth.code_flow_enabled():
        raise HTTPException(501, "Google OAuth code flow not configured.")
    claims = oauth.exchange_code(code)
    if not claims:
        raise HTTPException(401, "Google authorization failed.")
    user = service.get_or_create_oauth_user(db, claims["email"])
    audit.log_event(db, "login", user_id=user.id, ip=_client_ip(request), meta={"via": "google_code"})
    tokens = _issue_tokens(db, user, request)
    frontend = os.getenv("FRONTEND_URL", "http://localhost:5173")
    frag = f"access_token={tokens.access_token}&refresh_token={tokens.refresh_token}"
    return RedirectResponse(url=f"{frontend}/login#{frag}", status_code=302)


@auth_router.get("/google/status")
def google_status():
    """Whether Google sign-in is available (honest, env-gated) — drives the UI button."""
    return {"enabled": oauth.enabled(), "code_flow": oauth.code_flow_enabled()}


@auth_router.get("/tiers")
def list_tiers():
    return {"tiers": tiers_public(), "billing": "architecture only — no live payments"}


# ── API keys ────────────────────────────────────────────────────────────────
@keys_router.get("", response_model=list[ApiKeyOut])
def list_keys(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(select(ApiKey).where(ApiKey.user_id == user.id).order_by(ApiKey.id.desc())).all()


@keys_router.post("", response_model=ApiKeyCreated, status_code=201)
def create_key(
    name: str = Body("default", embed=True),
    scopes: str = Body("", embed=True),
    daily_quota: int | None = Body(None, embed=True),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    key, full = service.create_api_key(db, user, name, scopes=scopes, daily_quota=daily_quota)
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


# ── device / session management ─────────────────────────────────────────────
@account_router.get("/sessions", response_model=list[SessionOut])
def list_sessions(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return service.active_sessions(db, user.id)


@account_router.delete("/sessions/{session_id}")
def revoke_one_session(session_id: int, request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sess = db.scalar(select(RefreshSession).where(RefreshSession.id == session_id, RefreshSession.user_id == user.id))
    if not sess:
        raise HTTPException(404, "Session not found.")
    service.revoke_session(db, sess)
    audit.log_event(db, "session_revoked", user_id=user.id, ip=_client_ip(request),
                    target_type="session", target_id=sess.id)
    return {"ok": True, "revoked": session_id}


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

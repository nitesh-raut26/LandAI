"""API keys, metered developer API, quota enforcement, RBAC, persistence."""
import uuid
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.auth.models import User
from app.db import SessionLocal
from app.main import app

client = TestClient(app)


def _auth():
    email = f"k{uuid.uuid4().hex[:10]}@example.com"
    tok = client.post("/api/auth/register", json={"email": email, "password": "supersecret1"}).json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}, email


def test_create_list_revoke_key():
    h, _ = _auth()
    created = client.post("/api/keys", json={"name": "ci"}, headers=h)
    assert created.status_code == 201
    body = created.json()
    assert body["api_key"].startswith("lk_live_")
    assert body["prefix"] in body["api_key"]  # prefix is part of the secret

    keys = client.get("/api/keys", headers=h).json()
    assert any(k["id"] == body["id"] for k in keys)
    assert all("api_key" not in k for k in keys)  # secret never returned again

    assert client.delete(f"/api/keys/{body['id']}", headers=h).status_code == 200


def test_keys_require_auth():
    assert client.get("/api/keys").status_code == 401
    assert client.post("/api/keys", json={"name": "x"}).status_code == 401


def test_regenerate_key():
    h, _ = _auth()
    first = client.post("/api/keys", json={"name": "ci"}, headers=h).json()
    regen = client.post(f"/api/keys/{first['id']}/regenerate", headers=h)
    assert regen.status_code == 201
    assert regen.json()["api_key"] != first["api_key"]
    # old key is revoked → rejected by the metered API
    assert client.get("/api/v1/city/pune", headers={"X-API-Key": first["api_key"]}).status_code == 401


def test_metered_api_requires_key():
    assert client.get("/api/v1/city/pune").status_code == 401
    assert client.get("/api/v1/city/pune", headers={"X-API-Key": "lk_live_bogus"}).status_code == 401


def test_metered_api_with_key_sets_quota_headers():
    h, _ = _auth()
    key = client.post("/api/keys", json={"name": "ci"}, headers=h).json()["api_key"]
    r = client.get("/api/v1/city/pune", headers={"X-API-Key": key})
    assert r.status_code == 200
    assert "X-Quota-Used" in r.headers
    assert "X-Quota-Remaining" in r.headers
    assert "X-RateLimit-Limit" in r.headers
    assert int(r.headers["X-Quota-Used"]) >= 1


def test_revoked_key_rejected():
    h, _ = _auth()
    created = client.post("/api/keys", json={"name": "ci"}, headers=h).json()
    client.delete(f"/api/keys/{created['id']}", headers=h)
    assert client.get("/api/v1/city/pune", headers={"X-API-Key": created["api_key"]}).status_code == 401


def test_quota_exhaustion_returns_429():
    h, email = _auth()
    key = client.post("/api/keys", json={"name": "ci"}, headers=h).json()["api_key"]
    with SessionLocal() as db:  # exhaust quota directly (developer = 1000/day)
        u = db.scalar(select(User).where(User.email == email))
        u.quota_used = 1000
        u.quota_period = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        db.commit()
    r = client.get("/api/v1/city/pune", headers={"X-API-Key": key})
    assert r.status_code == 429
    assert r.json()["detail"]["error"] == "quota_exceeded"


def test_rbac_admin_metrics():
    h, email = _auth()
    assert client.get("/api/system/auth-metrics", headers=h).status_code == 403  # normal user
    with SessionLocal() as db:
        db.scalar(select(User).where(User.email == email)).role = "admin"
        db.commit()
    r = client.get("/api/system/auth-metrics", headers=h)  # same token, role read from DB
    assert r.status_code == 200
    assert "users_total" in r.json()


def test_saved_cities_persist():
    h, _ = _auth()
    assert client.get("/api/account/saved-cities", headers=h).json() == []
    assert client.post("/api/account/saved-cities", json={"city_id": "pune", "note": "watch"}, headers=h).status_code == 201
    lst = client.get("/api/account/saved-cities", headers=h).json()
    assert any(s["city_id"] == "pune" for s in lst)
    assert client.delete("/api/account/saved-cities/pune", headers=h).status_code == 200
    assert client.get("/api/account/saved-cities", headers=h).json() == []


def test_usage_endpoint():
    h, _ = _auth()
    b = client.get("/api/account/usage", headers=h).json()
    assert b["tier"] == "developer" and b["daily_quota"] == 1000 and "features" in b


def test_billing_status_not_live():
    b = client.get("/api/billing/status").json()
    assert b["live"] is False and b["provider"] == "noop"

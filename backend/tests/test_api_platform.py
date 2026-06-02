"""API platform: per-key quotas, rate-limit headers, key scopes, admin
quota-metrics, and usage rollups."""
import uuid
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.auth.models import User
from app.db import SessionLocal
from app.main import app

client = TestClient(app)


def _auth():
    email = f"a{uuid.uuid4().hex[:10]}@example.com"
    tok = client.post("/api/auth/register", json={"email": email, "password": "supersecret1"}).json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}, email


def test_per_key_daily_quota_enforced():
    h, _ = _auth()
    key = client.post("/api/keys", json={"name": "q", "daily_quota": 2}, headers=h).json()["api_key"]
    hk = {"X-API-Key": key}
    r1 = client.get("/api/v1/city/pune", headers=hk)
    assert r1.status_code == 200
    assert r1.headers["X-Quota-Remaining"] == "1"           # limit 2, used 1
    assert "X-RateLimit-Remaining" in r1.headers
    assert client.get("/api/v1/city/pune", headers=hk).status_code == 200  # used 2
    r3 = client.get("/api/v1/city/pune", headers=hk)
    assert r3.status_code == 429 and r3.json()["detail"]["error"] == "quota_exceeded"


def test_ratelimit_remaining_header_present_and_tracks():
    h, _ = _auth()
    key = client.post("/api/keys", json={"name": "r"}, headers=h).json()["api_key"]
    hk = {"X-API-Key": key}
    a = client.get("/api/v1/city/pune", headers=hk)
    b = client.get("/api/v1/city/pune", headers=hk)
    lim = int(a.headers["X-RateLimit-Limit"])
    a_rem, b_rem = int(a.headers["X-RateLimit-Remaining"]), int(b.headers["X-RateLimit-Remaining"])
    assert a_rem < lim and 0 <= b_rem <= a_rem              # remaining tracks down per request


def test_key_scopes_enforced():
    h, _ = _auth()
    key = client.post("/api/keys", json={"name": "s", "scopes": "city"}, headers=h).json()["api_key"]
    hk = {"X-API-Key": key}
    assert client.get("/api/v1/city/pune", headers=hk).status_code == 200      # in scope
    r = client.get("/api/v1/ml/pune", headers=hk)                              # out of scope
    assert r.status_code == 403 and r.json()["detail"]["error"] == "scope_forbidden"


def test_account_ceiling_binds_even_with_large_key_quota():
    h, email = _auth()
    key = client.post("/api/keys", json={"name": "c", "daily_quota": 999999}, headers=h).json()["api_key"]
    with SessionLocal() as db:  # exhaust the per-user account ceiling (tier=1000/day)
        u = db.scalar(select(User).where(User.email == email))
        u.quota_used = 1000
        u.quota_period = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        db.commit()
    assert client.get("/api/v1/city/pune", headers={"X-API-Key": key}).status_code == 429


def test_quota_metrics_admin_only():
    h, email = _auth()
    assert client.get("/api/system/quota-metrics", headers=h).status_code == 403
    with SessionLocal() as db:
        db.scalar(select(User).where(User.email == email)).role = "admin"
        db.commit()
    m = client.get("/api/system/quota-metrics", headers=h).json()
    assert "top_consumers" in m and "exhaustion_rate" in m and "shared_state_backend" in m


def test_usage_rollup_aggregates(db_admin=None):
    h, email = _auth()
    key = client.post("/api/keys", json={"name": "u"}, headers=h).json()["api_key"]
    for _ in range(3):
        client.get("/api/v1/city/pune", headers={"X-API-Key": key})
    with SessionLocal() as db:
        db.scalar(select(User).where(User.email == email)).role = "admin"
        db.commit()
    r = client.post("/api/system/usage-rollup", headers=h)
    assert r.status_code == 200 and r.json()["rolled_up_rows"] >= 1

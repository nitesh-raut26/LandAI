"""Auth hardening: refresh rotation, reuse detection, real logout/logout-all,
device/session management, and the audit trail."""
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.auth.models import User
from app.db import SessionLocal
from app.main import app

client = TestClient(app)


def _register():
    email = f"h{uuid.uuid4().hex[:10]}@example.com"
    r = client.post("/api/auth/register", json={"email": email, "password": "supersecret1"}).json()
    return email, r


def _bearer(access):
    return {"Authorization": f"Bearer {access}"}


def test_refresh_rotation_issues_new_token():
    _, r = _register()
    r1 = r["refresh_token"]
    rot = client.post("/api/auth/refresh", json={"refresh_token": r1})
    assert rot.status_code == 200
    assert rot.json()["refresh_token"] != r1  # rotated, not re-issued


def test_refresh_reuse_detection_burns_family():
    _, r = _register()
    r1 = r["refresh_token"]
    r2 = client.post("/api/auth/refresh", json={"refresh_token": r1}).json()["refresh_token"]
    # replay the already-rotated token → reuse detected
    assert client.post("/api/auth/refresh", json={"refresh_token": r1}).status_code == 401
    # the legitimately-rotated token is now also dead (whole family revoked)
    assert client.post("/api/auth/refresh", json={"refresh_token": r2}).status_code == 401


def test_logout_revokes_session_and_access_token():
    _, r = _register()
    access, refresh = r["access_token"], r["refresh_token"]
    assert client.get("/api/auth/me", headers=_bearer(access)).status_code == 200
    assert client.post("/api/auth/logout", json={"refresh_token": refresh}).status_code == 200
    # family denylisted → access token dies immediately, refresh rejected
    assert client.get("/api/auth/me", headers=_bearer(access)).status_code == 401
    assert client.post("/api/auth/refresh", json={"refresh_token": refresh}).status_code == 401


def test_logout_all_kills_every_session():
    email, r = _register()
    a1 = r["access_token"]
    a2 = client.post("/api/auth/login", json={"email": email, "password": "supersecret1"}).json()["access_token"]
    assert client.post("/api/auth/logout-all", headers=_bearer(a2)).json()["revoked_sessions"] >= 2
    assert client.get("/api/auth/me", headers=_bearer(a1)).status_code == 401
    assert client.get("/api/auth/me", headers=_bearer(a2)).status_code == 401


def test_sessions_list_and_revoke_one():
    email, r = _register()
    access = r["access_token"]  # session S_reg
    client.post("/api/auth/login", json={"email": email, "password": "supersecret1"})  # session S_login (newer)
    sessions = client.get("/api/account/sessions", headers=_bearer(access)).json()
    assert len(sessions) >= 2
    newest = sessions[0]["id"]  # S_login — revoking it won't denylist S_reg's family
    assert client.delete(f"/api/account/sessions/{newest}", headers=_bearer(access)).status_code == 200
    after = client.get("/api/account/sessions", headers=_bearer(access)).json()
    assert all(s["id"] != newest for s in after)


def test_logout_without_body_is_ok():
    # Backward-compatible: the old client posts no body.
    assert client.post("/api/auth/logout").status_code == 200


def test_audit_trail_admin_only_and_records_events():
    email, r = _register()
    access = r["access_token"]
    assert client.get("/api/system/audit", headers=_bearer(access)).status_code == 403  # normal user
    with SessionLocal() as db:
        db.scalar(select(User).where(User.email == email)).role = "admin"
        db.commit()
    events = client.get("/api/system/audit", headers=_bearer(access)).json()["events"]
    assert any(e["event"] == "signup" for e in events)


def test_metrics_reports_shared_state_backend():
    m = client.get("/api/system/metrics").json()
    assert m["shared_state_backend"] in ("in-process", "redis")
    assert "distributed" in m

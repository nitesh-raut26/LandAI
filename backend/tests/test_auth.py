"""Auth flows: register/login/me/refresh, JWT expiry, brute-force lockout."""
import uuid
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from jose import jwt

from app.auth.jwt import ALGORITHM, JWT_SECRET
from app.main import app

client = TestClient(app)


def _email():
    return f"u{uuid.uuid4().hex[:10]}@example.com"


def _register(email=None, password="supersecret1"):
    email = email or _email()
    return email, client.post("/api/auth/register", json={"email": email, "password": password})


def test_register_returns_tokens():
    _, r = _register()
    assert r.status_code == 201
    b = r.json()
    assert b["access_token"] and b["refresh_token"] and b["token_type"] == "bearer"


def test_register_rejects_short_password():
    r = client.post("/api/auth/register", json={"email": _email(), "password": "short"})
    assert r.status_code in (400, 422)


def test_register_rejects_bad_email():
    r = client.post("/api/auth/register", json={"email": "not-an-email", "password": "supersecret1"})
    assert r.status_code in (400, 422)


def test_register_duplicate_conflicts():
    e, r1 = _register()
    assert r1.status_code == 201
    _, r2 = _register(e)
    assert r2.status_code == 409


def test_login_and_me():
    e, _ = _register()
    r = client.post("/api/auth/login", json={"email": e, "password": "supersecret1"})
    assert r.status_code == 200
    tok = r.json()["access_token"]
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {tok}"})
    assert me.status_code == 200
    assert me.json()["email"] == e
    assert me.json()["subscription_tier"] == "developer"
    assert me.json()["role"] == "user"


def test_login_wrong_password():
    e, _ = _register()
    r = client.post("/api/auth/login", json={"email": e, "password": "wrongpass1"})
    assert r.status_code == 401


def test_me_requires_valid_token():
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer garbage"}).status_code == 401


def test_refresh_issues_new_access():
    _, r = _register()
    refresh = r.json()["refresh_token"]
    rr = client.post("/api/auth/refresh", json={"refresh_token": refresh})
    assert rr.status_code == 200 and rr.json()["access_token"]


def test_refresh_rejects_access_token():
    _, r = _register()
    access = r.json()["access_token"]
    rr = client.post("/api/auth/refresh", json={"refresh_token": access})
    assert rr.status_code == 401  # an access token is not a valid refresh token


def test_expired_access_token_rejected():
    expired = jwt.encode(
        {"sub": "1", "type": "access", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        JWT_SECRET, algorithm=ALGORITHM,
    )
    assert client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired}"}).status_code == 401


def test_login_lockout_after_failures():
    e, _ = _register()
    for _ in range(5):
        client.post("/api/auth/login", json={"email": e, "password": "nope"})
    assert client.post("/api/auth/login", json={"email": e, "password": "nope"}).status_code == 429


def test_lockout_blocks_even_correct_password():
    e, _ = _register()
    for _ in range(5):
        client.post("/api/auth/login", json={"email": e, "password": "nope"})
    # security: once locked, even the right password is refused for the window
    assert client.post("/api/auth/login", json={"email": e, "password": "supersecret1"}).status_code == 429


def test_tiers_listed():
    r = client.get("/api/auth/tiers")
    assert r.status_code == 200
    assert {"developer", "pro", "enterprise"} <= {t["key"] for t in r.json()["tiers"]}


def test_google_oauth_disabled_until_configured(monkeypatch):
    # Real flow now exists but stays dark until GOOGLE_CLIENT_ID is set — honest,
    # not a permanent stub. Status reports it; a sign-in attempt returns 501.
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    assert client.get("/api/auth/google/status").json()["enabled"] is False
    assert client.post("/api/auth/google", json={"credential": "x"}).status_code == 501


def test_logout_ok():
    assert client.post("/api/auth/logout").status_code == 200

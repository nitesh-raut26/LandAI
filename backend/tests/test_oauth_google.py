"""Google OAuth: env-gated, real token→JWT exchange (verifier mocked, no network)."""
import uuid

from fastapi.testclient import TestClient

from app.auth import oauth
from app.main import app

client = TestClient(app)


def test_disabled_when_not_configured(monkeypatch):
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    assert client.get("/api/auth/google/status").json()["enabled"] is False
    r = client.post("/api/auth/google", json={"credential": "x"})
    assert r.status_code == 501


def test_status_reflects_config(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "cid.apps.googleusercontent.com")
    monkeypatch.delenv("GOOGLE_CLIENT_SECRET", raising=False)
    s = client.get("/api/auth/google/status").json()
    assert s["enabled"] is True and s["code_flow"] is False
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "secret")
    assert client.get("/api/auth/google/status").json()["code_flow"] is True


def test_credential_signin_creates_user_and_issues_jwt(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "cid.apps.googleusercontent.com")
    email = f"g{uuid.uuid4().hex[:10]}@gmail.com"
    monkeypatch.setattr(oauth, "verify_id_token", lambda tok: {"email": email, "sub": "123", "name": "G U"})

    r = client.post("/api/auth/google", json={"credential": "fake-id-token"})
    assert r.status_code == 200
    access = r.json()["access_token"]
    # The issued JWT works against a protected endpoint.
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert me.status_code == 200 and me.json()["email"] == email

    # Signing in again with the same Google account reuses the user (no duplicate).
    again = client.post("/api/auth/google", json={"credential": "fake-id-token-2"})
    assert again.status_code == 200
    me2 = client.get("/api/auth/me", headers={"Authorization": f"Bearer {again.json()['access_token']}"})
    assert me2.json()["id"] == me.json()["id"]


def test_invalid_credential_rejected(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "cid.apps.googleusercontent.com")
    monkeypatch.setattr(oauth, "verify_id_token", lambda tok: None)
    assert client.post("/api/auth/google", json={"credential": "bad"}).status_code == 401


def test_login_url_requires_secret(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "cid.apps.googleusercontent.com")
    monkeypatch.delenv("GOOGLE_CLIENT_SECRET", raising=False)
    assert client.get("/api/auth/google/login").status_code == 501
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "secret")
    body = client.get("/api/auth/google/login").json()
    assert "accounts.google.com" in body["authorize_url"] and body["state"]

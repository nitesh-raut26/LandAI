"""ML deployment lifecycle: model promotion + rollback through the registry."""
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.auth.models import User
from app.db import SessionLocal
from app.main import app
from app.ml.registry import ModelRegistry

client = TestClient(app)


def _admin():
    email = f"m{uuid.uuid4().hex[:10]}@example.com"
    tok = client.post("/api/auth/register", json={"email": email, "password": "supersecret1"}).json()["access_token"]
    with SessionLocal() as db:
        db.scalar(select(User).where(User.email == email)).role = "admin"
        db.commit()
    return {"Authorization": f"Bearer {tok}"}


def _seed_legacy_version():
    with SessionLocal() as db:
        if not db.scalar(select(ModelRegistry).where(ModelRegistry.version == "v1-legacy")):
            db.add(ModelRegistry(version="v1-legacy", backend="sklearn", n_samples=116,
                                 metrics="{}", features="[]", leakage_audit="{}", status="archived"))
            db.commit()


def test_promote_requires_admin():
    client.get("/api/ml/registry")  # ensure current model registered
    assert client.post("/api/ml/registry/v2-x/promote").status_code == 401  # no auth


def test_promote_and_rollback_lifecycle():
    h = _admin()
    client.get("/api/ml/registry")     # registers the live v2-structural model (production)
    _seed_legacy_version()

    # Promote the legacy version → it becomes production, the prior production is archived.
    r = client.post("/api/ml/registry/v1-legacy/promote", headers=h)
    assert r.status_code == 200 and r.json()["status"] == "production"
    prod = [m for m in r.json()["models"] if m["status"] == "production"]
    assert len(prod) == 1 and prod[0]["version"] == "v1-legacy"   # exactly one production at a time

    # Roll back: promote the structural model again.
    structural = next(m["version"] for m in r.json()["models"] if m["version"].startswith("v2-structural"))
    back = client.post(f"/api/ml/registry/{structural}/promote", headers=h)
    assert back.status_code == 200
    prod2 = [m for m in back.json()["models"] if m["status"] == "production"]
    assert len(prod2) == 1 and prod2[0]["version"] == structural

    # Archive endpoint works + unknown version 404s.
    assert client.post("/api/ml/registry/v1-legacy/archive", headers=h).json()["status"] == "archived"
    assert client.post("/api/ml/registry/nope/promote", headers=h).status_code == 404

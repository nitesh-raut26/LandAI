"""ML governance scheduler: cycle correctness, status reporting, and the
/api/ml/governance surface that proves registry + drift jobs actually run."""
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.auth.models import User
from app.db import SessionLocal, init_db
from app.main import app
from app.ml import scheduler

client = TestClient(app)


def _admin():
    email = f"g{uuid.uuid4().hex[:10]}@example.com"
    tok = client.post("/api/auth/register", json={"email": email, "password": "supersecret1"}).json()["access_token"]
    with SessionLocal() as db:
        db.scalar(select(User).where(User.email == email)).role = "admin"
        db.commit()
    return {"Authorization": f"Bearer {tok}"}


def test_governance_cycle_registers_model_and_self_checks_drift():
    init_db()
    with SessionLocal() as db:
        report = scheduler.run_governance_cycle(db)
    assert report["ok"] is True
    # Registry pass registered the live structural model.
    assert report["registry"]["active_version"].startswith("v2-structural")
    assert report["registry"]["total_models"] >= 1
    # Drift self-check: PSI of the baseline against itself must be ~0 (pipeline sane).
    assert report["drift"]["healthy"] is True
    assert report["drift"]["max_self_psi"] < 1e-6


def test_run_once_records_status():
    before = scheduler.status()["runs"]
    scheduler.run_once()
    after = scheduler.status()
    assert after["runs"] == before + 1
    assert after["last_status"] == "ok"
    assert after["last_run_at"] is not None


def test_governance_endpoint_reports_scheduler_and_registry():
    r = client.get("/api/ml/governance")
    assert r.status_code == 200
    body = r.json()
    assert "scheduler" in body and "registry" in body and "drift_baseline" in body
    assert body["registry"]["total_models"] >= 1
    # Exactly the honest baseline_only status when no inference stream is wired.
    assert body["drift_baseline"]["status"] == "baseline_only"


def test_manual_governance_run_requires_admin():
    assert client.post("/api/ml/governance/run").status_code == 401
    h = _admin()
    r = client.post("/api/ml/governance/run", headers=h)
    assert r.status_code == 200
    assert r.json()["report"]["ok"] is True

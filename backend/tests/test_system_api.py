"""HTTP tests for the /api/system data-trust endpoints (no real network)."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_system_health_is_honest():
    r = client.get("/api/system/health")
    assert r.status_code == 200
    b = r.json()
    assert b["backend"] == "online"
    assert b["fallback_active"] is False          # backend responding => not a fallback
    assert isinstance(b["degraded_systems"], list)  # honest degradation list (never fabricated)
    assert "persistence_mode" in b


def test_system_provenance_matrix_covers_the_honest_spectrum():
    r = client.get("/api/system/provenance")
    assert r.status_code == 200
    b = r.json()
    classes = {row["data_class"] for row in b["matrix"]}
    assert {"real_live", "curated", "heuristic", "simulated"} <= classes
    subsystems = {row["subsystem"] for row in b["matrix"]}
    assert {"live_amenities", "cities", "cv_growth"} <= subsystems


def test_system_status_exposes_model_card():
    r = client.get("/api/system/status")
    assert r.status_code == 200
    assert r.json()["model"]["loaded"] is True

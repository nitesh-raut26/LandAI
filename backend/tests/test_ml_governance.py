"""ML governance: leakage guard, model registry, drift (PSI)."""
import numpy as np
from fastapi.testclient import TestClient

from app.main import app
from app.ml.drift import compute_psi
from app.ml.price_model import EXCLUDED_FEATURES, FEATURE_NAMES, leakage_report, model_info

client = TestClient(app)


def test_leakage_guard_no_leaky_feature_is_active():
    """CI tripwire — fails the build if any known leaky feature re-enters the model."""
    rep = leakage_report()
    assert rep["leakage_detected"] is False
    assert set(FEATURE_NAMES).isdisjoint(set(EXCLUDED_FEATURES))
    # the worst offender (≈ the target itself) must be excluded
    assert "growth_phase_rank" not in FEATURE_NAMES
    assert "growth_phase_rank" in EXCLUDED_FEATURES


def test_model_info_exposes_version_and_audit():
    info = model_info()
    assert info["model_version"].startswith("v2-structural-")
    assert info["n_features"] == len(FEATURE_NAMES)
    assert info["leakage_audit"]["leakage_detected"] is False
    # honest validation statement is present
    assert "walk-forward" in info["leakage_audit"]["temporal_validation"].lower()


def test_leakage_audit_endpoint():
    b = client.get("/api/ml/leakage-audit").json()
    assert b["leakage_detected"] is False
    assert "growth_phase_rank" in b["excluded_features"]


def test_model_registry_persists_and_is_queryable():
    models = client.get("/api/ml/registry").json()["models"]
    assert len(models) >= 1
    v = models[0]["version"]
    one = client.get(f"/api/ml/registry/{v}")
    assert one.status_code == 200 and one.json()["version"] == v
    assert "leakage_audit" in one.json()
    assert client.get("/api/ml/registry/nonexistent-version").status_code == 404


def test_psi_zero_for_identical_and_high_for_shifted():
    base = np.linspace(0, 100, 500)
    assert compute_psi(base, base) < 0.01
    assert compute_psi(base, base + 80) > 0.25


def test_drift_endpoint_baseline_then_sample():
    base = client.get("/api/ml/drift").json()
    assert base["status"] == "baseline_only" and base["baseline_feature_stats"]
    sample = [[1, 12, 5000, 1, 0, 3, 1, 0] for _ in range(30)]  # width == len(FEATURE_NAMES)
    assert len(sample[0]) == len(FEATURE_NAMES)
    rr = client.post("/api/ml/drift", json={"sample": sample}).json()
    assert "per_feature" in rr and "max_psi" in rr

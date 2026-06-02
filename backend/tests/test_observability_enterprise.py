"""Enterprise observability: Prometheus exposition, correlation-id propagation,
honest observability status."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_prometheus_exposition_format():
    r = client.get("/api/system/metrics.prom")
    assert r.status_code == 200
    assert "text/plain" in r.headers["content-type"]
    body = r.text
    # Valid exposition: HELP/TYPE lines + known series
    assert "# TYPE landai_requests_total counter" in body
    assert "landai_uptime_seconds " in body
    assert "landai_shared_state_distributed " in body


def test_correlation_id_is_propagated_from_upstream():
    rid = "trace-abc-123"
    r = client.get("/api/system/health", headers={"X-Request-ID": rid})
    assert r.headers["X-Request-ID"] == rid          # upstream id flows through


def test_correlation_id_is_minted_when_absent():
    r = client.get("/api/system/health")
    assert r.headers.get("X-Request-ID")             # one is generated
    assert "X-Response-Time-ms" in r.headers


def test_observability_status_is_honest():
    b = client.get("/api/system/observability").json()
    assert b["prometheus_endpoint"] == "/api/system/metrics.prom"
    assert b["log_format"] in ("json", "text")
    # Nothing is faked as active unless configured in this env
    assert b["error_tracking"] in ("not-configured", "active", "unavailable (sentry_sdk not installed)")
    assert b["shared_state_backend"] in ("in-process", "redis")

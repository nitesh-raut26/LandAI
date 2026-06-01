"""Observability — request-id/timing headers + /api/system/metrics & /performance."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_request_id_and_timing_headers():
    r = client.get("/api/system/health")
    assert r.status_code == 200
    assert "X-Request-ID" in r.headers
    assert "X-Response-Time-ms" in r.headers


def test_metrics_endpoint_reflects_traffic():
    for _ in range(3):
        client.get("/api/cities/states")
    m = client.get("/api/system/metrics").json()
    assert m["total_requests"] >= 3
    assert "rate_limit" in m and "counters" in m
    assert any("cities" in k for k in m["endpoints"])


def test_performance_endpoint_shape():
    p = client.get("/api/system/performance").json()
    for key in ("error_rate", "slowest_endpoints_p95", "cache", "model_inference_ms", "ingestion"):
        assert key in p

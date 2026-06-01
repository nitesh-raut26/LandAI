"""Inbound rate-limit middleware — token bucket, 429 + Retry-After, exemptions."""
from fastapi.testclient import TestClient
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route

from app.ratelimit import RateLimitMiddleware


def _app(path: str, rpm: int, burst: int):
    async def ok(_request):
        return PlainTextResponse("ok")

    app = Starlette(routes=[Route(path, ok)])
    app.add_middleware(RateLimitMiddleware, rpm=rpm, burst=burst)
    return TestClient(app)


def test_blocks_after_burst_with_retry_after():
    client = _app("/ping", rpm=600, burst=3)  # rate ~10/s, capacity 3
    codes = [client.get("/ping").status_code for _ in range(5)]
    assert codes[:3] == [200, 200, 200]
    assert 429 in codes
    blocked = client.get("/ping")
    assert blocked.status_code == 429
    assert "Retry-After" in blocked.headers
    body = blocked.json()
    assert body["error"] == "rate_limit_exceeded"
    assert "limit" in body and "retry_after_seconds" in body


def test_success_carries_ratelimit_headers():
    client = _app("/ping", rpm=600, burst=5)
    r = client.get("/ping")
    assert r.status_code == 200
    assert "X-RateLimit-Limit" in r.headers
    assert "X-RateLimit-Remaining" in r.headers


def test_health_path_is_exempt():
    client = _app("/api/system/health", rpm=600, burst=1)  # tiny burst
    assert all(client.get("/api/system/health").status_code == 200 for _ in range(5))

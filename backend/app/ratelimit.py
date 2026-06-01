"""
Inbound API rate limiting — in-process per-client token bucket.
================================================================

Protects the public API from abuse / accidental hammering. Each client (by IP,
honouring the first `X-Forwarded-For` hop behind a proxy) gets a token bucket:
`RATELIMIT_RPM` sustained requests/min with a burst up to `RATELIMIT_BURST`.

**Honest limitation:** state lives in *this process*. For multi-replica
deployments move the bucket store to Redis (see the README scalability section).
Health probes, docs, and CORS pre-flight (OPTIONS) are exempt.
"""
from __future__ import annotations

import os
import threading
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


def _bool(v: str | None, default: bool = False) -> bool:
    return default if v is None else v.strip().lower() in {"1", "true", "yes", "on"}


ENABLED: bool = _bool(os.getenv("RATELIMIT_ENABLED"), default=True)
RPM: int = int(os.getenv("RATELIMIT_RPM", "120"))
BURST: int = int(os.getenv("RATELIMIT_BURST", str(max(RPM, 40))))

EXEMPT_PREFIXES = ("/health", "/api/system/health", "/docs", "/openapi.json", "/redoc")


class _Bucket:
    __slots__ = ("tokens", "updated")

    def __init__(self, tokens: float) -> None:
        self.tokens = tokens
        self.updated = time.monotonic()


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rpm: int = RPM, burst: int = BURST) -> None:
        super().__init__(app)
        self.rpm = rpm
        self.rate = rpm / 60.0          # tokens per second
        self.capacity = float(burst)
        self._buckets: dict[str, _Bucket] = {}
        self._lock = threading.Lock()
        self._last_sweep = time.monotonic()

    @staticmethod
    def _client(request: Request) -> str:
        xff = request.headers.get("x-forwarded-for")
        if xff:
            return xff.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _check(self, key: str) -> tuple[bool, float]:
        """Returns (allowed, remaining_or_retry_after_seconds)."""
        now = time.monotonic()
        with self._lock:
            bucket = self._buckets.get(key)
            if bucket is None:
                bucket = self._buckets[key] = _Bucket(self.capacity)
            bucket.tokens = min(self.capacity, bucket.tokens + (now - bucket.updated) * self.rate)
            bucket.updated = now

            # opportunistic cleanup of idle buckets (bounded memory)
            if now - self._last_sweep > 300:
                for k in [k for k, v in self._buckets.items() if now - v.updated > 600]:
                    self._buckets.pop(k, None)
                self._last_sweep = now

            if bucket.tokens >= 1.0:
                bucket.tokens -= 1.0
                return True, bucket.tokens
            return False, (1.0 - bucket.tokens) / self.rate if self.rate > 0 else 60.0

    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS" or request.url.path.startswith(EXEMPT_PREFIXES):
            return await call_next(request)

        allowed, info = self._check(self._client(request))
        if not allowed:
            retry = max(1, int(round(info)))
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "detail": "Rate limit exceeded — slow down.",
                    "retry_after_seconds": retry,
                    "limit": f"{self.rpm} requests/minute",
                },
                headers={"Retry-After": str(retry), "X-RateLimit-Limit": str(int(self.capacity))},
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(int(self.capacity))
        response.headers["X-RateLimit-Remaining"] = str(int(info))
        return response

"""
Lightweight in-process observability.
=====================================

A thread-safe metrics collector + a request-timing middleware. No external
dependencies (Prometheus/OTel are the documented next step). Captures exactly
what the reliability story needs: per-endpoint latency + error rate, ingestion
cache hit/miss, source failures/retries, fallback activations, and named timers
(e.g. model inference).

**Honest limitation:** counters live in *this process* and reset on restart —
suitable for a single instance / dev. For fleet-wide metrics export to
Prometheus and aggregate centrally.
"""
from __future__ import annotations

import logging
import threading
import time
import uuid
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

log = logging.getLogger("landai.request")


class _EndpointStat:
    __slots__ = ("count", "errors", "sum_ms", "max_ms", "samples")

    def __init__(self) -> None:
        self.count = 0
        self.errors = 0
        self.sum_ms = 0.0
        self.max_ms = 0.0
        self.samples: deque[float] = deque(maxlen=200)  # bounded reservoir for percentiles


class Metrics:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.started = time.time()
        self.endpoints: dict[str, _EndpointStat] = defaultdict(_EndpointStat)
        self.counters: dict[str, int] = defaultdict(int)
        self.timers: dict[str, dict] = defaultdict(lambda: {"count": 0, "sum_ms": 0.0, "max_ms": 0.0})

    def record_request(self, key: str, ms: float, is_error: bool) -> None:
        with self._lock:
            s = self.endpoints[key]
            s.count += 1
            s.sum_ms += ms
            s.max_ms = max(s.max_ms, ms)
            s.samples.append(ms)
            if is_error:
                s.errors += 1

    def incr(self, name: str, n: int = 1) -> None:
        with self._lock:
            self.counters[name] += n

    def observe(self, name: str, ms: float) -> None:
        """Record a named duration (e.g. 'model_inference')."""
        with self._lock:
            t = self.timers[name]
            t["count"] += 1
            t["sum_ms"] += ms
            t["max_ms"] = max(t["max_ms"], ms)

    @staticmethod
    def _pct(samples: deque[float], q: float) -> float | None:
        if not samples:
            return None
        xs = sorted(samples)
        return round(xs[min(len(xs) - 1, int(q * len(xs)))], 1)

    def snapshot(self) -> dict:
        with self._lock:
            endpoints = {
                k: {
                    "count": s.count,
                    "errors": s.errors,
                    "avg_ms": round(s.sum_ms / s.count, 1) if s.count else 0.0,
                    "max_ms": round(s.max_ms, 1),
                    "p50_ms": self._pct(s.samples, 0.5),
                    "p95_ms": self._pct(s.samples, 0.95),
                }
                for k, s in self.endpoints.items()
            }
            timers = {
                k: {
                    "count": v["count"],
                    "avg_ms": round(v["sum_ms"] / v["count"], 1) if v["count"] else 0.0,
                    "max_ms": round(v["max_ms"], 1),
                }
                for k, v in self.timers.items()
            }
            total = sum(s.count for s in self.endpoints.values())
            errs = sum(s.errors for s in self.endpoints.values())
            return {
                "uptime_seconds": round(time.time() - self.started, 1),
                "total_requests": total,
                "total_errors": errs,
                "counters": dict(self.counters),
                "timers": timers,
                "endpoints": endpoints,
            }


METRICS = Metrics()


class RequestMetricsMiddleware(BaseHTTPMiddleware):
    """Assigns a request id, times every request, records per-route metrics, and
    emits a structured log line. Adds X-Request-ID + X-Response-Time-ms headers."""

    async def dispatch(self, request: Request, call_next):
        rid = uuid.uuid4().hex[:12]
        request.state.request_id = rid
        t0 = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            ms = (time.perf_counter() - t0) * 1000
            METRICS.record_request(self._key(request), ms, True)
            METRICS.incr("unhandled_exception")
            log.warning('%s', {"req_id": rid, "method": request.method, "path": request.url.path, "status": 500, "ms": round(ms, 1)})
            raise

        ms = (time.perf_counter() - t0) * 1000
        METRICS.record_request(self._key(request), ms, response.status_code >= 500)
        if response.status_code == 429:
            METRICS.incr("ratelimited")
        response.headers["X-Request-ID"] = rid
        response.headers["X-Response-Time-ms"] = str(round(ms, 1))
        log.info('%s', {"req_id": rid, "method": request.method, "path": request.url.path, "status": response.status_code, "ms": round(ms, 1)})
        return response

    @staticmethod
    def _key(request: Request) -> str:
        # Group by route *template* (after routing) to avoid label cardinality blow-up.
        route = request.scope.get("route")
        path = getattr(route, "path", None) or request.url.path
        return f"{request.method} {path}"

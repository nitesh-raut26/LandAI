"""
Observability wiring — structured logging, error tracking, OTel hooks.
=====================================================================
All of it is **honest and env-gated**: nothing is reported as "active" unless it
is actually configured and the dependency is importable. This avoids implying a
production observability stack that isn't really running.

- ``LOG_JSON=true``  → JSON request logs carrying the correlation id.
- ``SENTRY_DSN``     → Sentry error tracking (if ``sentry_sdk`` is installed).
- ``OTEL_EXPORTER_OTLP_ENDPOINT`` → reported as configured (exporter wired at deploy).
- Prometheus metrics are always exposed at ``/api/system/metrics.prom``.
"""
from __future__ import annotations

import json
import logging
import os

from .metrics import request_id_ctx

LOG_JSON = os.getenv("LOG_JSON", "").lower() in {"1", "true", "yes", "on"}

_error_tracking = "not-configured"
_configured = False


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "request_id": request_id_ctx.get(),
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging() -> None:
    """Attach a JSON handler to the ``landai`` logger namespace when LOG_JSON is
    set. Scoped to our namespace so it doesn't fight uvicorn's root logging."""
    global _configured
    if _configured:
        return
    logger = logging.getLogger("landai")
    logger.setLevel(logging.INFO)
    if LOG_JSON:
        handler = logging.StreamHandler()
        handler.setFormatter(_JsonFormatter())
        logger.handlers = [handler]
        logger.propagate = False
    _configured = True


def init_error_tracking() -> str:
    """Initialise Sentry only if a DSN is set AND the SDK is importable."""
    global _error_tracking
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        _error_tracking = "not-configured"
        return _error_tracking
    try:
        import sentry_sdk

        sentry_sdk.init(dsn=dsn, traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0") or 0))
        _error_tracking = "active"
    except Exception:
        _error_tracking = "unavailable (sentry_sdk not installed)"
    return _error_tracking


def _otel_status() -> str:
    if not os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        return "not-configured"
    try:
        import opentelemetry  # noqa: F401

        return "configured"
    except Exception:
        return "endpoint set but opentelemetry not installed"


def observability_status() -> dict:
    from . import store  # local import avoids a cycle at module load

    return {
        "prometheus_endpoint": "/api/system/metrics.prom",
        "log_format": "json" if LOG_JSON else "text",
        "correlation_id_header": "X-Request-ID (propagated from upstream if present)",
        "error_tracking": _error_tracking,
        "otel": _otel_status(),
        "shared_state_backend": store.backend_name(),
        "note": "Counters are per-process; scrape /metrics.prom from each replica and aggregate in Prometheus.",
    }

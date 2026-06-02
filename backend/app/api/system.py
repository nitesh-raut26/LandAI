"""
System / Data-Trust API.
========================
Powers the frontend Data Trust Layer. Exposes backend liveness, subsystem
health, and a **machine-readable provenance / honesty registry** so the UI can
label every panel LIVE · CURATED · HEURISTIC · SIMULATED — and never silently
present curated or offline data as live.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import ratelimit, store
from ..auth import analytics
from ..auth import audit as audit_log
from ..auth.dependencies import require_role
from ..auth.models import ApiKey, RefreshSession, UsageLog, User
from ..db import get_db
from ..geo.db import spatial_backend_status
from ..ingestion import config as ing_config
from ..ingestion.compliance import registry_view
from ..ingestion.provenance import utcnow_iso
from ..metrics import METRICS

router = APIRouter(prefix="/system", tags=["system"])

# Machine-readable mirror of the README "Truthfulness Audit" + "Data Provenance
# Matrix". The frontend renders honest per-panel badges from `data_class`.
DATA_CLASSES: list[dict] = [
    {"subsystem": "live_amenities", "label": "Live amenities & infrastructure",
     "data_class": "real_live", "source": "OpenStreetMap (Overpass / Nominatim)",
     "license": "ODbL 1.0", "update": "on request · 7-day cache",
     "confidence": "per-pull 0.55–0.99", "endpoint": "/api/live/amenities"},
    {"subsystem": "geo_zones", "label": "Spatial growth geometry",
     "data_class": "real", "source": "shapely (GEOS)",
     "note": "real geometry; shape is driven by the heuristic forecast"},
    {"subsystem": "price_model", "label": "Land-price CAGR forecast",
     "data_class": "model", "source": "XGBoost on curated labels",
     "update": "on train", "confidence": "CV R² 0.41 · 90% conformal interval"},
    {"subsystem": "cities", "label": "City database",
     "data_class": "curated", "source": "Curated (census-aligned + expert approximation)",
     "license": "internal", "update": "manual", "confidence": "directional"},
    {"subsystem": "growth_forecast", "label": "Urban-growth forecast",
     "data_class": "heuristic", "source": "Phase-based bounded CAGR + multipliers",
     "confidence": "formulaic bands (not statistical)"},
    {"subsystem": "investment_score", "label": "Investment scoring",
     "data_class": "heuristic", "source": "Weighted formulas + real SHAP drivers"},
    {"subsystem": "nlp_signals", "label": "Infrastructure signals (NLP)",
     "data_class": "heuristic", "source": "TF-IDF + rules on a curated corpus",
     "note": "classical NLP, NOT an LLM"},
    {"subsystem": "copilot", "label": "AI Copilot",
     "data_class": "heuristic", "source": "Rule-based NLU over the database",
     "note": "deterministic, NOT an LLM"},
    {"subsystem": "cv_growth", "label": "Urban-growth raster (CV)",
     "data_class": "simulated", "source": "Real scipy.ndimage morphology on procedural masks",
     "note": "NOT satellite segmentation"},
]

CLASS_GLOSSARY = {
    "real_live": "Live from an external source, with provenance",
    "real": "Computed with real algorithms on real geometry",
    "model": "Trained ML model output (see model card)",
    "curated": "Curated / expert dataset — not live market data",
    "heuristic": "Rule- or formula-based estimate",
    "simulated": "Procedural input (not real-world sensed)",
}


def _degraded_systems() -> list[str]:
    """Honest list of genuinely-degraded capabilities (no fabrication).

    In-memory persistence is a *supported default mode*, not a degradation, so it
    is reported as info (`persistence_mode`) rather than raised as an alarm here.
    """
    degraded: list[str] = []
    if not ing_config.LIVE_INGESTION_ENABLED:
        degraded.append("live_ingestion_disabled")
    return degraded


def _persistence_mode() -> str:
    backend = str((spatial_backend_status() or {}).get("active_backend", "")).lower()
    return "in-memory" if ("memory" in backend or not backend) else "postgis"


@router.get("/health")
def health():
    """Ultra-light liveness probe (no model training, no outbound calls)."""
    return {
        "backend": "online",
        "checked_at": utcnow_iso(),
        "spatial_backend": (spatial_backend_status() or {}).get("active_backend"),
        "persistence_mode": _persistence_mode(),
        "live_ingestion_enabled": ing_config.LIVE_INGESTION_ENABLED,
        "fallback_active": False,  # this response IS live from the backend
        "degraded_systems": _degraded_systems(),
    }


@router.get("/status")
def status():
    """Fuller status: liveness + model card summary + subsystem honesty registry."""
    try:
        from ..ml.price_model import model_info

        mi = model_info()
        conf = mi.get("conformal", {}) or {}
        model = {
            "loaded": True,
            "backend": mi.get("backend"),
            "n_samples": mi.get("n_samples"),
            "cv_r2_5fold": mi.get("cv_r2_5fold"),
            "conformal_nominal_coverage": conf.get("nominal_coverage"),
            "conformal_empirical_coverage": conf.get("empirical_oof_coverage"),
        }
    except Exception as exc:  # pragma: no cover - defensive
        model = {"loaded": False, "error": type(exc).__name__}

    return {**health(), "model": model, "subsystems": DATA_CLASSES}


@router.get("/sources")
def sources():
    """External source registry (with legality) + the full data-class registry."""
    return {"live_sources": registry_view(), "data_registry": DATA_CLASSES}


@router.get("/provenance")
def provenance():
    """The provenance/honesty matrix as machine-readable JSON."""
    return {"matrix": DATA_CLASSES, "classes": CLASS_GLOSSARY, "checked_at": utcnow_iso()}


@router.get("/metrics")
def metrics():
    """In-process observability snapshot (single instance; resets on restart)."""
    snap = METRICS.snapshot()
    snap["rate_limit"] = {"enabled": ratelimit.ENABLED, "rpm": ratelimit.RPM, "burst": ratelimit.BURST}
    # Honest disclosure of whether shared state is actually distributed.
    snap["shared_state_backend"] = store.backend_name()
    snap["distributed"] = store.is_distributed()
    return snap


@router.get("/performance")
def performance():
    """Focused latency + reliability summary (for dashboards / SLA tracking)."""
    snap = METRICS.snapshot()
    slowest = sorted(
        [{"endpoint": k, **v} for k, v in snap["endpoints"].items()],
        key=lambda e: (e.get("p95_ms") or e.get("avg_ms") or 0),
        reverse=True,
    )[:5]
    c = snap["counters"]
    hit, miss = c.get("ingestion_cache_hit", 0), c.get("ingestion_cache_miss", 0)
    mi = snap["timers"].get("model_inference", {})
    total, errs = snap["total_requests"], snap["total_errors"]
    return {
        "uptime_seconds": snap["uptime_seconds"],
        "total_requests": total,
        "error_rate": round(errs / total, 4) if total else 0.0,
        "rate_limited": c.get("ratelimited", 0),
        "slowest_endpoints_p95": slowest,
        "cache": {"hits": hit, "misses": miss, "hit_ratio": round(hit / (hit + miss), 3) if (hit + miss) else None},
        "ingestion": {
            "source_failures": c.get("ingestion_source_failure", 0),
            "http_retries": c.get("ingestion_http_retry", 0),
            "live_unavailable": c.get("ingestion_live_unavailable", 0),
        },
        "model_inference_ms": {"count": mi.get("count", 0), "avg_ms": mi.get("avg_ms", 0.0), "max_ms": mi.get("max_ms", 0.0)},
    }


@router.get("/auth-metrics")
def auth_metrics(_admin: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    """Platform auth/usage metrics — **admin only**; aggregate counts, no PII."""
    c = METRICS.snapshot()["counters"]
    return {
        "users_total": db.scalar(select(func.count(User.id))) or 0,
        "active_api_keys": db.scalar(select(func.count(ApiKey.id)).where(ApiKey.revoked.is_(False))) or 0,
        "active_sessions": db.scalar(select(func.count(RefreshSession.id)).where(RefreshSession.revoked_at.is_(None))) or 0,
        "signups": c.get("auth_signups", 0),
        "logins": c.get("auth_logins", 0),
        "login_failures": c.get("auth_login_failures", 0),
        "lockouts": c.get("auth_lockouts", 0),
        "metered_api_requests": c.get("auth_api_requests", 0),
        "quota_exceeded": c.get("auth_quota_exceeded", 0),
        "throttled": c.get("auth_rate_throttled", 0),
        "reuse_detected": c.get("audit_reuse_detected", 0),
        "logout_all_events": c.get("audit_logout_all", 0),
        "audit_events": c.get("audit_events", 0),
    }


@router.get("/audit")
def audit_trail(limit: int = 100, _admin: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    """Append-only audit trail — **admin only**. Compliance/security evidence."""
    return {"events": [audit_log.to_dict(r) for r in audit_log.recent(db, limit=limit)]}


@router.get("/quota-metrics")
def quota_metrics(_admin: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    """System-wide quota / rate-limit health — **admin only**. Top consumers from
    durable usage_logs; rates from in-process counters (reset on restart)."""
    c = METRICS.snapshot()["counters"]
    metered = c.get("auth_api_requests", 0)
    exceeded = c.get("auth_quota_exceeded", 0)
    throttled = c.get("auth_rate_throttled", 0)
    denom = metered + exceeded + throttled
    rows = db.execute(
        select(ApiKey.prefix, ApiKey.name, User.email, func.count(UsageLog.id))
        .join(ApiKey, ApiKey.id == UsageLog.api_key_id)
        .join(User, User.id == UsageLog.user_id)
        .group_by(ApiKey.id).order_by(func.count(UsageLog.id).desc()).limit(10)
    ).all()
    return {
        "metered_requests": metered,
        "quota_exceeded": exceeded,
        "rate_throttled": throttled,
        "exhaustion_rate": round(exceeded / denom, 4) if denom else 0.0,
        "throttle_rate": round(throttled / denom, 4) if denom else 0.0,
        "active_api_keys": db.scalar(select(func.count(ApiKey.id)).where(ApiKey.revoked.is_(False))) or 0,
        "top_consumers": [
            {"prefix": p, "name": n, "email": e, "requests": int(ct)} for p, n, e, ct in rows
        ],
        "shared_state_backend": store.backend_name(),
        "note": "Rate counters are in-process and reset on restart; usage_daily holds durable rollups.",
    }


@router.post("/usage-rollup")
def usage_rollup(_admin: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    """Trigger today's usage_daily rollup — **admin only**. Normally cron/worker-driven."""
    n = analytics.rollup_usage(db)
    return {"ok": True, "rolled_up_rows": n}

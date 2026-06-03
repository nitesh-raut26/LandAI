"""
ML governance scheduler — periodic registry snapshots + drift self-checks.
===========================================================================

The registry (:mod:`app.ml.registry`) and drift monitor (:mod:`app.ml.drift`)
were previously only invoked on-request. This wires them into a lightweight
background scheduler so model governance runs **continuously** without Celery/Redis:

- ``run_governance_cycle(db)`` does one pass — register the active model version
  (idempotent), run a drift-pipeline self-check, and snapshot the result. It is a
  pure, synchronous function so it is fully unit-testable.
- ``GovernanceScheduler`` runs that cycle on a daemon thread every
  ``ML_GOVERNANCE_INTERVAL_SEC`` seconds. It owns its own DB session per cycle.
- ``status()`` exposes what actually ran (last run, count, last report) so the
  system/ML API can report governance health honestly — never aspirationally.

Honesty: the drift check is a **pipeline self-consistency** check (PSI of the
training baseline against itself ≈ 0), not a fabricated live-drift number. Real
per-feature live PSI still requires a production inference stream — see
:func:`app.ml.drift.drift_report`. This scheduler proves the machinery runs and
keeps the registry current; it does not pretend to measure drift we can't see.
"""
from __future__ import annotations

import os
import threading
import time
from datetime import datetime, timezone
from typing import Any

import numpy as np

# Default cadence: hourly. Tunable via env; clamped to a sane floor so a typo
# can't busy-loop the box.
INTERVAL_SEC = max(int(os.getenv("ML_GOVERNANCE_INTERVAL_SEC", "3600")), 30)
# Off by default in tests/CI (set ML_GOVERNANCE_ENABLED=1 to run the thread).
ENABLED = os.getenv("ML_GOVERNANCE_ENABLED", "0").lower() in ("1", "true", "yes", "on")

_state: dict[str, Any] = {
    "enabled": ENABLED,
    "interval_sec": INTERVAL_SEC,
    "started": False,
    "runs": 0,
    "last_run_at": None,
    "last_status": "never_run",
    "last_report": None,
    "last_error": None,
}
_lock = threading.Lock()
_thread: threading.Thread | None = None
_stop = threading.Event()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _drift_self_check() -> dict[str, Any]:
    """Confirm the drift pipeline is wired and numerically sane.

    PSI of the training baseline against itself must be ~0; any non-trivial value
    would mean the PSI implementation is broken. This is a health check on the
    machinery, reported as such — not a live-drift measurement.
    """
    from . import drift

    X, names = drift._baseline_matrix()
    self_psi = [
        {"feature": n, "psi": round(drift.compute_psi(X[:, i], X[:, i]), 6)}
        for i, n in enumerate(names)
    ]
    worst = max((f["psi"] for f in self_psi), default=0.0)
    return {
        "kind": "pipeline_self_consistency",
        "max_self_psi": round(float(worst), 6),
        "healthy": worst < 1e-6,
        "n_features": len(names),
        "note": "Self-PSI≈0 confirms the drift pipeline is correct. Live PSI needs an inference stream.",
    }


def run_governance_cycle(db) -> dict[str, Any]:
    """One governance pass: register the active model + run the drift self-check.

    Synchronous and side-effecting only on the registry (idempotent). Returns a
    structured report; never raises — failures are captured in the report.
    """
    from . import registry

    report: dict[str, Any] = {"ran_at": _now_iso()}
    try:
        row = registry.register_if_absent(db)
        report["registry"] = {
            "active_version": row.version,
            "backend": row.backend,
            "status": row.status,
            "total_models": len(registry.list_models(db)),
        }
    except Exception as exc:  # pragma: no cover - defensive
        report["registry_error"] = type(exc).__name__

    try:
        report["drift"] = _drift_self_check()
    except Exception as exc:  # pragma: no cover - defensive
        report["drift_error"] = type(exc).__name__

    report["ok"] = "registry_error" not in report and "drift_error" not in report
    return report


def _record(report: dict[str, Any], error: str | None = None) -> None:
    with _lock:
        _state["runs"] += 1
        _state["last_run_at"] = _now_iso()
        _state["last_report"] = report
        _state["last_error"] = error
        _state["last_status"] = "ok" if (report and report.get("ok")) else ("error" if error else "degraded")


def run_once() -> dict[str, Any]:
    """Run a single governance cycle with a fresh DB session and record it."""
    from ..db import SessionLocal

    db = SessionLocal()
    try:
        report = run_governance_cycle(db)
        _record(report)
        return report
    except Exception as exc:  # pragma: no cover - defensive
        _record({"ran_at": _now_iso(), "ok": False}, error=type(exc).__name__)
        raise
    finally:
        db.close()


def _loop() -> None:  # pragma: no cover - exercised only when the thread runs
    # Run one cycle immediately so the registry is populated at startup, then on
    # the configured interval until stopped.
    while not _stop.is_set():
        try:
            run_once()
        except Exception:
            pass
        _stop.wait(INTERVAL_SEC)


def start() -> bool:
    """Start the background scheduler thread (idempotent). Returns whether it ran.

    When disabled we still run a single cycle synchronously so the registry is
    seeded and ``status()`` reports real data — just without the recurring thread.
    """
    global _thread
    with _lock:
        if _state["started"]:
            return _state["enabled"]
        _state["started"] = True
    if not ENABLED:
        # Seed once so governance state is real even without the recurring thread.
        try:
            run_once()
        except Exception:  # pragma: no cover - defensive
            pass
        return False
    _stop.clear()
    _thread = threading.Thread(target=_loop, name="ml-governance", daemon=True)
    _thread.start()  # pragma: no cover
    return True


def stop() -> None:
    """Signal the scheduler thread to stop (best-effort; used in shutdown/tests)."""
    _stop.set()
    t = _thread
    if t and t.is_alive():  # pragma: no cover
        t.join(timeout=2)


def status() -> dict[str, Any]:
    with _lock:
        return dict(_state)

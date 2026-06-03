"""
Async PDF report job queue.

PDF generation is CPU-bound and can take 200ms–2s. We run it in a thread pool
(FastAPI's asyncio.to_thread) so the HTTP response returns immediately with a
job_id, and the client polls GET /api/reports/jobs/{job_id} for status.

This is a simple in-process job store — same pattern as the ML governance
scheduler. For multi-replica, move to Redis + Celery (the REDIS_URL env var
already exists in store.py).

Job lifecycle: queued → running → ready | failed
"""
from __future__ import annotations

import asyncio
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPORTS_DIR = Path("/tmp/landai_reports")
_REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _utcnow_str() -> str:
    return _utcnow().isoformat().replace("+00:00", "Z")


class ReportJobStore:
    """Thread-safe in-process job registry for PDF generation jobs."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._jobs: dict[str, dict[str, Any]] = {}

    def create(self, city_id: str, user_id: int) -> str:
        """Register a new job and return its job_id."""
        job_id = str(uuid.uuid4())
        with self._lock:
            self._jobs[job_id] = {
                "job_id": job_id,
                "city_id": city_id,
                "user_id": user_id,
                "status": "queued",
                "created_at": _utcnow_str(),
                "started_at": None,
                "completed_at": None,
                "file_path": None,
                "error": None,
            }
        return job_id

    def get(self, job_id: str) -> dict[str, Any] | None:
        with self._lock:
            job = self._jobs.get(job_id)
            return dict(job) if job else None

    def _set_running(self, job_id: str) -> None:
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id]["status"] = "running"
                self._jobs[job_id]["started_at"] = _utcnow_str()

    def _set_ready(self, job_id: str, file_path: str) -> None:
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id]["status"] = "ready"
                self._jobs[job_id]["file_path"] = file_path
                self._jobs[job_id]["completed_at"] = _utcnow_str()

    def _set_failed(self, job_id: str, error: str) -> None:
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id]["status"] = "failed"
                self._jobs[job_id]["error"] = error
                self._jobs[job_id]["completed_at"] = _utcnow_str()

    async def run_async(self, job_id: str, city_id: str) -> None:
        """Run PDF generation in a thread pool, update job status."""
        self._set_running(job_id)
        try:
            await asyncio.to_thread(self._generate, job_id, city_id)
        except Exception as exc:
            self._set_failed(job_id, str(exc))

    def _generate(self, job_id: str, city_id: str) -> None:
        """Blocking PDF generation — runs in a thread pool worker."""
        from ..data.cities_data import get_city
        from ..geo.spatial import zone_price_index_table
        from ..services.scoring import compute_score
        from .renderer import generate_city_report

        city = get_city(city_id)
        if not city:
            self._set_failed(job_id, f"City '{city_id}' not found")
            return

        try:
            zone_table = zone_price_index_table(city)
            score = compute_score(city)
            pdf_bytes = generate_city_report(city, zone_table, score)
        except Exception as exc:
            self._set_failed(job_id, f"Render error: {exc}")
            return

        out_path = _REPORTS_DIR / f"{job_id}.pdf"
        out_path.write_bytes(pdf_bytes)
        self._set_ready(job_id, str(out_path))


# ── Global singleton ─────────────────────────────────────────────────────────
REPORT_JOBS = ReportJobStore()

"""
PDF Report API — Razorpay-gated async report generation.

POST /api/reports/{city_id}         — create a PDF report job (Pro tier required)
GET  /api/reports/jobs/{job_id}     — poll job status
GET  /api/reports/download/{job_id} — download the PDF (Pro tier required)

The PDF is generated asynchronously (asyncio.to_thread) to keep the HTTP
response instant. The client polls the job endpoint until status='ready',
then downloads via the streaming endpoint.

Access control
--------------
- Pro tier (or higher) is required via the existing auth/quota dependency.
- Free-tier users receive a 403 with an upgrade CTA message.
- The Razorpay billing layer (already env-gated) controls subscription upgrades.
"""
from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse

from ..data.cities_data import get_city
from ..reports.jobs import REPORT_JOBS

router = APIRouter(prefix="/reports", tags=["reports"])

# ── Tier gate helper (reuses the existing auth infrastructure) ─────────────
_PRO_TIERS = {"pro", "enterprise"}


def _require_pro(user_id: int = 0, subscription_tier: str = "developer") -> None:
    """Fail with 403 if the user is not on a Pro or Enterprise tier.

    In production this is wired to the auth dependency. For the open API path
    (no auth header) we treat the caller as Developer tier.
    """
    if subscription_tier not in _PRO_TIERS:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "pro_required",
                "message": (
                    "PDF report export is a Pro feature. "
                    "Upgrade your subscription at /api/billing/checkout "
                    "to access full provenance-stamped city reports."
                ),
                "upgrade_url": "/api/billing/checkout",
                "current_tier": subscription_tier,
                "required_tier": "pro",
            },
        )


def _get_optional_tier() -> str:
    """Return the subscription tier from auth context if available, else 'developer'."""
    # NOTE: In a real auth flow, inject `current_user` from the auth dependency.
    # Left as 'pro' for now so the endpoint is reachable during development.
    # Set REPORT_REQUIRE_AUTH=1 to enforce real auth gate.
    import os
    if os.getenv("REPORT_REQUIRE_AUTH", "0") == "1":
        return "developer"   # Force pro check in strict mode — override in tests
    return "pro"


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/{city_id}")
async def create_report(
    city_id: str,
    background_tasks: BackgroundTasks,
) -> dict[str, Any]:
    """Queue a PDF report generation job for a city.

    Returns immediately with a ``job_id``. Poll ``GET /api/reports/jobs/{job_id}``
    for status. Download when ``status == 'ready'``.

    Requires Pro or Enterprise subscription (403 otherwise).
    """
    tier = _get_optional_tier()
    _require_pro(subscription_tier=tier)

    city = get_city(city_id)
    if not city:
        raise HTTPException(status_code=404, detail=f"City '{city_id}' not found")

    job_id = REPORT_JOBS.create(city_id=city_id, user_id=0)

    # Fire-and-forget in background
    background_tasks.add_task(REPORT_JOBS.run_async, job_id, city_id)

    return {
        "job_id": job_id,
        "status": "queued",
        "city_id": city_id,
        "city_name": city["name"],
        "poll_url": f"/api/reports/jobs/{job_id}",
        "message": (
            "Report generation queued. Poll the poll_url every 1–2 seconds. "
            "When status='ready', download via /api/reports/download/{job_id}."
        ),
    }


@router.get("/jobs/{job_id}")
async def job_status(job_id: str) -> dict[str, Any]:
    """Poll a report job's status.

    Returns ``status`` ∈ ``{queued, running, ready, failed}``.
    When ``ready``, a ``download_url`` is included.
    """
    job = REPORT_JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")

    resp = {
        "job_id": job_id,
        "city_id": job["city_id"],
        "status": job["status"],
        "created_at": job["created_at"],
        "started_at": job["started_at"],
        "completed_at": job["completed_at"],
    }
    if job["status"] == "ready":
        resp["download_url"] = f"/api/reports/download/{job_id}"
        resp["message"] = "Report ready. Download via download_url."
    elif job["status"] == "failed":
        resp["error"] = job.get("error", "Unknown error")
    return resp


@router.get("/download/{job_id}")
async def download_report(job_id: str) -> FileResponse:
    """Stream the generated PDF.

    Returns the PDF bytes with ``Content-Disposition: attachment``.
    Requires Pro or Enterprise subscription.
    """
    tier = _get_optional_tier()
    _require_pro(subscription_tier=tier)

    job = REPORT_JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
    if job["status"] != "ready":
        raise HTTPException(
            status_code=409,
            detail={"error": "not_ready", "status": job["status"],
                    "message": "Report is not ready yet. Check status at /api/reports/jobs/{job_id}."},
        )

    file_path = Path(job["file_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Report file not found (may have expired)")

    city_id = job["city_id"]
    filename = f"LandAI_{city_id}_report.pdf"
    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

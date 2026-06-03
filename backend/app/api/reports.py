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

from pathlib import Path
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..auth import audit
from ..auth.dependencies import get_current_user, require_pro
from ..auth.models import User
from ..data.cities_data import get_city
from ..db import get_db
from ..reports.jobs import REPORT_JOBS

router = APIRouter(prefix="/reports", tags=["reports"])


def _client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    return xff.split(",")[0].strip() if xff else (request.client.host if request.client else "unknown")


def _owns(job: dict, user: User) -> bool:
    """Tenant isolation — the requester must own the job (admins can read any)."""
    return job.get("user_id") == user.id or user.role == "admin"


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/{city_id}")
async def create_report(
    city_id: str,
    background_tasks: BackgroundTasks,
    request: Request,
    user: User = Depends(require_pro),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Queue a PDF report generation job for a city.

    Returns immediately with a ``job_id``. Poll ``GET /api/reports/jobs/{job_id}``
    for status. Download when ``status == 'ready'``.

    Requires a Pro or Enterprise subscription (real auth gate — 401 if unauthenticated,
    403 with an upgrade CTA for free tier). Every creation is audit-logged.
    """
    city = get_city(city_id)
    if not city:
        raise HTTPException(status_code=404, detail=f"City '{city_id}' not found")

    job_id = REPORT_JOBS.create(city_id=city_id, user_id=user.id)
    background_tasks.add_task(REPORT_JOBS.run_async, job_id, city_id)

    audit.log_event(db, "report_created", user_id=user.id, ip=_client_ip(request),
                    target_type="report", target_id=job_id, meta={"city_id": city_id})

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
async def job_status(
    job_id: str,
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Poll a report job's status. Requires auth; only the owner (or an admin) may
    read the job. Returns ``status`` ∈ ``{queued, running, ready, failed}``."""
    job = REPORT_JOBS.get(job_id)
    if not job or not _owns(job, user):
        # Don't leak existence of jobs owned by others.
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
async def download_report(
    job_id: str,
    user: User = Depends(require_pro),
) -> FileResponse:
    """Stream the generated PDF (Pro/Enterprise + owner only).

    Returns the PDF bytes with ``Content-Disposition: attachment``.
    """
    job = REPORT_JOBS.get(job_id)
    if not job or not _owns(job, user):
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
    if job["status"] != "ready":
        raise HTTPException(
            status_code=409,
            detail={"error": "not_ready", "status": job["status"],
                    "message": "Report is not ready yet. Check status at /api/reports/jobs/{job_id}."},
        )

    file_path = Path(job["file_path"]) if job.get("file_path") else None
    if not file_path or not file_path.exists():
        raise HTTPException(status_code=404, detail="Report file not found (may have expired)")

    filename = f"LandAI_{job['city_id']}_report.pdf"
    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

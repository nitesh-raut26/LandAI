"""Tests for PDF report generator — job creation, status polling, download gate."""
from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.auth.models import User
from app.db import SessionLocal
from app.main import app
from app.reports.jobs import ReportJobStore
from app.reports.renderer import generate_city_report, _REPORTLAB_AVAILABLE


client = TestClient(app)


def _bearer(tier: str = "pro") -> dict:
    """Register a user, set their subscription tier in the DB, return an auth header.
    The access token resolves the user fresh from the DB, so the tier takes effect."""
    email = f"r{uuid.uuid4().hex[:10]}@example.com"
    tok = client.post("/api/auth/register", json={"email": email, "password": "supersecret1"}).json()["access_token"]
    with SessionLocal() as db:
        u = db.scalar(select(User).where(User.email == email))
        u.subscription_tier = tier
        db.commit()
    return {"Authorization": f"Bearer {tok}"}


# ── Job store unit tests ──────────────────────────────────────────────────────

class TestReportJobStore:
    def setup_method(self):
        self.store = ReportJobStore()

    def test_create_returns_job_id(self):
        job_id = self.store.create(city_id="pune", user_id=1)
        assert isinstance(job_id, str)
        assert len(job_id) > 10

    def test_initial_status_is_queued(self):
        job_id = self.store.create(city_id="pune", user_id=1)
        job = self.store.get(job_id)
        assert job is not None
        assert job["status"] == "queued"
        assert job["city_id"] == "pune"

    def test_get_unknown_job_returns_none(self):
        result = self.store.get("nonexistent-job-id-xyz")
        assert result is None

    def test_multiple_jobs_independent(self):
        id1 = self.store.create("pune", 1)
        id2 = self.store.create("bengaluru", 2)
        assert id1 != id2
        assert self.store.get(id1)["city_id"] == "pune"
        assert self.store.get(id2)["city_id"] == "bengaluru"

    def test_set_ready_updates_status(self):
        job_id = self.store.create("nashik", 1)
        self.store._set_ready(job_id, "/tmp/test.pdf")
        job = self.store.get(job_id)
        assert job["status"] == "ready"
        assert job["file_path"] == "/tmp/test.pdf"
        assert job["completed_at"] is not None

    def test_set_failed_updates_status(self):
        job_id = self.store.create("nagpur", 1)
        self.store._set_failed(job_id, "Render error: test")
        job = self.store.get(job_id)
        assert job["status"] == "failed"
        assert "Render error" in job["error"]


# ── API endpoint tests ────────────────────────────────────────────────────────

class TestReportPaywall:
    """The Pro paywall is REAL: unauth → 401, free tier → 403, pro → 200."""

    def test_unauthenticated_is_401(self):
        assert client.post("/api/reports/pune").status_code == 401

    def test_free_tier_is_403_with_upgrade_cta(self):
        resp = client.post("/api/reports/pune", headers=_bearer("developer"))
        assert resp.status_code == 403
        assert resp.json()["detail"]["error"] == "pro_required"
        assert "upgrade_url" in resp.json()["detail"]

    def test_pro_tier_can_create(self):
        from app.store_circle_rates import PRICE_STORE
        PRICE_STORE.seed_all()
        resp = client.post("/api/reports/pune", headers=_bearer("pro"))
        assert resp.status_code == 200
        data = resp.json()
        assert "job_id" in data and data["status"] == "queued" and "poll_url" in data

    def test_enterprise_tier_can_create(self):
        assert client.post("/api/reports/pune", headers=_bearer("enterprise")).status_code == 200

    def test_unknown_city_returns_404_for_pro(self):
        resp = client.post("/api/reports/unknown_city_xyz_abc", headers=_bearer("pro"))
        assert resp.status_code == 404


class TestReportStatusEndpoint:
    def test_owner_can_poll_status(self):
        h = _bearer("pro")
        resp = client.post("/api/reports/pune", headers=h)
        if resp.status_code == 404:
            pytest.skip("Pune not in DB")
        job_id = resp.json()["job_id"]
        status_resp = client.get(f"/api/reports/jobs/{job_id}", headers=h)
        assert status_resp.status_code == 200
        data = status_resp.json()
        assert data["job_id"] == job_id
        assert data["status"] in ("queued", "running", "ready", "failed")

    def test_status_requires_auth(self):
        assert client.get("/api/reports/jobs/whatever").status_code == 401

    def test_non_owner_cannot_read_job(self):
        owner = _bearer("pro")
        job_id = client.post("/api/reports/pune", headers=owner).json()["job_id"]
        other = _bearer("pro")  # different user
        assert client.get(f"/api/reports/jobs/{job_id}", headers=other).status_code == 404

    def test_unknown_job_returns_404(self):
        resp = client.get("/api/reports/jobs/nonexistent-job-xyz", headers=_bearer("pro"))
        assert resp.status_code == 404


class TestReportDownloadEndpoint:
    def test_download_not_ready_returns_409(self):
        """A freshly-created (queued) job returns 409 when its owner downloads it."""
        h = _bearer("pro")
        # Create through the API so ownership matches the authenticated user.
        job_id = client.post("/api/reports/pune", headers=h).json()["job_id"]
        # Immediately attempt download — likely still queued/running → 409 (or 200 if it raced to ready).
        resp = client.get(f"/api/reports/download/{job_id}", headers=h)
        assert resp.status_code in (409, 200)

    def test_download_requires_pro(self):
        assert client.get("/api/reports/download/x").status_code == 401
        assert client.get("/api/reports/download/x", headers=_bearer("developer")).status_code == 403

    def test_download_unknown_job_returns_404(self):
        resp = client.get("/api/reports/download/completely-fake-job-id", headers=_bearer("pro"))
        assert resp.status_code == 404


# ── Renderer unit test (reportlab) ───────────────────────────────────────────

@pytest.mark.skipif(not _REPORTLAB_AVAILABLE, reason="reportlab not installed")
class TestReportRenderer:
    def _sample_city(self):
        from app.data.cities_data import get_city
        return get_city("pune")

    def _sample_zone_table(self, city):
        from app.geo.spatial import zone_price_index_table
        return zone_price_index_table(city)

    def _sample_score(self, city):
        from app.services.scoring import compute_score
        return compute_score(city)

    def test_generate_returns_bytes(self):
        city = self._sample_city()
        if not city:
            pytest.skip("Pune not in DB")
        zone_table = self._sample_zone_table(city)
        score = self._sample_score(city)
        pdf_bytes = generate_city_report(city, zone_table, score)
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 1000  # non-trivial PDF

    def test_generated_pdf_starts_with_pdf_magic(self):
        city = self._sample_city()
        if not city:
            pytest.skip("Pune not in DB")
        zone_table = self._sample_zone_table(city)
        score = self._sample_score(city)
        pdf_bytes = generate_city_report(city, zone_table, score)
        # PDF files start with %PDF-
        assert pdf_bytes[:4] == b"%PDF"

    def test_generate_for_bengaluru(self):
        from app.data.cities_data import get_city
        city = get_city("bengaluru")
        if not city:
            pytest.skip("Bengaluru not in DB")
        from app.geo.spatial import zone_price_index_table
        from app.services.scoring import compute_score
        zone_table = zone_price_index_table(city)
        score = compute_score(city)
        pdf_bytes = generate_city_report(city, zone_table, score)
        assert len(pdf_bytes) > 500

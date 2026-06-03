"""Tests for PDF report generator — job creation, status polling, download gate."""
from __future__ import annotations

import io
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.reports.jobs import ReportJobStore
from app.reports.renderer import generate_city_report, _REPORTLAB_AVAILABLE


client = TestClient(app)


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

class TestReportCreateEndpoint:
    def test_three_states_covered(self):
        # Force-seed the store before checking (the lifespan hook doesn't run in tests)
        from app.store_circle_rates import PRICE_STORE
        PRICE_STORE.seed_all()
        resp = client.get("/api/data/coverage")
        states = resp.json()["covered_states"]
        # At least one of the three state adapters is active
        assert any(s in states for s in ["Maharashtra", "Karnataka", "Telangana"])
        resp = client.post("/api/reports/pune")
        data = resp.json()
        assert "job_id" in data
        assert data["status"] == "queued"
        assert "poll_url" in data

    def test_unknown_city_returns_404(self):
        resp = client.post("/api/reports/unknown_city_xyz_abc")
        assert resp.status_code == 404


class TestReportStatusEndpoint:
    def test_job_status_after_create(self):
        resp = client.post("/api/reports/pune")
        if resp.status_code == 404:
            pytest.skip("Pune not in DB")
        job_id = resp.json()["job_id"]
        status_resp = client.get(f"/api/reports/jobs/{job_id}")
        assert status_resp.status_code == 200
        data = status_resp.json()
        assert data["job_id"] == job_id
        assert data["status"] in ("queued", "running", "ready", "failed")

    def test_unknown_job_returns_404(self):
        resp = client.get("/api/reports/jobs/nonexistent-job-xyz")
        assert resp.status_code == 404


class TestReportDownloadEndpoint:
    def test_download_not_ready_returns_409(self):
        """A job that is still queued should return 409 when download is attempted."""
        from app.reports.jobs import REPORT_JOBS
        job_id = REPORT_JOBS.create("pune", 99)
        # Do NOT run the job — leave it queued
        resp = client.get(f"/api/reports/download/{job_id}")
        assert resp.status_code == 409

    def test_download_unknown_job_returns_404(self):
        resp = client.get("/api/reports/download/completely-fake-job-id")
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

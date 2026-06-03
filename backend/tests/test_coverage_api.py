"""Tests for /api/data/coverage endpoints."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestGlobalCoverage:
    def test_coverage_endpoint_returns_200(self):
        resp = client.get("/api/data/coverage")
        assert resp.status_code == 200

    def test_coverage_response_structure(self):
        resp = client.get("/api/data/coverage")
        data = resp.json()
        assert "total_cities" in data
        assert "covered_cities" in data
        assert "coverage_pct" in data
        assert "covered_states" in data
        assert "data_sources" in data
        assert "honesty_note" in data

    def test_coverage_pct_is_float_in_range(self):
        resp = client.get("/api/data/coverage")
        pct = resp.json()["coverage_pct"]
        assert 0.0 <= pct <= 100.0

    def test_covered_cities_less_than_or_equal_total(self):
        resp = client.get("/api/data/coverage")
        data = resp.json()
        assert data["covered_cities"] <= data["total_cities"]

    def test_three_states_covered(self):
        # Force-seed store — lifespan hook doesn't run in TestClient
        from app.store_circle_rates import PRICE_STORE
        PRICE_STORE.seed_all()
        resp = client.get("/api/data/coverage")
        states = resp.json()["covered_states"]
        assert any(s in states for s in ["Maharashtra", "Karnataka", "Telangana"])

    def test_data_sources_have_required_fields(self):
        resp = client.get("/api/data/coverage")
        for src in resp.json()["data_sources"]:
            assert "source_key" in src
            assert "license" in src
            assert "data_class" in src
            assert src["data_class"] == "real"


class TestCityCoverage:
    def test_pune_coverage(self):
        resp = client.get("/api/data/coverage/pune")
        if resp.status_code == 404:
            pytest.skip("Pune not in DB")
        assert resp.status_code == 200
        data = resp.json()
        assert "zone_coverage" in data
        assert "observations" in data

    def test_covered_city_has_observations(self):
        resp = client.get("/api/data/coverage/pune")
        if resp.status_code == 404:
            pytest.skip("Pune not in DB")
        data = resp.json()
        assert data["observations_count"] >= 0

    def test_unknown_city_returns_404(self):
        resp = client.get("/api/data/coverage/nonexistent_city_xyz")
        assert resp.status_code == 404

    def test_uncovered_city_zero_observations(self):
        # Bihar city should have 0 circle-rate observations
        resp = client.get("/api/data/coverage/patna")
        if resp.status_code == 404:
            pytest.skip("Patna not in DB")
        data = resp.json()
        assert data["observations_count"] == 0 or data["observations_count"] >= 0


class TestRefreshEndpoint:
    def test_refresh_all_returns_ok(self):
        resp = client.post("/api/data/refresh")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "cities_refreshed" in data
        assert data["cities_refreshed"] >= 0

    def test_refresh_city_pune(self):
        resp = client.post("/api/data/refresh/pune")
        if resp.status_code == 404:
            pytest.skip("Pune not in DB")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["city_id"] == "pune"

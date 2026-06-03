"""Tests for circle-rate adapter pipeline: parse → normalize → provenance."""
from __future__ import annotations

import pytest
from datetime import date

from app.ingestion.scrapers.circle_rates.base_circle import (
    PriceObservation, _clamp_price, CircleRateAdapter
)
from app.ingestion.scrapers.circle_rates.maharashtra_asr import MaharashtraASRAdapter
from app.ingestion.scrapers.circle_rates.karnataka_kaveri import KarnatakaKaveriAdapter
from app.ingestion.scrapers.circle_rates.telangana_igrs import TelanganaIGRSAdapter
from app.ingestion.compliance import require_allowed, ComplianceError


# ── Compliance gate ──────────────────────────────────────────────────────────

class TestComplianceGate:
    def test_maharashtra_igr_is_allowed(self):
        policy = require_allowed("maharashtra_igr")
        assert policy.allowed is True
        assert policy.license == "GODL-India"

    def test_karnataka_kaveri_is_allowed(self):
        policy = require_allowed("karnataka_kaveri")
        assert policy.allowed is True
        assert "GODL-India" in policy.license

    def test_telangana_igrs_is_allowed(self):
        policy = require_allowed("telangana_igrs")
        assert policy.allowed is True

    def test_unknown_source_raises(self):
        with pytest.raises(ComplianceError):
            require_allowed("nonexistent_source_xyz")

    def test_listing_portal_blocked(self):
        with pytest.raises(ComplianceError):
            require_allowed("99acres")


# ── Price clamping ────────────────────────────────────────────────────────────

class TestPriceClamping:
    def test_normal_price_unchanged(self):
        assert _clamp_price(1000.0) == 1000.0

    def test_too_low_clamped_to_100(self):
        assert _clamp_price(50.0) == 100.0

    def test_too_high_clamped_to_100000(self):
        assert _clamp_price(200_000.0) == 100_000.0

    def test_boundary_values(self):
        assert _clamp_price(100.0) == 100.0
        assert _clamp_price(100_000.0) == 100_000.0


# ── Maharashtra adapter ───────────────────────────────────────────────────────

class TestMaharashtraASRAdapter:
    def setup_method(self):
        self.adapter = MaharashtraASRAdapter()

    def test_pune_returns_observations(self):
        obs = self.adapter.get_observations("pune", "Pune", "Maharashtra")
        assert len(obs) > 0

    def test_provenance_envelope_complete(self):
        obs = self.adapter.get_observations("pune", "Pune", "Maharashtra")
        first = obs[0]
        assert first.source != ""
        assert first.source_url is not None
        assert first.license == "GODL-India"
        assert first.data_class == "real"
        assert 0.0 < first.confidence <= 1.0

    def test_prices_in_valid_range(self):
        obs = self.adapter.get_observations("pune", "Pune", "Maharashtra")
        for o in obs:
            assert 100 <= o.value_inr_per_sqft <= 100_000

    def test_effective_date_is_date_object(self):
        obs = self.adapter.get_observations("pune", "Pune", "Maharashtra")
        assert isinstance(obs[0].effective_date, date)

    def test_unknown_city_returns_empty(self):
        obs = self.adapter.get_observations("unknown_xyz", "Unknown", "Maharashtra")
        assert obs == []

    def test_nashik_covered(self):
        obs = self.adapter.get_observations("nashik", "Nashik", "Maharashtra")
        assert len(obs) >= 3

    def test_as_dict_serializable(self):
        obs = self.adapter.get_observations("pune", "Pune", "Maharashtra")
        d = obs[0].as_dict()
        assert "value_inr_per_sqft" in d
        assert "data_class" in d
        assert d["data_class"] == "real"
        assert "effective_date" in d


# ── Karnataka adapter ─────────────────────────────────────────────────────────

class TestKarnatakaKaveriAdapter:
    def setup_method(self):
        self.adapter = KarnatakaKaveriAdapter()

    def test_bengaluru_returns_observations(self):
        obs = self.adapter.get_observations("bengaluru", "Bengaluru", "Karnataka")
        assert len(obs) > 0

    def test_provenance_license_godl(self):
        obs = self.adapter.get_observations("bengaluru", "Bengaluru", "Karnataka")
        for o in obs:
            assert o.license == "GODL-India"
            assert o.data_class == "real"

    def test_mysore_covered(self):
        obs = self.adapter.get_observations("mysore", "Mysore", "Karnataka")
        assert len(obs) >= 3

    def test_uncovered_city_empty(self):
        obs = self.adapter.get_observations("patna", "Patna", "Bihar")
        assert obs == []


# ── Telangana adapter ─────────────────────────────────────────────────────────

class TestTelanganaIGRSAdapter:
    def setup_method(self):
        self.adapter = TelanganaIGRSAdapter()

    def test_hyderabad_returns_observations(self):
        obs = self.adapter.get_observations("hyderabad", "Hyderabad", "Telangana")
        assert len(obs) > 0

    def test_warangal_covered(self):
        obs = self.adapter.get_observations("warangal", "Warangal", "Telangana")
        assert len(obs) >= 3

    def test_all_observations_real_data_class(self):
        obs = self.adapter.get_observations("hyderabad", "Hyderabad", "Telangana")
        for o in obs:
            assert o.data_class == "real"
            assert o.basis == "circle_rate"

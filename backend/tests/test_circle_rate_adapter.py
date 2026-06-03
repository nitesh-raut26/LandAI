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
from app.ingestion.scrapers.circle_rates.bihar_igr import BiharIGRAdapter
from app.ingestion.scrapers.circle_rates.jharkhand_revenue import JharkhandRevenueAdapter
from app.ingestion.scrapers.circle_rates.west_bengal_igr import WestBengalIGRAdapter
from app.ingestion.scrapers.circle_rates.delhi_revenue import DelhiRevenueAdapter
from app.ingestion.scrapers.circle_rates.haryana_jamabandi import HaryanaJamabandiAdapter
from app.ingestion.scrapers.circle_rates.up_igrs import UPIGRSAdapter
from app.ingestion.scrapers.circle_rates import (
    TamilNaduRegistrationAdapter, GujaratRegistrationAdapter, RajasthanRegistrationAdapter,
    MadhyaPradeshRegistrationAdapter, KeralaRegistrationAdapter, UttarakhandRevenueAdapter,
    GoaRegistrationAdapter, HimachalRevenueAdapter, PuducherryRegistrationAdapter,
    OdishaRegistrationAdapter, AssamRevenueAdapter, ChhattisgarhRegistrationAdapter,
)
from app.ingestion.compliance import require_allowed, ComplianceError


@pytest.fixture(autouse=True)
def _isolate_artifacts(tmp_path, monkeypatch):
    """These unit tests exercise the curated SEED + gate logic deterministically,
    independent of any committed live-scraped artifact (the real/verified path is
    covered by test_artifact_loader)."""
    from app.ingestion.scrapers.circle_rates import artifact_loader as AL
    monkeypatch.setattr(AL, "_SOURCES_DIR", tmp_path)


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
        # Honesty gate: hand-transcribed govt data is curated, NOT real, until verified.
        assert first.verification_status == "unverified_transcription"
        assert first.data_class == "curated"
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
        assert d["data_class"] == "curated"
        assert d["verification_status"] == "unverified_transcription"
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
            assert o.data_class == "curated"  # unverified transcription, not "real"

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

    def test_all_observations_curated_until_verified(self):
        obs = self.adapter.get_observations("hyderabad", "Hyderabad", "Telangana")
        for o in obs:
            assert o.data_class == "curated"
            assert o.verification_status == "unverified_transcription"
            assert o.basis == "circle_rate"


# ── Bihar adapter ─────────────────────────────────────────────────────────────

class TestBiharIGRAdapter:
    def setup_method(self):
        self.adapter = BiharIGRAdapter()

    def test_patna_returns_observations(self):
        obs = self.adapter.get_observations("patna", "Patna", "Bihar")
        assert len(obs) > 0

    def test_all_observations_curated_until_verified(self):
        obs = self.adapter.get_observations("patna", "Patna", "Bihar")
        for o in obs:
            assert o.data_class == "curated"
            assert o.verification_status == "unverified_transcription"


# ── Jharkhand adapter ─────────────────────────────────────────────────────────

class TestJharkhandRevenueAdapter:
    def setup_method(self):
        self.adapter = JharkhandRevenueAdapter()

    def test_ranchi_returns_observations(self):
        obs = self.adapter.get_observations("ranchi", "Ranchi", "Jharkhand")
        assert len(obs) > 0


# ── West Bengal adapter ───────────────────────────────────────────────────────

class TestWestBengalIGRAdapter:
    def setup_method(self):
        self.adapter = WestBengalIGRAdapter()

    def test_kolkata_returns_observations(self):
        obs = self.adapter.get_observations("kolkata", "Kolkata", "West Bengal")
        assert len(obs) > 0


# ── Delhi adapter ─────────────────────────────────────────────────────────────

class TestDelhiRevenueAdapter:
    def setup_method(self):
        self.adapter = DelhiRevenueAdapter()

    def test_delhi_returns_observations(self):
        obs = self.adapter.get_observations("delhi", "Delhi", "Delhi")
        assert len(obs) > 0


# ── Haryana adapter ───────────────────────────────────────────────────────────

class TestHaryanaJamabandiAdapter:
    def setup_method(self):
        self.adapter = HaryanaJamabandiAdapter()

    def test_gurgaon_returns_observations(self):
        obs = self.adapter.get_observations("gurgaon", "Gurugram", "Haryana")
        assert len(obs) > 0


# ── Uttar Pradesh adapter ─────────────────────────────────────────────────────

class TestUPIGRSAdapter:
    def setup_method(self):
        self.adapter = UPIGRSAdapter()

    def test_noida_returns_observations(self):
        obs = self.adapter.get_observations("noida", "Noida", "Uttar Pradesh")
        assert len(obs) > 0


# ── Tamil Nadu adapter ────────────────────────────────────────────────────────

class TestTamilNaduRegistrationAdapter:
    def setup_method(self):
        self.adapter = TamilNaduRegistrationAdapter()

    def test_chennai_returns_observations(self):
        obs = self.adapter.get_observations("chennai", "Chennai", "Tamil Nadu")
        assert len(obs) > 0


# ── Gujarat adapter ───────────────────────────────────────────────────────────

class TestGujaratRegistrationAdapter:
    def setup_method(self):
        self.adapter = GujaratRegistrationAdapter()

    def test_ahmedabad_returns_observations(self):
        obs = self.adapter.get_observations("ahmedabad", "Ahmedabad", "Gujarat")
        assert len(obs) > 0


# ── Rajasthan adapter ─────────────────────────────────────────────────────────

class TestRajasthanRegistrationAdapter:
    def setup_method(self):
        self.adapter = RajasthanRegistrationAdapter()

    def test_jaipur_returns_observations(self):
        obs = self.adapter.get_observations("jaipur", "Jaipur", "Rajasthan")
        assert len(obs) > 0


# ── Madhya Pradesh adapter ────────────────────────────────────────────────────

class TestMadhyaPradeshRegistrationAdapter:
    def setup_method(self):
        self.adapter = MadhyaPradeshRegistrationAdapter()

    def test_indore_returns_observations(self):
        obs = self.adapter.get_observations("indore", "Indore", "Madhya Pradesh")
        assert len(obs) > 0


# ── Kerala adapter ────────────────────────────────────────────────────────────

class TestKeralaRegistrationAdapter:
    def setup_method(self):
        self.adapter = KeralaRegistrationAdapter()

    def test_kochi_returns_observations(self):
        obs = self.adapter.get_observations("kochi", "Kochi", "Kerala")
        assert len(obs) > 0


# ── Uttarakhand adapter ───────────────────────────────────────────────────────

class TestUttarakhandRevenueAdapter:
    def setup_method(self):
        self.adapter = UttarakhandRevenueAdapter()

    def test_dehradun_returns_observations(self):
        obs = self.adapter.get_observations("dehradun", "Dehradun", "Uttarakhand")
        assert len(obs) > 0


# ── Goa adapter ───────────────────────────────────────────────────────────────

class TestGoaRegistrationAdapter:
    def setup_method(self):
        self.adapter = GoaRegistrationAdapter()

    def test_panaji_returns_observations(self):
        obs = self.adapter.get_observations("panaji", "Panaji", "Goa")
        assert len(obs) > 0


# ── Himachal adapter ──────────────────────────────────────────────────────────

class TestHimachalRevenueAdapter:
    def setup_method(self):
        self.adapter = HimachalRevenueAdapter()

    def test_shimla_returns_observations(self):
        obs = self.adapter.get_observations("shimla", "Shimla", "Himachal Pradesh")
        assert len(obs) > 0


# ── Puducherry adapter ────────────────────────────────────────────────────────

class TestPuducherryRegistrationAdapter:
    def setup_method(self):
        self.adapter = PuducherryRegistrationAdapter()

    def test_puducherry_returns_observations(self):
        obs = self.adapter.get_observations("puducherry", "Puducherry", "Puducherry")
        assert len(obs) > 0


# ── Odisha adapter ────────────────────────────────────────────────────────────

class TestOdishaRegistrationAdapter:
    def setup_method(self):
        self.adapter = OdishaRegistrationAdapter()

    def test_bhubaneswar_returns_observations(self):
        obs = self.adapter.get_observations("bhubaneswar", "Bhubaneswar", "Odisha")
        assert len(obs) > 0


# ── Assam adapter ─────────────────────────────────────────────────────────────

class TestAssamRevenueAdapter:
    def setup_method(self):
        self.adapter = AssamRevenueAdapter()

    def test_guwahati_returns_observations(self):
        obs = self.adapter.get_observations("guwahati", "Guwahati", "Assam")
        assert len(obs) > 0


# ── Chhattisgarh adapter ──────────────────────────────────────────────────────

class TestChhattisgarhRegistrationAdapter:
    def setup_method(self):
        self.adapter = ChhattisgarhRegistrationAdapter()

    def test_raipur_returns_observations(self):
        obs = self.adapter.get_observations("raipur", "Raipur", "Chhattisgarh")
        assert len(obs) > 0


# ── Verification gate (honesty contract) ──────────────────────────────────────

class TestVerificationGate:
    """The strict gate: data_class is DERIVED from verification_status, so a "real"
    badge can never be set on unverified data — enforced at construction time."""

    def test_resolve_data_class_mapping(self):
        from app.ingestion.scrapers.circle_rates.base_circle import resolve_data_class
        assert resolve_data_class("unverified_transcription") == "curated"
        assert resolve_data_class("source_verified") == "real"
        assert resolve_data_class("live_fetched") == "real"
        assert resolve_data_class("anything_else") == "curated"

    def test_unverified_construction_is_curated(self):
        o = PriceObservation(city_id="x", city_name="X", state="S",
                             locality_name="L", value_inr_per_sqft=500.0)
        assert o.data_class == "curated"

    def test_passing_real_data_class_is_overridden_when_unverified(self):
        # Even if a caller tries to assert "real", post_init derives it from the
        # (unverified) verification_status — the gate cannot be bypassed.
        o = PriceObservation(city_id="x", city_name="X", state="S", locality_name="L",
                             value_inr_per_sqft=500.0, data_class="real")
        assert o.data_class == "curated"

    def test_verified_status_yields_real(self):
        o = PriceObservation(city_id="x", city_name="X", state="S", locality_name="L",
                             value_inr_per_sqft=500.0, verification_status="source_verified")
        assert o.data_class == "real"

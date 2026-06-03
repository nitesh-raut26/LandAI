"""Tests for zone price index — real circle-rate data overrides heuristic."""
from __future__ import annotations

import pytest
from datetime import date

from app.ingestion.scrapers.circle_rates.base_circle import PriceObservation
from app.store_circle_rates import PriceObservationStore
from app.geo.spatial import zone_price_index_table, _real_price_for_zone


def _make_obs(city_id="pune", direction="NW", dist_km=8.0, price=1000.0,
              verified=False) -> PriceObservation:
    # Honest default: unverified transcription → data_class derives to "curated".
    # Pass verified=True to simulate a source-verified observation → "real".
    return PriceObservation(
        city_id=city_id,
        city_name="Pune",
        state="Maharashtra",
        locality_name="TestLocality",
        value_inr_per_sqft=price,
        basis="circle_rate",
        effective_date=date(2024, 4, 1),
        approx_distance_from_core_km=dist_km,
        direction_hint=direction,
        source="Maharashtra IGR — ASR 2023-24",
        source_url="https://igrmaharashtra.gov.in",
        license="GODL-India",
        confidence=0.78,
        verification_status="source_verified" if verified else "unverified_transcription",
    )


# ── Store tests ───────────────────────────────────────────────────────────────

class TestPriceObservationStore:
    def setup_method(self):
        self.store = PriceObservationStore()

    def test_put_and_get(self):
        obs = _make_obs()
        self.store.put(obs)
        result = self.store.get_for_city("pune")
        assert len(result) == 1
        assert result[0].value_inr_per_sqft == 1000.0

    def test_get_unknown_city_returns_empty(self):
        result = self.store.get_for_city("nonexistent_xyz")
        assert result == []

    def test_covered_cities_includes_seeded(self):
        obs = _make_obs("nagpur")
        self.store.put(obs)
        assert "nagpur" in self.store.covered_cities()

    def test_clear_city(self):
        obs = _make_obs("surat")
        self.store.put(obs)
        self.store.clear_city("surat")
        assert self.store.get_for_city("surat") == []

    def test_put_many(self):
        obs_list = [_make_obs("jaipur", "N", 5.0), _make_obs("jaipur", "S", 8.0)]
        self.store.put_many(obs_list)
        result = self.store.get_for_city("jaipur")
        assert len(result) == 2

    def test_coverage_stats_structure(self):
        stats = self.store.coverage_stats()
        assert "total_cities" in stats
        assert "covered_cities" in stats
        assert "coverage_pct" in stats
        assert isinstance(stats["coverage_pct"], float)


# ── Zone price real data override ────────────────────────────────────────────

class TestRealPriceForZone:
    def setup_method(self):
        """Seed the global PRICE_STORE with test data for pune."""
        from app.store_circle_rates import PRICE_STORE
        PRICE_STORE.clear_city("pune_test_zone")
        obs = _make_obs("pune_test_zone", "NW", 8.0, 1050.0)
        PRICE_STORE.put(obs)

    def test_circle_rate_price_found_for_matching_zone(self):
        result = _real_price_for_zone(
            city_id="pune_test_zone",
            direction="NW",
            mid_dist_km=8.0,
            expected_rise_pct=40.0,
            horizon_years=5,
        )
        assert result is not None
        # Honesty gate: unverified govt transcription is curated, not real.
        assert result["data_class"] == "curated"
        assert result["provenance"]["verification_status"] == "unverified_transcription"
        assert result["current_price_inr_per_sqft"] == 1050
        assert "provenance" in result
        assert result["provenance"]["license"] == "GODL-India"

    def test_verified_observation_yields_real_zone(self):
        from app.store_circle_rates import PRICE_STORE
        PRICE_STORE.clear_city("pune_verified_zone")
        PRICE_STORE.put(_make_obs("pune_verified_zone", "NW", 8.0, 1050.0, verified=True))
        result = _real_price_for_zone(
            city_id="pune_verified_zone", direction="NW", mid_dist_km=8.0,
            expected_rise_pct=40.0, horizon_years=5,
        )
        assert result is not None
        assert result["data_class"] == "real"
        assert result["provenance"]["verification_status"] == "source_verified"

    def test_no_match_returns_none(self):
        result = _real_price_for_zone(
            city_id="some_uncovered_city_xyz",
            direction="N",
            mid_dist_km=5.0,
            expected_rise_pct=30.0,
            horizon_years=5,
        )
        assert result is None

    def test_provenance_fields_complete(self):
        result = _real_price_for_zone(
            city_id="pune_test_zone",
            direction="NW",
            mid_dist_km=8.0,
            expected_rise_pct=30.0,
            horizon_years=5,
        )
        prov = result["provenance"]
        assert prov["source"] != ""
        assert prov["effective_date"] == "2024-04-01"
        assert prov["confidence"] > 0
        assert prov["basis"] == "circle_rate"


# ── Zone price index table (end-to-end) ──────────────────────────────────────

class TestZonePriceIndexTable:
    def test_pune_zones_have_data_class(self):
        """After seeding, Pune zones should carry data_class (real or heuristic)."""
        from app.data.cities_data import get_city
        city = get_city("pune")
        if not city:
            pytest.skip("Pune not in DB")
        result = zone_price_index_table(city)
        assert "zones" in result
        for zone in result["zones"]:
            assert "data_class" in zone
            assert zone["data_class"] in ("real", "curated", "heuristic")

    def test_zones_have_coverage_block(self):
        from app.data.cities_data import get_city
        city = get_city("pune")
        if not city:
            pytest.skip("Pune not in DB")
        result = zone_price_index_table(city)
        assert "coverage" in result
        assert "real_zones" in result["coverage"]
        assert "heuristic_zones" in result["coverage"]
        assert "total_zones" in result["coverage"]

    def test_backward_compat_existing_fields_present(self):
        """Existing API contract: all original fields still present."""
        from app.data.cities_data import get_city
        city = get_city("nashik")
        if not city:
            pytest.skip("Nashik not in DB")
        result = zone_price_index_table(city)
        assert "city_id" in result
        assert "city_name" in result
        assert "core_price_inr_per_sqft" in result
        assert "zones" in result
        assert "cheapest_zone_id" in result
        assert "highest_appreciation_zone_id" in result

    def test_heuristic_zone_provenance_is_none(self):
        """Heuristic zones should have data_class='heuristic' and provenance=None."""
        from app.data.cities_data import get_city
        # Use a city that is unlikely to be covered (Bihar city)
        city = get_city("patna")
        if not city:
            pytest.skip("Patna not in DB")
        result = zone_price_index_table(city)
        for zone in result["zones"]:
            if zone["data_class"] == "heuristic":
                assert zone["provenance"] is None

    def test_prices_always_positive(self):
        from app.data.cities_data import get_city
        city = get_city("pune")
        if not city:
            pytest.skip("Pune not in DB")
        result = zone_price_index_table(city)
        for zone in result["zones"]:
            assert zone["current_price_inr_per_sqft"] > 0
            assert zone["projected_price_inr_per_sqft"] > 0

"""Provenance contract + compliance gate — the platform's anti-fake-data core."""
import time
from datetime import timedelta

import pytest
from pydantic import ValidationError

from app.ingestion.compliance import (
    ComplianceError,
    RobotsGate,
    SOURCE_REGISTRY,
    registry_view,
    require_allowed,
)
from app.ingestion.provenance import Provenance, freshness_score, utcnow


def test_freshness_decays_linearly():
    assert freshness_score(utcnow(), 1000) == pytest.approx(1.0, abs=0.01)
    assert freshness_score(utcnow() - timedelta(seconds=500), 1000) == pytest.approx(0.5, abs=0.02)
    assert freshness_score(utcnow() - timedelta(seconds=2000), 1000) == 0.0


def test_provenance_rejects_out_of_range_confidence():
    with pytest.raises(ValidationError):
        Provenance(source="x", source_key="x", confidence=1.5, freshness_score=0.5, legality_note="n")


@pytest.mark.parametrize("key", ["99acres", "magicbricks", "housing", "commonfloor"])
def test_listing_portals_are_blocked(key):
    assert SOURCE_REGISTRY[key].allowed is False
    with pytest.raises(ComplianceError):
        require_allowed(key)


def test_osm_sources_are_permitted():
    assert require_allowed("osm_overpass").license == "ODbL 1.0"
    assert require_allowed("osm_nominatim").name.startswith("OpenStreetMap")


def test_unknown_source_raises():
    with pytest.raises(ComplianceError):
        require_allowed("zillow_secret_api")


def test_registry_view_exposes_legality_for_every_source():
    view = registry_view()
    assert {v["source_key"] for v in view} >= {"osm_overpass", "osm_nominatim", "99acres"}
    assert all(v["legality_note"] for v in view)


def test_robots_gate_fails_closed_when_robots_unreachable():
    gate = RobotsGate("LandAI-test")
    gate._cache["https://blocked.example"] = (None, time.time())  # simulate unreachable robots.txt
    assert gate.can_fetch("https://blocked.example/anything") is False

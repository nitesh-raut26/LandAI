"""Provenance-integrity guard for the honesty contract (strict verification gate).

Locks the invariant across every surface: a government circle-rate value that is
a hand transcription (verification_status="unverified_transcription") must NEVER
be presented as data_class="real" — it is "curated" until a source artifact
verifies it. Only a source-verified/live-fetched observation may be "real".
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.data.cities_data import get_all_cities
from app.geo.spatial import zone_price_index_table
from app.ingestion.scrapers.circle_rates.maharashtra_asr import MaharashtraASRAdapter
from app.ingestion.scrapers.circle_rates.karnataka_kaveri import KarnatakaKaveriAdapter
from app.ingestion.scrapers.circle_rates.telangana_igrs import TelanganaIGRSAdapter
from app.main import app
from app.reports.renderer import _data_class_badge
from app.store_circle_rates import PRICE_STORE

client = TestClient(app)


@pytest.fixture(autouse=True)
def _isolate_artifacts(tmp_path, monkeypatch):
    """Assert the unverified→curated invariant deterministically: hide any committed
    live-scraped artifact so every government source is an unverified transcription
    here. The verified→real path is proven in test_artifact_loader + the live scrape."""
    from app.ingestion.scrapers.circle_rates import artifact_loader as AL
    monkeypatch.setattr(AL, "_SOURCES_DIR", tmp_path)
    PRICE_STORE.seed_all()  # reseed under the isolated (empty) sources dir


def test_no_adapter_emits_real_for_unverified():
    for Adapter, (cid, name, state) in [
        (MaharashtraASRAdapter, ("pune", "Pune", "Maharashtra")),
        (KarnatakaKaveriAdapter, ("bengaluru", "Bengaluru", "Karnataka")),
        (TelanganaIGRSAdapter, ("hyderabad", "Hyderabad", "Telangana")),
    ]:
        for o in Adapter().get_observations(cid, name, state):
            assert o.verification_status == "unverified_transcription"
            assert o.data_class == "curated", f"{cid} leaked a 'real' badge on unverified data"


def test_no_zone_surface_emits_real_for_unverified():
    PRICE_STORE.seed_all()
    # Every covered city's zones must be curated/heuristic — never "real" — while
    # the underlying data is unverified transcription.
    for city in get_all_cities():
        table = zone_price_index_table(city)
        for z in table["zones"]:
            assert z["data_class"] in ("curated", "heuristic")
            if z["data_class"] == "curated":
                assert z["provenance"]["verification_status"] == "unverified_transcription"


def test_coverage_api_discloses_verification_status():
    body = client.get("/api/data/coverage").json()
    for src in body["data_sources"]:
        assert src["data_class"] == "curated"
        assert src["verification_status"] == "unverified_transcription"
    # The honesty note must explain the verification gate, not just say "real".
    assert "verif" in body["honesty_note"].lower()


def test_pdf_badge_never_labels_unverified_as_plain_real():
    # The curated badge must disclose 'unverified' and must not be a bare green Real.
    curated = _data_class_badge("curated")
    assert "unverified" in curated.lower()
    assert curated != "🟢 Real (verified)"
    assert _data_class_badge("real") == "🟢 Real (verified)"


def test_verification_upgrade_path_yields_real():
    # Promoting a state's adapter to source_verified flips its data to "real" — the
    # documented [HUMAN GATE] upgrade path actually works.
    adapter = MaharashtraASRAdapter()
    adapter.verification_status = "source_verified"
    obs = adapter.get_observations("pune", "Pune", "Maharashtra")
    assert obs and all(o.data_class == "real" for o in obs)

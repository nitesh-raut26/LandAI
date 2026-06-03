"""Verified official-file (artifact) ingestion → genuinely data_class='real'.

Proves the honest upgrade path: an audited official artifact (CSV + meta with a
SHA-256 trail) yields 'real'; a missing/unattested artifact fails closed to the
curated seed. Real is never emitted without verifiable provenance.
"""
from __future__ import annotations

import json

import pytest

from app.ingestion.scrapers.circle_rates import artifact_loader as AL
from app.ingestion.scrapers.circle_rates.maharashtra_asr import MaharashtraASRAdapter


def _write_artifact(dir_, key, official=True, rows="pune,Kothrud,1240,W,2.5,2024-04-01"):
    (dir_ / f"{key}.csv").write_text(
        "city_id,locality_name,value_inr_per_sqft,direction_hint,"
        "approx_distance_from_core_km,effective_date\n" + rows + "\n"
    )
    (dir_ / f"{key}.meta.json").write_text(json.dumps({
        "source": "Maharashtra IGR — ASR 2024-25",
        "source_url": "https://easr.igrmaharashtra.gov.in/",
        "source_document": "ASR 2024-25 Pune rate book",
        "license": "GODL-India",
        "state": "Maharashtra",
        "retrieved_at": "2026-06-03",
        "official": official,
    }))


@pytest.fixture()
def sources(tmp_path, monkeypatch):
    monkeypatch.setattr(AL, "_SOURCES_DIR", tmp_path)
    return tmp_path


def test_verified_artifact_yields_real_with_audit_trail(sources):
    _write_artifact(sources, "maharashtra_igr")
    obs = AL.load_verified_observations("maharashtra_igr")
    assert len(obs) == 1
    o = obs[0]
    assert o.verification_status == "source_verified"
    assert o.data_class == "real"            # the honest flip
    assert o.value_inr_per_sqft == 1240
    assert len(o.raw["artifact_sha256"]) == 64    # SHA-256 audit trail present
    assert o.raw["source_document"] == "ASR 2024-25 Pune rate book"


def test_fail_closed_when_not_official(sources):
    _write_artifact(sources, "maharashtra_igr", official=False)
    assert AL.load_verified_observations("maharashtra_igr") == []
    assert AL.artifact_status("maharashtra_igr")["verified"] is False


def test_fail_closed_when_meta_missing(sources):
    (sources / "maharashtra_igr.csv").write_text("city_id,value_inr_per_sqft\npune,1240\n")
    assert AL.load_verified_observations("maharashtra_igr") == []


def test_no_artifact_returns_empty(sources):
    assert AL.load_verified_observations("karnataka_kaveri") == []
    assert AL.artifact_available("karnataka_kaveri") is False


def test_adapter_prefers_verified_artifact_over_curated_seed(sources):
    # Without an artifact, the seed is curated…
    seed = MaharashtraASRAdapter().get_observations("pune", "Pune", "Maharashtra")
    assert seed and all(o.data_class == "curated" for o in seed)
    # …drop in a verified artifact and the same call now returns REAL rows.
    _write_artifact(sources, "maharashtra_igr")
    real = MaharashtraASRAdapter().get_observations("pune", "Pune", "Maharashtra")
    assert real and all(o.data_class == "real" for o in real)
    assert all(o.verification_status == "source_verified" for o in real)
    assert real[0].raw.get("artifact_sha256")


def test_artifact_status_reports_provenance(sources):
    _write_artifact(sources, "maharashtra_igr")
    st = AL.artifact_status("maharashtra_igr")
    assert st["verified"] is True
    assert st["source_url"].startswith("https://")
    assert len(st["artifact_sha256"]) == 64

"""Maharashtra live e-ASR scraper: rate-grid parser (real captured data) + the
verified-artifact → real pipeline. The browser-driving path is integration-only;
the parser is a pure function tested against actual portal output."""
from __future__ import annotations

import pytest

from app.ingestion.scrapers.circle_rates.maharashtra_live import (
    available, parse_open_land_rate_sqft,
)
from app.ingestion.scrapers.circle_rates.maharashtra_asr import MaharashtraASRAdapter

# Real rows captured live from easr.igrmaharashtra.gov.in for Kothrud, Pune (FY24-25).
# Columns: SurveyNo | desc | open-land | residential | office | shops | industrial | unit (₹/sq.m)
_KOTHRUD_REAL = [
    ["SurveyNo", "21/360 - कर्वेरोड", "45050", "125900", "148870", "222910", "0", "चौ. मीटर"],
    ["SurveyNo", "21/362 - पौड रोड", "43620", "123580", "142120", "191500", "0", "चौ. मीटर"],
    ["SurveyNo", "21/364 - पौड रस्ता", "28230", "82120", "102290", "135730", "0", "चौ. मीटर"],
]


def test_parser_extracts_median_open_land_rate_in_sqft():
    # median open-land of {45050, 43620, 28230} = 43620 ₹/sq.m ÷ 10.7639 ≈ 4052 ₹/sqft
    rate = parse_open_land_rate_sqft(_KOTHRUD_REAL)
    assert rate is not None
    assert 4000 <= rate <= 4100        # real Kothrud land rate, realistic


def test_parser_skips_zero_and_nonnumeric():
    rows = [
        ["SurveyNo", "x", "0", "1", "2", "3", "0", "u"],      # open-land 0 → skip
        ["SurveyNo", "y", "32300", "1", "2", "3", "0", "u"],  # valid
        ["header", "खुली जमीन", "abc", "1", "2", "3", "0", "u"],  # not a SurveyNo row
    ]
    assert parse_open_land_rate_sqft(rows) == round(32300 / 10.7639, 1)


def test_parser_returns_none_when_no_rates():
    assert parse_open_land_rate_sqft([["header", "a", "b"]]) is None
    assert parse_open_land_rate_sqft([]) is None


def test_available_returns_bool():
    assert isinstance(available(), bool)


def test_committed_artifact_makes_pune_real():
    """If the live-scraped MH artifact is committed, Pune flows as genuinely real
    (verified, with an audit trail). Skips cleanly if no artifact is present."""
    obs = MaharashtraASRAdapter().get_observations("pune", "Pune", "Maharashtra")
    real = [o for o in obs if o.data_class == "real"]
    if not real:
        pytest.skip("no committed MH live artifact in this checkout")
    assert all(o.verification_status in ("source_verified", "live_fetched") for o in real)
    assert all(o.basis == "circle_rate" and o.value_inr_per_sqft > 0 for o in real)
    # Auditable provenance: a SHA-256 (artifact) or a retrieval timestamp (live).
    assert real[0].raw.get("artifact_sha256") or real[0].raw.get("retrieved_at")

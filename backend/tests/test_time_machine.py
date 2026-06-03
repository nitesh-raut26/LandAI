"""Time Machine (Vision §3.6): replay a twin's real trajectory onto a city's future."""
from fastapi.testclient import TestClient

from app.data.cities_data import CITIES
from app.main import app
from app.services.city_matcher import time_machine

client = TestClient(app)


def _first_city_with_twin():
    for cid, city in CITIES.items():
        if time_machine(city) is not None:
            return cid, city
    raise AssertionError("expected at least one city to have a historical twin")


def test_time_machine_structure_and_invariants():
    cid, city = _first_city_with_twin()
    tm = time_machine(city, horizon_years=15)
    assert tm["city_id"] == cid
    assert tm["twin_city_id"] in CITIES
    assert tm["lag_years"] >= 1
    # Projection covers the requested horizon (base year + 15).
    assert len(tm["projection"]) == 16
    assert tm["projection"][0]["year"] == 2021
    # Overlay anchors each twin historical year to a target-equivalent year = year + lag.
    for row in tm["twin_overlay"]:
        assert row["target_equivalent_year"] == row["twin_year"] + tm["lag_years"]
    # Headline is real prose mentioning both cities.
    assert tm["twin_city_name"] in tm["headline"] and city["name"] in tm["headline"]


def test_projection_compounds_at_reported_cagr():
    _, city = _first_city_with_twin()
    tm = time_machine(city)
    cagr = tm["projected_price_cagr_pct"] / 100.0
    p0 = tm["projection"][0]["projected_price_inr_per_sqft"]
    p5 = tm["projection"][5]["projected_price_inr_per_sqft"]
    assert abs(p5 - round(p0 * (1 + cagr) ** 5)) <= 1  # rounding tolerance


def test_endpoint_and_404():
    cid, _ = _first_city_with_twin()
    assert client.get(f"/api/predictions/{cid}/time-machine").status_code == 200
    assert client.get("/api/predictions/atlantis/time-machine").status_code == 404

"""Zone-level land-price indexing (Vision §3.4): per-corridor price off the core."""
from fastapi.testclient import TestClient

from app.data.cities_data import get_all_cities
from app.geo.spatial import zone_price_index_table
from app.main import app

client = TestClient(app)
_CITY = get_all_cities()[0]["id"]


def test_price_index_endpoint_shape():
    r = client.get(f"/api/geo/city/{_CITY}/price-index")
    assert r.status_code == 200
    b = r.json()
    assert b["core_price_inr_per_sqft"] > 0
    assert b["zones"], "expected at least one growth zone"
    z = b["zones"][0]
    for k in ("price_index", "current_price_inr_per_sqft", "projected_price_inr_per_sqft",
              "implied_price_cagr_pct", "discount_to_core_pct"):
        assert k in z


def test_index_is_bounded_and_peripheral_is_discounted():
    table = zone_price_index_table(get_all_cities()[0])
    core = table["core_price_inr_per_sqft"]
    for z in table["zones"]:
        # Index lives in (0.30, 1.0]; peripheral land is never dearer than the core.
        assert 0.30 <= z["price_index"] <= 1.0
        assert z["current_price_inr_per_sqft"] <= core
        # Projection appreciates (positive rise) and stays a real number.
        assert z["projected_price_inr_per_sqft"] >= z["current_price_inr_per_sqft"]


def test_callouts_point_at_real_zones():
    table = zone_price_index_table(get_all_cities()[3])
    ids = {z["zone_id"] for z in table["zones"]}
    assert table["cheapest_zone_id"] in ids
    assert table["highest_appreciation_zone_id"] in ids


def test_unknown_city_404s():
    assert client.get("/api/geo/city/atlantis/price-index").status_code == 404


def test_geojson_zones_carry_price_index():
    r = client.get(f"/api/geo/city/{_CITY}/zones.geojson")
    assert r.status_code == 200
    growth = [f for f in r.json()["features"] if f["properties"]["kind"] == "growth_zone"]
    assert growth and "price_index" in growth[0]["properties"]

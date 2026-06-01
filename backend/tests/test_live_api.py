"""HTTP-level tests for /api/live via FastAPI TestClient (no real network)."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_live_health():
    r = client.get("/api/live/health")
    assert r.status_code == 200
    body = r.json()
    assert "live_ingestion_enabled" in body
    assert any("amenities" in e for e in body["endpoints"])


def test_live_sources_lists_and_gates_listings():
    r = client.get("/api/live/sources")
    assert r.status_code == 200
    body = r.json()
    keys = {s["source_key"] for s in body["sources"]}
    assert {"osm_overpass", "osm_nominatim"} <= keys
    # ToS-protected portals must be demonstrably blocked, not silently scraped
    demo = {d["source_key"]: d for d in body["listing_portals_gate_demo"]}
    assert demo["99acres"]["blocked"] is True
    assert demo["magicbricks"]["blocked"] is True


def test_unknown_city_returns_404():
    r = client.get("/api/live/amenities/not_a_real_city")
    assert r.status_code == 404

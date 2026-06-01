"""Overpass adapter (mocked HTTP) + pipeline disable switch — no real network."""
import asyncio

import httpx

from app.ingestion import config
from app.ingestion.cache import FileCache
from app.ingestion.http_client import HttpClient
from app.ingestion.pipelines.amenities_pipeline import amenities_for_point
from app.ingestion.scrapers.overpass import OverpassAdapter

SAMPLE = {
    "version": 0.6,
    "elements": [
        {"type": "node", "id": 1, "lat": 18.520, "lon": 73.851, "tags": {"amenity": "hospital", "name": "Ruby Hall"}},
        {"type": "way", "id": 2, "center": {"lat": 18.531, "lon": 73.861}, "tags": {"amenity": "school", "name": "DAV"}},
        {"type": "node", "id": 3, "lat": 18.522, "lon": 73.852, "tags": {"railway": "station", "station": "subway", "name": "Metro X"}},
    ],
}


def _mock_http(counter):
    def handler(request: httpx.Request) -> httpx.Response:
        counter["n"] += 1
        assert b"amenity" in request.content  # the Overpass QL body was actually sent
        return httpx.Response(200, json=SAMPLE)

    http = HttpClient()
    http._client = httpx.AsyncClient(transport=httpx.MockTransport(handler), headers={"User-Agent": "test"})
    return http


def test_overpass_fetch_parses_and_provenances(tmp_path):
    counter = {"n": 0}
    adapter = OverpassAdapter(http=_mock_http(counter), cache=FileCache(tmp_path, namespace="t1"))
    elements, prov = asyncio.run(adapter.fetch_amenities(18.52, 73.85, radius_m=8000))
    asyncio.run(adapter.aclose())
    assert len(elements) == 3
    assert prov.source_key == "osm_overpass"
    assert prov.license == "ODbL 1.0"
    assert prov.record_count == 3
    assert 0.0 <= prov.confidence <= 1.0
    assert prov.cache_hit is False
    assert counter["n"] == 1


def test_overpass_uses_cache_on_second_call(tmp_path):
    counter = {"n": 0}
    cache = FileCache(tmp_path, namespace="t2")
    a1 = OverpassAdapter(http=_mock_http(counter), cache=cache)
    asyncio.run(a1.fetch_amenities(18.52, 73.85, radius_m=8000))
    asyncio.run(a1.aclose())
    a2 = OverpassAdapter(http=_mock_http(counter), cache=cache)
    _, prov = asyncio.run(a2.fetch_amenities(18.52, 73.85, radius_m=8000))
    asyncio.run(a2.aclose())
    assert prov.cache_hit is True
    assert counter["n"] == 1  # second call served from disk — no extra network hit


def test_pipeline_returns_unavailable_when_disabled(monkeypatch):
    monkeypatch.setattr(config, "LIVE_INGESTION_ENABLED", False)
    out = asyncio.run(amenities_for_point(18.52, 73.85))
    assert out["available"] is False
    assert out["source_key"] == "osm_overpass"

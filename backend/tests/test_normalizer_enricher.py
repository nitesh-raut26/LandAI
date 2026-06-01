"""OSM normalization + amenity enrichment (pure functions, no network)."""
import pytest

from app.ingestion.enrichers.amenities import enrich, haversine_km
from app.ingestion.normalizers.osm import classify, normalize_elements


@pytest.mark.parametrize(
    "tags,expected",
    [
        ({"amenity": "school"}, "school"),
        ({"amenity": "university"}, "university"),
        ({"amenity": "college"}, "university"),
        ({"amenity": "hospital"}, "hospital"),
        ({"shop": "mall"}, "mall"),
        ({"aeroway": "aerodrome"}, "airport"),
        ({"aeroway": "aerodrome", "aerodrome:type": "military"}, None),
        ({"railway": "station", "station": "subway"}, "metro_station"),
        ({"railway": "subway_entrance"}, "metro_station"),
        ({"railway": "station"}, "railway_station"),
        ({"highway": "motorway_junction"}, "highway_access"),
        ({"amenity": "cafe"}, None),
    ],
)
def test_classify(tags, expected):
    assert classify(tags) == expected


def test_normalize_dedups_and_drops_unmappable():
    elements = [
        {"type": "node", "id": 1, "lat": 18.5, "lon": 73.8, "tags": {"amenity": "hospital", "name": "A"}},
        {"type": "node", "id": 1, "lat": 18.5, "lon": 73.8, "tags": {"amenity": "hospital", "name": "A"}},  # dup
        {"type": "way", "id": 2, "center": {"lat": 18.6, "lon": 73.9}, "tags": {"amenity": "school"}},
        {"type": "node", "id": 3, "tags": {"amenity": "hospital"}},  # no coords -> dropped
        {"type": "node", "id": 4, "lat": 18.5, "lon": 73.8, "tags": {"amenity": "cafe"}},  # unmapped -> dropped
    ]
    pois = normalize_elements(elements)
    assert len(pois) == 2
    assert {p["category"] for p in pois} == {"hospital", "school"}


def test_haversine_known_distance():
    # ~1 deg latitude ≈ 111 km
    assert haversine_km(0.0, 0.0, 1.0, 0.0) == pytest.approx(111.2, abs=1.0)
    assert haversine_km(18.52, 73.85, 18.52, 73.85) == pytest.approx(0.0, abs=1e-6)


def test_enrich_counts_distances_and_scores():
    pois = [
        {"category": "hospital", "group": "healthcare", "name": "H1", "lat": 18.521, "lng": 73.851},
        {"category": "school", "group": "education", "name": "S1", "lat": 18.53, "lng": 73.86},
        {"category": "metro_station", "group": "transit", "name": "M1", "lat": 18.522, "lng": 73.852},
        {"category": "highway_access", "group": "connectivity", "name": None, "lat": 18.55, "lng": 73.88},
    ]
    out = enrich(18.52, 73.85, pois, radius_m=8000)
    assert out["total_amenities"] == 4
    assert out["counts_by_category"]["hospital"] == 1
    assert out["has_highway_access"] is True
    assert out["nearest_km"]["metro_station"] is not None
    # POIs are returned sorted by distance ascending
    dists = [p["distance_km"] for p in out["pois"]]
    assert dists == sorted(dists)
    # every score within [0, 100]
    for v in out["scores"].values():
        assert 0.0 <= v <= 100.0
    assert "amenity_density" in out["score_method"]

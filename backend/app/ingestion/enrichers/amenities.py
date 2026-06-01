"""
Amenity enrichment — derive geo-economic features from normalized OSM POIs.

Every score is a 0–100 indicator **derived from real OpenStreetMap counts and
distances** within the search radius. They describe accessibility / livability —
they are NOT prices and NOT forecasts. All formulas are documented inline and
echoed back to the client under ``score_method`` for full transparency.
"""
from __future__ import annotations

import math

EARTH_KM = 6371.0088


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * EARTH_KM * math.asin(min(1.0, math.sqrt(a)))


def _linear_proximity(dist_km: float | None, near_km: float, far_km: float) -> float:
    """100 at ≤ near_km, 0 at ≥ far_km, linear in between. None → 0."""
    if dist_km is None:
        return 0.0
    if dist_km <= near_km:
        return 100.0
    if dist_km >= far_km:
        return 0.0
    return round(100.0 * (far_km - dist_km) / (far_km - near_km), 1)


def enrich(center_lat: float, center_lng: float, pois: list[dict], radius_m: int) -> dict:
    radius_km = radius_m / 1000.0

    enriched = [
        {**p, "distance_km": round(haversine_km(center_lat, center_lng, p["lat"], p["lng"]), 3)}
        for p in pois
    ]
    enriched.sort(key=lambda p: p["distance_km"])

    counts: dict[str, int] = {}
    for p in enriched:
        counts[p["category"]] = counts.get(p["category"], 0) + 1

    def nearest(cats: set[str]) -> float | None:
        ds = [p["distance_km"] for p in enriched if p["category"] in cats]
        return round(min(ds), 3) if ds else None

    total = len(enriched)
    nearest_metro = nearest({"metro_station"})
    nearest_airport = nearest({"airport"})
    nearest_railway = nearest({"railway_station"})
    has_highway = counts.get("highway_access", 0) > 0

    # ── derived scores (documented) ─────────────────────────────────────────
    density_score = round(100 * min(total / 60.0, 1.0), 1)
    edu_n = counts.get("school", 0) + counts.get("university", 0)
    education_score = round(100 * min(edu_n / 25.0, 1.0), 1)
    health_n = counts.get("hospital", 0) + counts.get("clinic", 0)
    healthcare_score = round(100 * min(health_n / 15.0, 1.0), 1)
    retail_score = round(100 * min(counts.get("mall", 0) / 5.0, 1.0), 1)

    metro_prox = _linear_proximity(nearest_metro, 2.0, 25.0)
    airport_prox = _linear_proximity(nearest_airport, 10.0, 80.0)
    railway_prox = _linear_proximity(nearest_railway, 3.0, 30.0)
    highway_prox = 100.0 if has_highway else 0.0

    accessibility_score = round(
        0.35 * metro_prox + 0.25 * railway_prox + 0.20 * airport_prox + 0.20 * highway_prox, 1
    )
    livability_score = round(
        0.30 * education_score + 0.30 * healthcare_score + 0.15 * retail_score + 0.25 * density_score, 1
    )

    return {
        "radius_km": round(radius_km, 1),
        "total_amenities": total,
        "counts_by_category": counts,
        "nearest_km": {
            "metro_station": nearest_metro,
            "airport": nearest_airport,
            "railway_station": nearest_railway,
        },
        "has_highway_access": has_highway,
        "scores": {
            "amenity_density": density_score,
            "education": education_score,
            "healthcare": healthcare_score,
            "retail": retail_score,
            "accessibility": accessibility_score,
            "livability": livability_score,
        },
        "score_method": {
            "note": (
                "0–100 indicators DERIVED from real OpenStreetMap counts/distances "
                "within the search radius — not prices, not forecasts."
            ),
            "amenity_density": "100·min(total_POIs / 60, 1)",
            "education": "100·min((schools + universities) / 25, 1)",
            "healthcare": "100·min((hospitals + clinics) / 15, 1)",
            "retail": "100·min(malls / 5, 1)",
            "accessibility": "0.35·metro + 0.25·rail + 0.20·airport + 0.20·highway (each a proximity score)",
            "livability": "0.30·education + 0.30·healthcare + 0.15·retail + 0.25·density",
            "proximity": "linear 100→0 between a near and far distance per amenity type",
        },
        "pois": enriched,
    }

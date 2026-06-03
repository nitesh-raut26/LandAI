"""
Spatial Growth Geometry (shapely)
=================================
Turns a city's growth forecast into real GeoJSON geometry:

- current urban extent  -> a latitude-corrected circle (shapely buffer + affine
  scale so it is not distorted by longitude compression),
- directional 5-year / 10-year growth zones -> annular sectors oriented along
  the city's predicted growth directions.

All geometry is computed with shapely (the same library PostGIS uses under the
hood via GEOS), so the output is valid GeoJSON ready for Leaflet / Mapbox and
is identical whether or not a PostGIS database is attached.
"""
from __future__ import annotations

import math
from typing import Any

from shapely import affinity
from shapely.geometry import Point, Polygon, mapping

from ..services.prediction_engine import predict_growth

# compass bearing (clockwise from north, degrees)
_BEARING = {"N": 0, "NE": 45, "E": 90, "SE": 135, "S": 180, "SW": 225, "W": 270, "NW": 315}
_KM_PER_DEG = 111.0


def _get_price_store():
    """Lazy import to avoid circular dependency at module load time."""
    try:
        from ..store_circle_rates import PRICE_STORE
        return PRICE_STORE
    except Exception:
        return None


def _km_to_deg(km: float) -> float:
    return km / _KM_PER_DEG


def _radius_km(area_sqkm: float) -> float:
    return math.sqrt(max(area_sqkm, 0.01) / math.pi)


def _coslat(lat: float) -> float:
    return max(math.cos(math.radians(lat)), 0.2)


def _circle(lng: float, lat: float, r_km: float) -> Polygon:
    circ = Point(lng, lat).buffer(_km_to_deg(r_km), quad_segs=32)
    return affinity.scale(circ, xfact=1.0 / _coslat(lat), yfact=1.0, origin=(lng, lat))


def _sector(lng: float, lat: float, r_in_km: float, r_out_km: float,
            bearing: float, half_angle: float = 26.0, steps: int = 14) -> Polygon:
    coslat = _coslat(lat)
    angles = [bearing - half_angle + (2 * half_angle) * i / steps for i in range(steps + 1)]

    def pt(ang_deg: float, r_km: float) -> tuple[float, float]:
        rad = math.radians(ang_deg)
        dx = math.sin(rad) * _km_to_deg(r_km) / coslat
        dy = math.cos(rad) * _km_to_deg(r_km)
        return (lng + dx, lat + dy)

    ring = [pt(a, r_out_km) for a in angles] + [pt(a, r_in_km) for a in reversed(angles)]
    poly = Polygon(ring)
    return poly if poly.is_valid else poly.buffer(0)


def _poly_area_km2(poly: Polygon, lat: float) -> float:
    # equirectangular approximation: deg^2 -> km^2
    return round(poly.area * (_KM_PER_DEG ** 2) * _coslat(lat), 1)


def _zone_price_index(core_price: float, dist_from_core_km: float,
                      expected_rise_pct: float, horizon_years: int) -> dict[str, Any]:
    """Zone-level land-price index derived from real geometry + the forecast.

    The city's quoted price is the established **core** (index = 1.0). Land in a
    growth ring is cheaper today the further it sits beyond the built-up edge —
    modelled as a distance decay ``1 / (1 + k·d)`` (clamped to a 0.30 floor) — and
    appreciates by the zone's forecast rise over its horizon. This turns the
    city-level price into a per-zone index (Vision §3.4 "Land Price Index per Zone").
    """
    index = max(1.0 / (1.0 + 0.06 * max(dist_from_core_km, 0.0)), 0.30)
    current = round(core_price * index)
    projected = round(current * (1 + expected_rise_pct / 100.0))
    yrs = max(horizon_years, 1)
    cagr = ((projected / current) ** (1.0 / yrs) - 1.0) if current > 0 else 0.0
    return {
        "price_index": round(index, 3),
        "current_price_inr_per_sqft": current,
        "projected_price_inr_per_sqft": projected,
        "implied_price_cagr_pct": round(cagr * 100, 2),
        "discount_to_core_pct": round((1 - index) * 100, 1),
        "data_class": "heuristic",
        "provenance": None,
    }


def _real_price_for_zone(
    city_id: str,
    direction: str,
    mid_dist_km: float,
    expected_rise_pct: float,
    horizon_years: int,
) -> dict[str, Any] | None:
    """Return a real-data price index if a circle-rate observation covers this zone.

    Matching logic: find observations whose ``direction_hint`` matches the zone
    direction (exact or adjacent compass point) AND whose
    ``approx_distance_from_core_km`` is within 50% of ``mid_dist_km``.
    Returns None if no match — caller falls back to heuristic.
    """
    store = _get_price_store()
    if store is None:
        return None
    observations = store.get_for_city(city_id)
    if not observations:
        return None

    # Adjacent compass directions for fuzzy matching
    _ADJACENT = {
        "N": {"N", "NE", "NW"},
        "NE": {"NE", "N", "E"},
        "E": {"E", "NE", "SE"},
        "SE": {"SE", "E", "S"},
        "S": {"S", "SE", "SW"},
        "SW": {"SW", "S", "W"},
        "W": {"W", "SW", "NW"},
        "NW": {"NW", "N", "W"},
    }
    adjacent = _ADJACENT.get(direction, {direction})
    tolerance = max(mid_dist_km * 0.5, 3.0)  # km tolerance

    candidates = [
        obs for obs in observations
        if obs.direction_hint in adjacent
        and abs(obs.approx_distance_from_core_km - mid_dist_km) <= tolerance
    ]
    if not candidates:
        return None

    # Use the median price of matching candidates (robust against outliers)
    prices = sorted(obs.value_inr_per_sqft for obs in candidates)
    mid = len(prices) // 2
    current_price = prices[mid] if len(prices) % 2 == 1 else (prices[mid - 1] + prices[mid]) / 2
    current_price = round(current_price)

    projected = round(current_price * (1 + expected_rise_pct / 100.0))
    yrs = max(horizon_years, 1)
    cagr = ((projected / current_price) ** (1.0 / yrs) - 1.0) if current_price > 0 else 0.0

    # Build provenance from the best-confidence candidate. The data_class is the
    # observation's own honesty-gated class (curated for unverified govt data,
    # real only once verified) — never hardcoded to "real".
    best = max(candidates, key=lambda o: o.confidence)
    return {
        "price_index": 1.0,        # observed price is the ground truth; no decay index
        "current_price_inr_per_sqft": current_price,
        "projected_price_inr_per_sqft": projected,
        "implied_price_cagr_pct": round(cagr * 100, 2),
        "discount_to_core_pct": 0.0,  # observed; no synthetic discount
        "data_class": best.data_class,
        "provenance": {
            "source": best.source,
            "source_url": best.source_url,
            "license": best.license,
            "effective_date": best.effective_date.isoformat(),
            "confidence": best.confidence,
            "verification_status": best.verification_status,
            "localities_matched": len(candidates),
            "basis": best.basis,
        },
    }


def city_zones_geojson(city: dict) -> dict[str, Any]:
    """Build a GeoJSON FeatureCollection of current extent + growth zones."""
    lng, lat = city["lng"], city["lat"]
    pred = predict_growth(city)

    cur_area = pred["current_urban_area_sqkm"]
    area5 = pred["milestones"]["area_2026_sqkm"]
    area10 = pred["milestones"]["area_2031_sqkm"]
    r_cur, r5, r10 = _radius_km(cur_area), _radius_km(area5), _radius_km(area10)
    core_price = city["land_price_inr_per_sqft"]["2021"]

    features: list[dict] = []

    extent = _circle(lng, lat, r_cur)
    features.append({
        "type": "Feature",
        "geometry": mapping(extent),
        "properties": {
            "kind": "current_extent",
            "label": f"{city['name']} — built-up extent (2021)",
            "horizon_years": 0,
            "radius_km": round(r_cur, 2),
            "area_sqkm": cur_area,
            "color": "#6B7280",
        },
    })

    for zone in pred["investment_zones"]:
        bearing = _BEARING.get(zone["direction"], 0)
        if zone["horizon_years"] == 5:
            r_in, r_out = r_cur, r5
        else:
            r_in, r_out = r5, r10
        sector = _sector(lng, lat, r_in, r_out, bearing)
        mid_r = (r_in + r_out) / 2.0
        dist = max(mid_r - r_cur, 0.0)

        # Try real circle-rate data first; fall back to heuristic
        real_price = _real_price_for_zone(
            city["id"], zone["direction"], mid_r,
            zone["expected_price_rise_pct"], zone["horizon_years"],
        )
        price = real_price if real_price else _zone_price_index(
            core_price, dist_from_core_km=dist,
            expected_rise_pct=zone["expected_price_rise_pct"],
            horizon_years=zone["horizon_years"],
        )

        features.append({
            "type": "Feature",
            "geometry": mapping(sector),
            "properties": {
                "kind": "growth_zone",
                "zone_id": zone["zone_id"],
                "label": zone["label"],
                "direction": zone["direction"],
                "horizon_years": zone["horizon_years"],
                "investment_score": zone["investment_score"],
                "expected_price_rise_pct": zone["expected_price_rise_pct"],
                "risk_level": zone["risk_level"],
                "recommendation": zone["recommendation"],
                "area_sqkm": _poly_area_km2(sector, lat),
                "color": "#059669" if zone["horizon_years"] == 5 else "#4338CA",
                **price,
            },
        })

    return {
        "type": "FeatureCollection",
        "city_id": city["id"],
        "city_name": city["name"],
        "center": [lng, lat],
        "features": features,
    }


def zone_price_index_table(city: dict) -> dict[str, Any]:
    """Tabular land-price index per growth zone (core = 1.0 baseline).

    A frontend-friendly companion to ``city_zones_geojson`` — same numbers, no
    geometry — powering a "price per zone" panel and answering "how much cheaper
    is the N corridor today, and what's its implied appreciation?".

    Each zone row now carries ``data_class`` (``'real'`` or ``'heuristic'``) and
    a ``provenance`` dict when real circle-rate data is available.
    """
    pred = predict_growth(city)
    cur_area = pred["current_urban_area_sqkm"]
    r_cur = _radius_km(cur_area)
    r5 = _radius_km(pred["milestones"]["area_2026_sqkm"])
    r10 = _radius_km(pred["milestones"]["area_2031_sqkm"])
    core_price = city["land_price_inr_per_sqft"]["2021"]

    rows = []
    for zone in pred["investment_zones"]:
        r_in, r_out = (r_cur, r5) if zone["horizon_years"] == 5 else (r5, r10)
        mid_r = (r_in + r_out) / 2.0
        dist = max(mid_r - r_cur, 0.0)

        # Prefer real circle-rate data; fall back to heuristic
        real_price = _real_price_for_zone(
            city["id"], zone["direction"], mid_r,
            zone["expected_price_rise_pct"], zone["horizon_years"],
        )
        price = real_price if real_price else _zone_price_index(
            core_price, dist_from_core_km=dist,
            expected_rise_pct=zone["expected_price_rise_pct"],
            horizon_years=zone["horizon_years"],
        )

        rows.append({
            "zone_id": zone["zone_id"],
            "label": zone["label"],
            "direction": zone["direction"],
            "horizon_years": zone["horizon_years"],
            "investment_score": zone["investment_score"],
            "risk_level": zone["risk_level"],
            "recommendation": zone["recommendation"],
            "approx_distance_from_core_km": round(dist, 1),
            **price,
        })

    # Cheapest entry point + highest implied appreciation, for quick UI callouts.
    cheapest = min(rows, key=lambda r: r["current_price_inr_per_sqft"]) if rows else None
    hottest = max(rows, key=lambda r: r["implied_price_cagr_pct"]) if rows else None

    # Count zones by honest data_class for transparency. Government circle-rate
    # zones are "curated" (govt guidance, unverified transcription) until verified;
    # only verified observations are "real". Everything else is "heuristic".
    real_count = sum(1 for r in rows if r.get("data_class") == "real")
    curated_count = sum(1 for r in rows if r.get("data_class") == "curated")
    govt_count = real_count + curated_count          # backed by a government source
    heuristic_count = len(rows) - govt_count

    if real_count:
        overall = "real"
    elif curated_count:
        overall = "curated"
    else:
        overall = "heuristic"

    return {
        "city_id": city["id"],
        "city_name": city["name"],
        "core_price_inr_per_sqft": core_price,
        "method": "distance-decay index off the city core, projected by the per-zone growth forecast",
        "zones": rows,
        "cheapest_zone_id": cheapest["zone_id"] if cheapest else None,
        "highest_appreciation_zone_id": hottest["zone_id"] if hottest else None,
        "coverage": {
            "real_zones": real_count,           # verified government data
            "curated_zones": curated_count,     # govt guidance, unverified transcription
            "govt_backed_zones": govt_count,    # real + curated (any government source)
            "heuristic_zones": heuristic_count,
            "total_zones": len(rows),
            "data_class": overall,
        },
    }


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance between two lat/lng points, in kilometres."""
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def nearest_cities(cities: list[dict], lat: float, lng: float,
                   radius_km: float = 400, top: int = 8) -> list[dict[str, Any]]:
    """In-memory KNN by great-circle distance (no PostGIS required)."""
    rows = []
    for c in cities:
        d = haversine_km(lat, lng, c["lat"], c["lng"])
        if d <= radius_km:
            rows.append({
                "id": c["id"], "name": c["name"], "state": c["state"], "tier": c["tier"],
                "growth_phase": c["growth_phase"], "investment_score": c["investment_score"],
                "land_price_2021": c["land_price_inr_per_sqft"]["2021"],
                "lat": c["lat"], "lng": c["lng"],
                "distance_km": round(d, 1),
            })
    rows.sort(key=lambda r: r["distance_km"])
    return rows[:top]


def cities_geojson(cities: list[dict]) -> dict[str, Any]:
    """All cities as a GeoJSON point FeatureCollection."""
    features = [{
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [c["lng"], c["lat"]]},
        "properties": {
            "id": c["id"], "name": c["name"], "state": c["state"], "tier": c["tier"],
            "growth_phase": c["growth_phase"], "investment_score": c["investment_score"],
            "land_price_2021": c["land_price_inr_per_sqft"]["2021"],
        },
    } for c in cities]
    return {"type": "FeatureCollection", "count": len(features), "features": features}


def city_spatial_summary(city: dict) -> dict[str, Any]:
    pred = predict_growth(city)
    cur_area = pred["current_urban_area_sqkm"]
    area5 = pred["milestones"]["area_2026_sqkm"]
    area10 = pred["milestones"]["area_2031_sqkm"]
    return {
        "city_id": city["id"],
        "center": [city["lng"], city["lat"]],
        "current_extent": {"area_sqkm": cur_area, "radius_km": round(_radius_km(cur_area), 2)},
        "zone_5yr": {"area_sqkm": area5, "radius_km": round(_radius_km(area5), 2)},
        "zone_10yr": {"area_sqkm": area10, "radius_km": round(_radius_km(area10), 2)},
        "growth_directions": city.get("growth_directions", []),
        "expansion_ratio_10yr": round(area10 / max(cur_area, 0.1), 2),
    }

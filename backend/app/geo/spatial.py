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


def city_zones_geojson(city: dict) -> dict[str, Any]:
    """Build a GeoJSON FeatureCollection of current extent + growth zones."""
    lng, lat = city["lng"], city["lat"]
    pred = predict_growth(city)

    cur_area = pred["current_urban_area_sqkm"]
    area5 = pred["milestones"]["area_2026_sqkm"]
    area10 = pred["milestones"]["area_2031_sqkm"]
    r_cur, r5, r10 = _radius_km(cur_area), _radius_km(area5), _radius_km(area10)

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
            },
        })

    return {
        "type": "FeatureCollection",
        "city_id": city["id"],
        "city_name": city["name"],
        "center": [lng, lat],
        "features": features,
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

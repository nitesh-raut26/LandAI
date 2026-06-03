from fastapi import APIRouter, HTTPException, Query

from ..data.cities_data import get_all_cities, get_city
from ..geo.db import nearby_cities, spatial_backend_status
from ..geo.spatial import (
    cities_geojson, city_spatial_summary, city_zones_geojson, nearest_cities, zone_price_index_table,
)

router = APIRouter(prefix="/geo", tags=["geo"])


@router.get("/status")
def geo_status():
    """Which spatial backend is active (PostGIS vs in-memory shapely)."""
    return spatial_backend_status()


@router.get("/cities.geojson")
def all_cities_geojson():
    """All cities as a GeoJSON point FeatureCollection."""
    return cities_geojson(get_all_cities())


@router.get("/city/{city_id}/zones.geojson")
def zones_geojson(city_id: str):
    """Growth-zone polygons (current extent + 5yr/10yr sectors) as GeoJSON."""
    city = get_city(city_id)
    if not city:
        raise HTTPException(404, detail=f"City '{city_id}' not found")
    return city_zones_geojson(city)


@router.get("/city/{city_id}/price-index")
def zone_price_index(city_id: str):
    """Zone-level land-price index: per-corridor current price, projected price,
    implied CAGR and discount-to-core (Vision §3.4 — price per zone, not just city)."""
    city = get_city(city_id)
    if not city:
        raise HTTPException(404, detail=f"City '{city_id}' not found")
    return zone_price_index_table(city)


@router.get("/city/{city_id}")
def spatial_summary(city_id: str):
    """Compact spatial summary: extent + zone radii + expansion ratio."""
    city = get_city(city_id)
    if not city:
        raise HTTPException(404, detail=f"City '{city_id}' not found")
    return city_spatial_summary(city)


@router.get("/nearby")
def nearby(
    lat: float = Query(..., ge=-90, le=90, description="Latitude (e.g. user GPS)"),
    lng: float = Query(..., ge=-180, le=180, description="Longitude"),
    radius_km: float = Query(400, ge=10, le=2000),
    top: int = Query(8, ge=1, le=30),
):
    """Nearest cities to a point. Uses PostGIS when attached, else in-memory
    great-circle (haversine) ranking — always works. Powers the GPS 'near you' UI."""
    pg = nearby_cities(lng, lat, radius_km)
    if pg is not None:
        rows, backend = pg[:top], "postgis"
    else:
        rows, backend = nearest_cities(get_all_cities(), lat, lng, radius_km, top), "haversine"
    region = rows[0]["state"] if rows else None
    return {"backend": backend, "count": len(rows), "detected_region": region, "results": rows}

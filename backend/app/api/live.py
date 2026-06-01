"""
Live data API — real, provenance-wrapped intelligence.
=======================================================

Every successful response carries a ``provenance`` block (source, source_url,
license, fetched_at, confidence, freshness_score, legality_note). When a real
source can't be reached the response is an explicit ``available: false``
envelope — never fabricated data.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from ..data.cities_data import get_city
from ..ingestion import config
from ..ingestion.compliance import registry_view
from ..ingestion.pipelines.amenities_pipeline import amenities_for_city, amenities_for_point
from ..ingestion.scrapers.listings_gated import attempt_listing_ingest

router = APIRouter(prefix="/live", tags=["live"])


@router.get("/health")
def live_health():
    return {
        "live_ingestion_enabled": config.LIVE_INGESTION_ENABLED,
        "user_agent": config.USER_AGENT,
        "endpoints": [
            "/api/live/amenities/{city_id}",
            "/api/live/amenities?lat=&lng=",
            "/api/live/sources",
        ],
    }


@router.get("/sources")
def live_sources():
    """Full source registry + a live demonstration that ToS-protected listing
    portals are gated (they return blocked=true, not data)."""
    gate_demo = [attempt_listing_ingest(k) for k in ("99acres", "magicbricks", "housing", "commonfloor")]
    return {"sources": registry_view(), "listing_portals_gate_demo": gate_demo}


@router.get("/amenities/{city_id}")
async def amenities_city(
    city_id: str,
    radius_m: int | None = Query(None, ge=500, le=60000),
    max_pois: int = Query(60, ge=0, le=500),
):
    city = get_city(city_id)
    if city is None:
        raise HTTPException(status_code=404, detail=f"Unknown city '{city_id}'")
    return await amenities_for_city(city, radius_m=radius_m, max_pois=max_pois)


@router.get("/amenities")
async def amenities_point(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_m: int | None = Query(None, ge=500, le=60000),
    max_pois: int = Query(60, ge=0, le=500),
):
    return await amenities_for_point(lat, lng, radius_m=radius_m, max_pois=max_pois)

"""
Amenities pipeline — city/point → Overpass → normalize → enrich → Provenance.

This is the orchestration the API calls. It owns the adapter lifecycle and never
fabricates: if Overpass is unreachable or live ingestion is disabled, it returns
an explicit ``available: false`` envelope rather than fake numbers.
"""
from __future__ import annotations

from .. import config
from ..enrichers.amenities import enrich
from ..normalizers.osm import normalize_elements
from ..provenance import Unavailable
from ..scrapers.overpass import OverpassAdapter
from ...metrics import METRICS

_SRC = "OpenStreetMap (Overpass API)"
_KEY = "osm_overpass"


async def amenities_for_point(
    lat: float,
    lng: float,
    *,
    radius_m: int | None = None,
    name: str | None = None,
    max_pois: int = 60,
) -> dict:
    if not config.LIVE_INGESTION_ENABLED:
        METRICS.incr("ingestion_live_unavailable")
        return Unavailable(
            source=_SRC,
            source_key=_KEY,
            reason="Live ingestion is disabled (LIVE_INGESTION_ENABLED=false).",
        ).model_dump()

    radius = int(radius_m or config.AMENITY_RADIUS_M)
    adapter = OverpassAdapter()
    try:
        elements, prov = await adapter.fetch_amenities(lat, lng, radius_m=radius)
    except Exception as exc:  # network / upstream failure → honest "unavailable"
        METRICS.incr("ingestion_live_unavailable")
        return Unavailable(
            source=_SRC,
            source_key=_KEY,
            reason=f"Overpass fetch failed: {type(exc).__name__}: {exc}",
            legality_note=adapter.policy.legality_note,
        ).model_dump()
    finally:
        await adapter.aclose()

    pois = normalize_elements(elements)
    features = enrich(lat, lng, pois, radius)
    all_pois = features.pop("pois")
    features["poi_sample"] = all_pois[: max(max_pois, 0)]
    features["poi_sample_truncated"] = len(all_pois) > max_pois

    return {
        "available": True,
        "query": {"lat": lat, "lng": lng, "name": name, "radius_m": radius},
        "amenities": features,
        "provenance": prov.model_dump(),
    }


async def amenities_for_city(city: dict, *, radius_m: int | None = None, max_pois: int = 60) -> dict:
    out = await amenities_for_point(
        city["lat"], city["lng"], radius_m=radius_m, name=city.get("name"), max_pois=max_pois
    )
    if out.get("available"):
        out["query"]["city_id"] = city["id"]
        out["query"]["state"] = city.get("state")
    return out

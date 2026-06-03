"""
Data coverage API — real circle-rate coverage statistics.

GET /api/data/coverage              — global coverage stats
GET /api/data/coverage/{city_id}   — per-city zone-level breakdown
POST /api/data/refresh              — trigger re-seed (admin only)
POST /api/data/refresh/{city_id}   — refresh one city (admin only)
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from ..data.cities_data import get_all_cities, get_city
from ..geo.spatial import zone_price_index_table
from ..store_circle_rates import PRICE_STORE

router = APIRouter(prefix="/data", tags=["data-coverage"])


@router.get("/coverage")
async def global_coverage() -> dict[str, Any]:
    """Global circle-rate coverage statistics.

    Returns the fraction of LandAI cities and zones backed by real government
    circle-rate data (🟢 Real) vs the heuristic distance-decay model (🟠 Heuristic).
    """
    stats = PRICE_STORE.coverage_stats()
    cities = get_all_cities()

    # Per-state breakdown
    state_coverage: dict[str, dict] = {}
    for c in cities:
        state = c["state"]
        obs = PRICE_STORE.get_for_city(c["id"])
        if state not in state_coverage:
            state_coverage[state] = {"total": 0, "covered": 0}
        state_coverage[state]["total"] += 1
        if obs:
            state_coverage[state]["covered"] += 1

    return {
        **stats,
        "state_breakdown": {
            s: {
                "total_cities": v["total"],
                "covered_cities": v["covered"],
                "coverage_pct": round(v["covered"] / v["total"] * 100, 1) if v["total"] else 0.0,
            }
            for s, v in sorted(state_coverage.items())
        },
        "data_sources": [
            {
                "source_key": "maharashtra_igr",
                "source": "Maharashtra IGR — Annual Statement of Rates (ASR) 2023-24",
                "license": "GODL-India",
                "source_url": "https://igrmaharashtra.gov.in/english/pages/RRRates.aspx",
                "data_class": "real",
            },
            {
                "source_key": "karnataka_kaveri",
                "source": "Karnataka Kaveri Online Services — Guidance Value 2023-24",
                "license": "GODL-India",
                "source_url": "https://kaverionline.karnataka.gov.in",
                "data_class": "real",
            },
            {
                "source_key": "telangana_igrs",
                "source": "Telangana IGRS — Dharani Guidance Values 2023-24",
                "license": "GODL-India",
                "source_url": "https://registration.telangana.gov.in/guidancevalue.htm",
                "data_class": "real",
            },
        ],
        "honesty_note": (
            "Coverage 🟢 Real means the zone price is sourced from a government-published "
            "guidance value (circle rate). 🟠 Heuristic means the zone price is derived "
            "from a distance-decay formula off the city core price — transparent but not "
            "a real market observation."
        ),
    }


@router.get("/coverage/{city_id}")
async def city_coverage(city_id: str) -> dict[str, Any]:
    """Per-city zone-level coverage breakdown.

    Returns the zone price index table with data_class per zone (real/heuristic)
    and the observations that back each real zone.
    """
    city = get_city(city_id)
    if not city:
        raise HTTPException(status_code=404, detail=f"City '{city_id}' not found")

    observations = PRICE_STORE.get_for_city(city_id)
    obs_list = [o.as_dict() for o in observations]

    zone_table = zone_price_index_table(city)

    return {
        "city_id": city_id,
        "city_name": city["name"],
        "state": city["state"],
        "zone_coverage": zone_table.get("coverage", {}),
        "zones": zone_table.get("zones", []),
        "observations_count": len(observations),
        "observations": obs_list,
        "last_refresh": (
            PRICE_STORE.last_refresh(city_id).isoformat().replace("+00:00", "Z")
            if PRICE_STORE.last_refresh(city_id) else None
        ),
    }


@router.post("/refresh")
async def refresh_all() -> dict[str, Any]:
    """Re-seed the circle-rate store for all cities (admin intent).

    In production, protect this with an admin dependency. Left open for
    development convenience.
    """
    results = PRICE_STORE.seed_all()
    return {
        "status": "ok",
        "cities_refreshed": len(results),
        "total_observations": sum(results.values()),
        "refreshed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


@router.post("/refresh/{city_id}")
async def refresh_city(city_id: str) -> dict[str, Any]:
    """Re-seed circle-rate data for a single city."""
    city = get_city(city_id)
    if not city:
        raise HTTPException(status_code=404, detail=f"City '{city_id}' not found")

    from ..ingestion.scrapers.circle_rates import (
        MaharashtraASRAdapter, KarnatakaKaveriAdapter, TelanganaIGRSAdapter,
    )
    adapters = [MaharashtraASRAdapter(), KarnatakaKaveriAdapter(), TelanganaIGRSAdapter()]
    new_obs = []
    for adapter in adapters:
        try:
            obs = adapter.get_observations(city_id, city["name"], city["state"])
            new_obs.extend(obs)
        except Exception:
            pass

    PRICE_STORE.clear_city(city_id)
    if new_obs:
        PRICE_STORE.put_many(new_obs)

    return {
        "status": "ok",
        "city_id": city_id,
        "city_name": city["name"],
        "observations": len(new_obs),
        "covered": len(new_obs) > 0,
        "refreshed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

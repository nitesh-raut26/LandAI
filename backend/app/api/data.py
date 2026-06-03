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

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from ..data.cities_data import get_all_cities, get_city
from ..geo.spatial import zone_price_index_table
from ..store_circle_rates import PRICE_STORE

router = APIRouter(prefix="/data", tags=["data-coverage"])

# Registered state circle-rate sources (key → published portal).
_SOURCE_REGISTRY = [
    ("maharashtra_igr", "Maharashtra IGR — Annual Statement of Rates (ASR)",
     "https://easr.igrmaharashtra.gov.in/"),
    ("karnataka_kaveri", "Karnataka Kaveri Online Services — Guidance Value",
     "https://kaverionline.karnataka.gov.in"),
    ("telangana_igrs", "Telangana IGRS — Dharani Guidance Values",
     "https://registration.telangana.gov.in/guidancevalue.htm"),
]


def _data_sources() -> list[dict[str, Any]]:
    """Per-source verification status — reflects whether a verified official
    artifact is present (→ real) or the data is still an unverified transcription
    (→ curated). Honest and dynamic: drop in an artifact and this flips to real."""
    from ..ingestion.scrapers.circle_rates.artifact_loader import artifact_status

    out = []
    for key, label, url in _SOURCE_REGISTRY:
        st = artifact_status(key)
        verified = st.get("verified", False)
        out.append({
            "source_key": key,
            "source": st.get("source") or label,
            "license": "GODL-India",
            "source_url": st.get("source_url") or url,
            "verification_status": "source_verified" if verified else "unverified_transcription",
            "data_class": "real" if verified else "curated",
            **({"artifact_sha256": st["artifact_sha256"],
                "source_document": st.get("source_document"),
                "retrieved_at": st.get("retrieved_at")} if verified else {}),
        })
    return out


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
        "data_sources": _data_sources(),
        "honesty_note": (
            "Data class is gated on verifiability, not on source type. 🟢 Real = a "
            "VERIFIED government guidance value (backed by a committed source artifact). "
            "🟡 Curated = a believed-government circle rate whose transcription is NOT yet "
            "verified against the source gazette — honest, not 'real'. 🟠 Heuristic = a "
            "distance-decay estimate off the city core price. Government datasets are "
            "currently 'unverified_transcription'; committing the official gazette extract "
            "(with SHA-256) promotes them to 'real'. See /api/ml/model-info for formulas."
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


def _scrape_live_into_store(city_id: str, city_name: str) -> None:
    """Background worker: live-scrape circle rates and load them (real) into the store."""
    try:
        from ..ingestion.scrapers.circle_rates.maharashtra_live import MaharashtraLiveASRScraper
        obs = MaharashtraLiveASRScraper().fetch_city(city_id, city_name)
        if obs:
            PRICE_STORE.clear_city(city_id)
            PRICE_STORE.put_many(obs)
    except Exception:
        pass


@router.post("/scrape-live/{city_id}")
async def scrape_live(city_id: str, background_tasks: BackgroundTasks) -> dict[str, Any]:
    """Trigger a LIVE headless-browser scrape of the official portal for a city
    (real data → data_class='real', verification='live_fetched'). Runs in the
    background (the browser cascade is slow); results land in the price store.

    Requires Playwright/Chromium in the server environment. For persistence across
    restarts, use ``scripts/scrape_mh_easr.py`` to write a committed artifact."""
    from ..ingestion.scrapers.circle_rates.maharashtra_live import available, CITY_PLANS

    city = get_city(city_id)
    if not city:
        raise HTTPException(status_code=404, detail=f"City '{city_id}' not found")
    if not available():
        raise HTTPException(status_code=503, detail={
            "error": "scraper_unavailable",
            "message": "Playwright/Chromium not installed in this environment. "
                       "pip install playwright && python -m playwright install chromium",
        })
    if city_id not in CITY_PLANS:
        raise HTTPException(status_code=400, detail={
            "error": "no_scrape_plan",
            "message": f"No live-scrape plan for '{city_id}'. Supported: {sorted(CITY_PLANS)}",
        })
    background_tasks.add_task(_scrape_live_into_store, city_id, city["name"])
    return {"status": "scraping", "city_id": city_id,
            "message": "Live scrape started in background. Poll /api/data/coverage/{city_id} for results."}


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

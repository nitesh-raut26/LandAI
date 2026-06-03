from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..data.cities_data import get_city, CITIES
from ..services.prediction_engine import predict_growth, full_analysis
from ..services.city_matcher import find_similar_cities, get_historical_twin, compare_timelines, time_machine

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("/{city_id}")
def city_prediction(city_id: str, horizon: int = Query(15, ge=5, le=25)):
    city = get_city(city_id)
    if not city:
        raise HTTPException(404, detail=f"City '{city_id}' not found")
    return predict_growth(city, horizon)


@router.get("/{city_id}/full")
def city_full_analysis(city_id: str):
    city = get_city(city_id)
    if not city:
        raise HTTPException(404, detail=f"City '{city_id}' not found")
    analysis = full_analysis(city)

    # Attach twin city info
    twin_info = get_historical_twin(city)
    if twin_info:
        twin = twin_info["twin_city"]
        analysis["twin"] = {
            "city_id": twin["id"],
            "city_name": twin["name"],
            "twin_city": twin,
            "lag_years": twin_info["lag_years"],
            "similarity_score": twin_info["similarity_score"],
            "match_reason": twin_info["match_reason"],
            "twin_current_price": twin["land_price_inr_per_sqft"]["2021"],
            "twin_urban_area": twin["urban_area_sqkm"]["2021"],
            "comparison": compare_timelines(city, twin)
        }
    return analysis


@router.get("/{city_id}/similar")
def similar_cities(city_id: str, top: int = Query(5, ge=1, le=10)):
    city = get_city(city_id)
    if not city:
        raise HTTPException(404, detail=f"City '{city_id}' not found")
    results = find_similar_cities(city_id, top)
    return [
        {
            "city_id": r["city"]["id"],
            "name": r["city"]["name"],
            "state": r["city"]["state"],
            "tier": r["city"]["tier"],
            "similarity_score": r["similarity_score"],
            "growth_phase": r["city"]["growth_phase"],
            "investment_score": r["city"]["investment_score"]
        }
        for r in results
    ]


@router.get("/{city_id}/time-machine")
def city_time_machine(city_id: str, horizon: int = Query(15, ge=5, le=25)):
    """Time Machine (Vision §3.6): replay this city's more-developed twin's real
    price trajectory onto its projected future — 'where will it be in N years?'."""
    city = get_city(city_id)
    if not city:
        raise HTTPException(404, detail=f"City '{city_id}' not found")
    tm = time_machine(city, horizon)
    if not tm:
        raise HTTPException(404, detail="No historical twin available for a Time Machine view.")
    return tm


@router.get("/{city_id}/twin")
def city_twin(city_id: str):
    city = get_city(city_id)
    if not city:
        raise HTTPException(404, detail=f"City '{city_id}' not found")
    twin_info = get_historical_twin(city)
    if not twin_info:
        raise HTTPException(404, detail="No historical twin found")
    twin = twin_info["twin_city"]
    return {
        **twin_info,
        "twin_city": twin,
        "comparison": compare_timelines(city, twin)
    }

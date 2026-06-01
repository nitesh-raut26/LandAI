"""
Metered Developer API (v1).
===========================
Requires an API key (``X-API-Key``), enforces the user's daily quota, and stamps
``X-Quota-*`` / ``X-RateLimit-*`` headers on each response. This is the
monetizable surface; the web app's ``/api/*`` endpoints stay open for the free /
demo tier so the UI keeps working without a login.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ..auth.dependencies import require_api_key
from ..auth.models import User
from ..data.cities_data import get_city
from ..ml.price_model import predict_price_growth
from ..services.scoring import compute_score

router = APIRouter(prefix="/v1", tags=["developer-api"])


@router.get("/city/{city_id}")
def v1_city(city_id: str, user: User = Depends(require_api_key)):
    city = get_city(city_id)
    if not city:
        raise HTTPException(404, f"City '{city_id}' not found")
    return {
        "city": {k: city[k] for k in ("id", "name", "state", "tier", "lat", "lng", "growth_phase", "investment_score")},
        "land_price_2021": city["land_price_inr_per_sqft"]["2021"],
        "served_by": "LandAI Developer API v1 (metered)",
    }


@router.get("/ml/{city_id}")
def v1_ml(city_id: str, user: User = Depends(require_api_key)):
    city = get_city(city_id)
    if not city:
        raise HTTPException(404, f"City '{city_id}' not found")
    return predict_price_growth(city)


@router.get("/score/{city_id}")
def v1_score(city_id: str, user: User = Depends(require_api_key)):
    city = get_city(city_id)
    if not city:
        raise HTTPException(404, f"City '{city_id}' not found")
    return compute_score(city)

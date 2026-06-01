from fastapi import APIRouter, HTTPException

from ..data.cities_data import get_city
from ..services.scoring import compute_score

router = APIRouter(prefix="/score", tags=["score"])


@router.get("/{city_id}")
def city_score(city_id: str):
    """Institutional-style investment breakdown: ROI / risk / liquidity / demand /
    future-development sub-scores, a composite, plain-English rationale and the
    XGBoost driver attribution."""
    city = get_city(city_id)
    if not city:
        raise HTTPException(404, detail=f"City '{city_id}' not found")
    return compute_score(city)

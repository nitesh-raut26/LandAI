from fastapi import APIRouter, HTTPException, Query

from ..data.cities_data import get_city
from ..services.scoring import compute_score, personas_public

router = APIRouter(prefix="/score", tags=["score"])


@router.get("/personas")
def list_personas():
    """Investor personas for the UI toggle — each re-weights the same sub-scores
    (Small Investor / Builder / NRI / Balanced). See Vision §3.5."""
    return {"personas": personas_public(), "default": "balanced"}


@router.get("/{city_id}")
def city_score(city_id: str, persona: str = Query("balanced", description="balanced | small | builder | nri")):
    """Institutional-style investment breakdown: ROI / risk / liquidity / demand /
    future-development sub-scores, a composite, plain-English rationale and the
    XGBoost driver attribution. ``persona`` reframes the composite for the buyer
    (Investor Persona Mode) without changing the underlying signals."""
    city = get_city(city_id)
    if not city:
        raise HTTPException(404, detail=f"City '{city_id}' not found")
    return compute_score(city, persona=persona)

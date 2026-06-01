from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..data.cities_data import get_all_cities, get_city, search_cities, get_states

router = APIRouter(prefix="/cities", tags=["cities"])


@router.get("/")
def list_cities(
    q: Optional[str] = Query(None, description="Search by name"),
    state: Optional[str] = Query(None),
    tier: Optional[int] = Query(None, ge=1, le=3)
):
    if q or state or tier is not None:
        return search_cities(q or "", state or "", tier)
    return get_all_cities()


@router.get("/states")
def list_states():
    return get_states()


@router.get("/{city_id}")
def get_city_detail(city_id: str):
    city = get_city(city_id)
    if not city:
        raise HTTPException(status_code=404, detail=f"City '{city_id}' not found")
    return city

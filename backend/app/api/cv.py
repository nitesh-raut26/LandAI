from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from ..cv.urban_growth import growth_metrics, growth_raster_png
from ..data.cities_data import get_city

router = APIRouter(prefix="/cv", tags=["cv"])


@router.get("/{city_id}/metrics")
def cv_metrics(city_id: str):
    """Per-year urban-footprint morphology metrics (area, compactness, fragmentation, growth bearing)."""
    city = get_city(city_id)
    if not city:
        raise HTTPException(404, detail=f"City '{city_id}' not found")
    return growth_metrics(city)


@router.get("/{city_id}/growth-raster.png")
def cv_raster(city_id: str):
    """Colour-coded multi-temporal urban-growth raster (PNG)."""
    city = get_city(city_id)
    if not city:
        raise HTTPException(404, detail=f"City '{city_id}' not found")
    png = growth_raster_png(city)
    return Response(content=png, media_type="image/png",
                    headers={"Cache-Control": "public, max-age=3600"})

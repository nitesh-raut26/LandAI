import time

from fastapi import APIRouter, HTTPException, Query

from ..data.cities_data import get_city
from ..metrics import METRICS
from ..ml.price_model import model_info, predict_price_growth

router = APIRouter(prefix="/ml", tags=["ml"])


@router.get("/model-info")
def ml_model_info():
    """Model card: backend, metrics (train + 5-fold CV R2, RMSE, MAE) and feature importances."""
    return model_info()


@router.get("/price/{city_id}")
def ml_price(city_id: str, horizon: int = Query(10, ge=3, le=20)):
    """XGBoost-predicted land-price CAGR + forward trajectory for a city."""
    city = get_city(city_id)
    if not city:
        raise HTTPException(404, detail=f"City '{city_id}' not found")
    t0 = time.perf_counter()
    result = predict_price_growth(city, horizon)
    METRICS.observe("model_inference", (time.perf_counter() - t0) * 1000)
    return result

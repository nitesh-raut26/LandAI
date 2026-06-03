import time

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..auth.dependencies import require_role
from ..auth.models import User
from ..data.cities_data import get_city
from ..db import get_db
from ..metrics import METRICS
from ..ml import drift as drift_mod
from ..ml import registry as model_registry
from ..ml import scheduler as ml_scheduler
from ..ml.price_model import leakage_report, model_info, predict_price_growth

router = APIRouter(prefix="/ml", tags=["ml"])


@router.get("/model-info")
def ml_model_info():
    """Model card: version, metrics (train + CV R2, RMSE, MAE), importances, leakage audit."""
    return model_info()


@router.get("/leakage-audit")
def ml_leakage_audit():
    """Honest temporal-leakage audit: active vs excluded features and why."""
    return leakage_report()


@router.get("/registry")
def ml_registry(db: Session = Depends(get_db)):
    """Model registry — version, lineage, metrics, leakage audit per model."""
    model_registry.register_if_absent(db)
    return {"models": model_registry.list_models(db)}


@router.get("/registry/{version}")
def ml_registry_version(version: str, db: Session = Depends(get_db)):
    row = model_registry.get_version(db, version)
    if not row:
        raise HTTPException(404, f"Model version '{version}' not found")
    return model_registry.to_dict(row)


@router.post("/registry/{version}/promote")
def ml_registry_promote(version: str, _admin: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    """Promote a model version to production (archives the prior production model).
    Rolling back = promoting an earlier version. **Admin only.**"""
    model_registry.register_if_absent(db)
    row = model_registry.promote(db, version)
    if not row:
        raise HTTPException(404, f"Model version '{version}' not found")
    return {"ok": True, "version": version, "status": row.status, "models": model_registry.list_models(db)}


@router.post("/registry/{version}/archive")
def ml_registry_archive(version: str, _admin: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    """Archive a model version (take it out of rotation). **Admin only.**"""
    row = model_registry.set_status(db, version, "archived")
    if not row:
        raise HTTPException(404, f"Model version '{version}' not found")
    return {"ok": True, "version": version, "status": row.status}


@router.get("/governance")
def ml_governance(db: Session = Depends(get_db)):
    """ML lifecycle governance health: scheduler state + registry summary + the
    last drift self-check. Surfaces that registry/drift jobs actually run (the
    scheduler seeds on startup and recurs when ML_GOVERNANCE_ENABLED is set)."""
    model_registry.register_if_absent(db)
    models = model_registry.list_models(db)
    return {
        "scheduler": ml_scheduler.status(),
        "registry": {
            "total_models": len(models),
            "production": [m["version"] for m in models if m.get("status") == "production"],
            "models": models,
        },
        "drift_baseline": drift_mod.drift_report(),
    }


@router.post("/governance/run")
def ml_governance_run(_admin: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    """Trigger a governance cycle now (register model + drift self-check). **Admin only.**
    Normally the background scheduler drives this; this is the manual lever."""
    return {"ok": True, "report": ml_scheduler.run_governance_cycle(db), "scheduler": ml_scheduler.status()}


@router.get("/drift")
def ml_drift():
    """Feature-drift baseline (PSI). Live PSI needs a production inference stream."""
    return drift_mod.drift_report()


@router.post("/drift")
def ml_drift_sample(sample: list[list[float]] = Body(..., embed=True)):
    """Compute PSI for a supplied batch of feature vectors against the baseline."""
    return drift_mod.drift_report(sample=sample)


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

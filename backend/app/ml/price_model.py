"""
XGBoost Land-Price Growth Model
================================
A *real* trained gradient-boosted regressor (not a heuristic). It learns the
historical land-price CAGR (2010 -> 2021) of every city in the database from
infrastructure / demographic / connectivity features, then projects each city's
land-price trajectory forward.

Design notes
------------
- Trained on ~116 rows, so the model is intentionally small and regularised.
- All quality metrics (train R2, 5-fold CV R2, RMSE, MAE) are reported
  transparently via /api/ml/model-info — we do not hide that this is a compact
  model fit on a compact dataset.
- Per-prediction feature attribution uses XGBoost's built-in TreeSHAP
  (pred_contribs) when XGBoost is present.
- Falls back to scikit-learn's GradientBoostingRegressor if XGBoost cannot be
  imported, so the API never breaks.
"""
from __future__ import annotations

import math
import threading
from typing import Any

import numpy as np

from ..data.cities_data import get_all_cities

# ── optional XGBoost, graceful fallback to scikit-learn ─────────────────────
try:
    import xgboost as xgb
    from xgboost import XGBRegressor
    _HAS_XGB = True
except Exception:  # pragma: no cover
    _HAS_XGB = False

from sklearn.ensemble import GradientBoostingRegressor

FEATURE_NAMES = [
    "tier",
    "log_population_2021",
    "population_cagr_01_21",
    "urban_area_cagr_01_21",
    "population_density",
    "has_railway",
    "has_airport",
    "num_national_highways",
    "has_university",
    "has_medical_college",
    "num_govt_schemes",
    "has_smart_city",
    "dist_to_metro_km",
    "infrastructure_score",
    "connectivity_score",
    "economic_score",
    "growth_phase_rank",
]

_PHASE_RANK = {"emerging": 0, "accelerating": 1, "maturing": 2, "mature": 3}

# Conformal prediction: 1 - alpha = nominal coverage of the prediction interval.
_CONFORMAL_ALPHA = 0.10  # 90% nominal coverage

_XGB_PARAMS = dict(
    n_estimators=180,
    max_depth=3,
    learning_rate=0.06,
    subsample=0.9,
    colsample_bytree=0.85,
    reg_lambda=1.5,
    min_child_weight=2,
    random_state=42,
    objective="reg:squarederror",
)
_GBR_PARAMS = dict(
    n_estimators=180, max_depth=3, learning_rate=0.06, subsample=0.9, random_state=42
)


def _cagr(start: float, end: float, years: int) -> float:
    if start <= 0 or end <= 0 or years <= 0:
        return 0.0
    return (end / start) ** (1.0 / years) - 1.0


def featurize(city: dict) -> list[float]:
    """Build the model feature vector for a single city."""
    pop = city["population"]
    area = city["urban_area_sqkm"]
    infra = city["infrastructure"]
    scores = city["scores"]
    schemes = city.get("government_schemes", [])

    pop21, pop01 = pop["2021"], pop["2001"]
    area21, area01 = area["2021"], area["2001"]

    return [
        float(city["tier"]),
        math.log(max(pop21, 1)),
        _cagr(pop01, pop21, 20),
        _cagr(area01, area21, 20),
        pop21 / max(area21, 0.1),
        1.0 if infra["has_railway"] else 0.0,
        1.0 if infra["has_airport"] else 0.0,
        float(infra["num_national_highways"]),
        1.0 if infra["has_university"] else 0.0,
        1.0 if infra["has_medical_college"] else 0.0,
        float(len(schemes)),
        1.0 if "Smart City" in schemes else 0.0,
        float(city["dist_to_metro_km"]),
        float(scores["infrastructure"]),
        float(scores["connectivity"]),
        float(scores["economic_activity"]),
        float(_PHASE_RANK.get(city["growth_phase"], 1)),
    ]


def _target_cagr(city: dict) -> float:
    """Observed historical land-price CAGR 2010 -> 2021 (11 years) — the label."""
    p = city["land_price_inr_per_sqft"]
    return _cagr(p["2010"], p["2021"], 11)


def _new_estimator():
    if _HAS_XGB:
        return XGBRegressor(**_XGB_PARAMS)
    return GradientBoostingRegressor(**_GBR_PARAMS)


class _ModelBundle:
    """Lazily-trained, thread-safe singleton holding the fitted model."""

    def __init__(self) -> None:
        self.model = None
        self.metrics: dict[str, Any] = {}
        self.importances: list[dict] = []
        self.conformal: dict[str, Any] = {}
        self.backend = "xgboost" if _HAS_XGB else "sklearn-gbr"
        self._lock = threading.Lock()

    def ensure_trained(self) -> None:
        if self.model is not None:
            return
        with self._lock:
            if self.model is None:
                self._train()

    def _train(self) -> None:
        cities = get_all_cities()
        X = np.array([featurize(c) for c in cities], dtype=float)
        y = np.array([_target_cagr(c) for c in cities], dtype=float)

        model = _new_estimator()
        model.fit(X, y)
        preds = model.predict(X)

        ss_res = float(np.sum((y - preds) ** 2))
        ss_tot = float(np.sum((y - y.mean()) ** 2))
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
        rmse = float(np.sqrt(np.mean((y - preds) ** 2)))
        mae = float(np.mean(np.abs(y - preds)))

        imp = np.asarray(getattr(model, "feature_importances_", np.zeros(len(FEATURE_NAMES))))
        order = np.argsort(imp)[::-1]
        self.importances = [
            {"feature": FEATURE_NAMES[i], "importance": round(float(imp[i]), 4)}
            for i in order
        ]
        self.metrics = {
            "backend": self.backend,
            "n_samples": int(len(cities)),
            "n_features": len(FEATURE_NAMES),
            "target": "historical land-price CAGR 2010-2021",
            "train_r2": round(r2, 3),
            "cv_r2_5fold": round(self._cv_r2(X, y), 3),
            "rmse": round(rmse, 4),
            "mae": round(mae, 4),
        }
        self.conformal = self._fit_conformal(X, y)
        self.model = model

    @staticmethod
    def _fit_conformal(X: np.ndarray, y: np.ndarray, alpha: float = _CONFORMAL_ALPHA) -> dict[str, Any]:
        """CV+ split-conformal calibration of the CAGR prediction interval.

        Computes out-of-fold residuals (so all rows calibrate without leaking
        into their own training fold), then takes the conformal quantile
        ``q_hat`` of |residual|. The prediction interval is ``pred ± q_hat`` and
        carries ~``1-alpha`` marginal coverage under exchangeability. With
        n≈116 this is wide and only approximate — reported transparently."""
        try:
            from sklearn.model_selection import KFold, cross_val_predict

            kf = KFold(n_splits=5, shuffle=True, random_state=42)
            oof = cross_val_predict(_new_estimator(), X, y, cv=kf)
            resid = np.abs(y - oof)
            n = len(resid)
            level = min(math.ceil((n + 1) * (1 - alpha)) / n, 1.0)
            q_hat = float(np.quantile(resid, level, method="higher"))
            coverage = float(np.mean(resid <= q_hat))
            return {
                "method": "CV+ split-conformal (5-fold out-of-fold residuals)",
                "alpha": alpha,
                "nominal_coverage": round(1 - alpha, 2),
                "q_hat_cagr": round(q_hat, 4),
                "empirical_oof_coverage": round(coverage, 3),
                "n_calibration": int(n),
                "note": (
                    "Marginal coverage holds under exchangeability. With n≈116 the "
                    "interval is wide and coverage approximate — directional, not a guarantee."
                ),
            }
        except Exception:
            return {}

    @staticmethod
    def _cv_r2(X: np.ndarray, y: np.ndarray) -> float:
        try:
            from sklearn.model_selection import KFold, cross_val_score

            kf = KFold(n_splits=5, shuffle=True, random_state=42)
            scores = cross_val_score(_new_estimator(), X, y, cv=kf, scoring="r2")
            return float(np.mean(scores))
        except Exception:
            return 0.0


_BUNDLE = _ModelBundle()


def model_info() -> dict[str, Any]:
    """Global model card: metrics + feature importances."""
    _BUNDLE.ensure_trained()
    return {
        **_BUNDLE.metrics,
        "conformal": _BUNDLE.conformal,
        "features": FEATURE_NAMES,
        "feature_importances": _BUNDLE.importances,
    }


def _contributions(vec: np.ndarray) -> list[dict] | None:
    """Per-prediction TreeSHAP attribution (XGBoost only)."""
    if not _HAS_XGB:
        return None
    try:
        booster = _BUNDLE.model.get_booster()
        dm = xgb.DMatrix(vec.reshape(1, -1), feature_names=FEATURE_NAMES)
        contribs = booster.predict(dm, pred_contribs=True)[0]  # trailing item = bias
        items = [
            {"feature": FEATURE_NAMES[i], "contribution": round(float(contribs[i]), 5)}
            for i in range(len(FEATURE_NAMES))
        ]
        items.sort(key=lambda d: abs(d["contribution"]), reverse=True)
        return items[:6]
    except Exception:
        return None


def predict_price_growth(city: dict, horizon_years: int = 10) -> dict[str, Any]:
    """Predict forward land-price CAGR + trajectory for one city."""
    _BUNDLE.ensure_trained()
    vec = np.array(featurize(city), dtype=float)
    pred_cagr = float(_BUNDLE.model.predict(vec.reshape(1, -1))[0])
    pred_cagr = max(min(pred_cagr, 0.35), 0.0)  # clamp to a sane band

    current = city["land_price_inr_per_sqft"]["2021"]
    base_year = 2021
    trajectory = [
        {"year": yr, "price_inr_per_sqft": round(current * ((1 + pred_cagr) ** (yr - base_year)))}
        for yr in range(base_year, base_year + horizon_years + 1)
    ]

    # Conformal prediction interval on the CAGR — statistical, not heuristic.
    q = float(_BUNDLE.conformal.get("q_hat_cagr", 0.0))
    cagr_low, cagr_high = max(pred_cagr - q, 0.0), min(pred_cagr + q, 0.5)
    trajectory_interval = [
        {
            "year": yr,
            "low": round(current * ((1 + cagr_low) ** (yr - base_year))),
            "high": round(current * ((1 + cagr_high) ** (yr - base_year))),
        }
        for yr in range(base_year, base_year + horizon_years + 1)
    ]

    return {
        "city_id": city["id"],
        "model_backend": _BUNDLE.backend,
        "predicted_annual_cagr_pct": round(pred_cagr * 100, 2),
        "predicted_cagr_interval_pct": {
            "low": round(cagr_low * 100, 2),
            "high": round(cagr_high * 100, 2),
            "nominal_coverage": _BUNDLE.conformal.get("nominal_coverage"),
            "method": _BUNDLE.conformal.get("method"),
        },
        "current_price_inr_per_sqft": current,
        "projected_price_5yr": trajectory[5]["price_inr_per_sqft"] if len(trajectory) > 5 else trajectory[-1]["price_inr_per_sqft"],
        "projected_price_10yr": trajectory[-1]["price_inr_per_sqft"],
        "projected_price_10yr_interval": {
            "low": trajectory_interval[-1]["low"],
            "high": trajectory_interval[-1]["high"],
        },
        "price_trajectory": trajectory,
        "price_trajectory_interval": trajectory_interval,
        "top_feature_contributions": _contributions(vec),
        "feature_values": dict(zip(FEATURE_NAMES, [round(float(v), 3) for v in vec])),
    }

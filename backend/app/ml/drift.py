"""Feature-drift monitoring (PSI) for the price model.

``compute_psi`` is the standard Population Stability Index — 0 = identical,
<0.1 = stable, 0.1–0.25 = moderate shift, >0.25 = significant drift.

``drift_report`` exposes the training-feature baseline. Live PSI requires a
production inference stream (predictions logged with their feature vectors);
until that exists we report ``status="baseline_only"`` rather than fabricate a
drift number — honest about what is and isn't measured yet.
"""
from __future__ import annotations

from typing import Any

import numpy as np


def compute_psi(expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
    """PSI between a baseline (expected) and a new sample (actual) for one feature."""
    expected = np.asarray(expected, dtype=float)
    actual = np.asarray(actual, dtype=float)
    if expected.size == 0 or actual.size == 0:
        return 0.0
    # Quantile bin edges from the baseline; guard against constant features.
    edges = np.unique(np.quantile(expected, np.linspace(0, 1, bins + 1)))
    if edges.size < 2:
        return 0.0
    edges[0], edges[-1] = -np.inf, np.inf
    e_hist = np.histogram(expected, bins=edges)[0].astype(float)
    a_hist = np.histogram(actual, bins=edges)[0].astype(float)
    eps = 1e-6
    e_pct = np.clip(e_hist / max(e_hist.sum(), 1), eps, None)
    a_pct = np.clip(a_hist / max(a_hist.sum(), 1), eps, None)
    return float(np.sum((a_pct - e_pct) * np.log(a_pct / e_pct)))


def classify(psi: float) -> str:
    if psi < 0.1:
        return "stable"
    if psi < 0.25:
        return "moderate_shift"
    return "significant_drift"


def _baseline_matrix():
    from ..data.cities_data import get_all_cities
    from .price_model import FEATURE_NAMES, featurize

    X = np.array([featurize(c) for c in get_all_cities()], dtype=float)
    return X, FEATURE_NAMES


def drift_report(sample: list[list[float]] | None = None) -> dict[str, Any]:
    """Baseline feature stats, plus live PSI per feature if a sample is supplied."""
    X, names = _baseline_matrix()
    stats = [
        {"feature": n, "mean": round(float(X[:, i].mean()), 4), "std": round(float(X[:, i].std()), 4)}
        for i, n in enumerate(names)
    ]
    out: dict[str, Any] = {
        "method": "Population Stability Index (PSI)",
        "thresholds": {"stable": "<0.1", "moderate_shift": "0.1–0.25", "significant_drift": ">0.25"},
        "baseline_feature_stats": stats,
    }
    if not sample:
        out["status"] = "baseline_only"
        out["note"] = (
            "No live inference stream wired yet — PSI is computed once predictions are "
            "logged with their feature vectors. Provide a sample to compute drift now."
        )
        return out

    arr = np.asarray(sample, dtype=float)
    per_feature = []
    for i, n in enumerate(names):
        if i < arr.shape[1]:
            psi = compute_psi(X[:, i], arr[:, i])
            per_feature.append({"feature": n, "psi": round(psi, 4), "status": classify(psi)})
    worst = max((f["psi"] for f in per_feature), default=0.0)
    out["status"] = classify(worst)
    out["max_psi"] = round(worst, 4)
    out["per_feature"] = per_feature
    return out

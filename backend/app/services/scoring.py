"""
Investment Scoring Engine + Explainability
==========================================
Turns a city's profile into institutional-style sub-scores (ROI, risk,
liquidity, demand, future-development probability) plus a composite, a
plain-English rationale, and the XGBoost driver attribution — so a user can see
*why* a city scores the way it does.
"""
from __future__ import annotations

import math
from typing import Any

from ..ml.price_model import predict_price_growth
from .prediction_engine import _price_cagr


def _roi_score(city: dict) -> float:
    return round(min(_price_cagr(city) / 0.15 * 100, 100), 1)


def _risk_score(city: dict) -> tuple[float, str]:
    s = {"emerging": 70, "accelerating": 52, "maturing": 34, "mature": 22}.get(city.get("growth_phase"), 50)
    if city["tier"] == 3:
        s += 10
    if city["dist_to_metro_km"] > 300:
        s += 8
    elif city["dist_to_metro_km"] > 120:
        s += 4
    if not city["infrastructure"]["has_airport"]:
        s += 5
    s = max(5.0, min(s, 95.0))
    level = "high" if s >= 62 else "medium" if s >= 40 else "low"
    return round(s, 1), level


def _liquidity_score(city: dict) -> float:
    pop = city["population"]["2021"]
    s = min(math.log10(max(pop, 1)) / 7 * 60, 60)
    s += {1: 30, 2: 20, 3: 10}.get(city["tier"], 10)
    if city["dist_to_metro_km"] < 100:
        s += 10
    return round(min(s, 100), 1)


def _demand_score(city: dict) -> float:
    pop = city["population"]
    growth = pop["2021"] / max(pop["2001"], 1) - 1
    s = min(growth * 60, 45) + city["scores"]["economic_activity"] * 0.35
    s += len(city.get("government_schemes", [])) * 4
    return round(min(s, 100), 1)


def _future_dev_probability(city: dict) -> float:
    s = 30 + len(city.get("growth_triggers", [])) * 7
    s += {"emerging": 22, "accelerating": 16, "maturing": 6, "mature": 0}.get(city.get("growth_phase"), 8)
    if city["infrastructure"]["has_airport"]:
        s += 8
    if "Smart City" in city.get("government_schemes", []):
        s += 8
    return round(min(s, 100), 1)


def _rationale(city: dict, sc: dict[str, Any]) -> dict[str, list[str]]:
    infra = city["infrastructure"]
    schemes = city.get("government_schemes", [])
    strengths, watch = [], []

    if infra.get("has_airport"):
        strengths.append("Airport access widens the catchment and lifts connectivity.")
    if infra.get("num_national_highways", 0) >= 2:
        strengths.append(f"{infra['num_national_highways']} national highways form a logistics junction.")
    if "Smart City" in schemes:
        strengths.append("Smart City Mission funding is upgrading urban infrastructure.")
    if city.get("growth_phase") == "emerging":
        strengths.append("Early-stage market — the most upside if growth materialises.")
    if sc["roi_score"] >= 70:
        strengths.append(f"High modelled appreciation (ROI score {sc['roi_score']}/100).")
    if sc["demand_score"] >= 65:
        strengths.append("Strong demand from population and economic growth.")

    if sc["risk_level"] == "high":
        watch.append("High-risk profile — peripheral/early market; verify infra projects actually execute.")
    if city["dist_to_metro_km"] > 300:
        watch.append(f"{city['dist_to_metro_km']} km from the nearest metro reduces liquidity.")
    if not infra.get("has_airport"):
        watch.append("No airport yet — a key future catalyst if one is announced.")
    if city.get("growth_phase") == "mature":
        watch.append("Mature market — stable but limited remaining upside.")

    return {"strengths": strengths[:4], "watch_outs": watch[:3] or ["Standard market risks apply."]}


def compute_score(city: dict) -> dict[str, Any]:
    infra_s = city["scores"]["infrastructure"]
    conn_s = city["scores"]["connectivity"]
    eco_s = city["scores"]["economic_activity"]
    roi = _roi_score(city)
    risk, risk_level = _risk_score(city)
    liquidity = _liquidity_score(city)
    demand = _demand_score(city)
    fdp = _future_dev_probability(city)

    composite = round(
        roi * 0.26 + demand * 0.18 + fdp * 0.16 + infra_s * 0.12
        + conn_s * 0.10 + eco_s * 0.10 + (100 - risk) * 0.08, 1
    )

    sub = {
        "roi_score": roi,
        "risk_score": risk,
        "risk_level": risk_level,
        "liquidity_score": liquidity,
        "demand_score": demand,
        "future_development_probability": fdp,
        "infrastructure_score": infra_s,
        "connectivity_score": conn_s,
        "economic_score": eco_s,
    }

    try:
        drivers = predict_price_growth(city).get("top_feature_contributions")
    except Exception:
        drivers = None

    return {
        "city_id": city["id"],
        "city_name": city["name"],
        "composite_score": composite,
        "headline_investment_score": city.get("investment_score"),
        "sub_scores": sub,
        "rationale": _rationale(city, sub),
        "model_drivers": drivers,
        "recommendation": (
            "Buy Now" if composite >= 75 and risk_level != "high"
            else "Buy Early" if composite >= 62
            else "Watch" if composite >= 48
            else "Hold"
        ),
    }

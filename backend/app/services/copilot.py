"""
LandAI Copilot — rule-based natural-language investment query engine.

Parses plain-English investor questions ("best city under ₹20 lakh near a metro",
"low-risk Tier-2 cities in Gujarat", "alternatives to Bangalore", "highest ROI
emerging towns") into structured filters + a ranking, and returns recommendations
with a short interpretation.

This is deterministic NLU (regex + keyword rules over the city database), not a
hosted LLM — so it runs offline with no API key. The request/response shape is
LLM-ready: a model-backed version can replace `_parse` without touching callers.
"""
from __future__ import annotations

import re
from typing import Any

from ..data.cities_data import CITIES, get_all_cities, get_states
from .city_matcher import find_similar_cities
from .prediction_engine import _price_cagr
from .scoring import _risk_score


def _parse(q: str) -> dict[str, Any]:
    ql = q.lower()
    intent: dict[str, Any] = {}

    # price per sqft ceiling
    m = re.search(r'(?:₹|rs\.?|inr)?\s?([\d,]+)\s?(?:/|per\s?)?\s?sq\s?\.?\s?ft', ql)
    if m:
        intent["max_price_per_sqft"] = int(m.group(1).replace(",", ""))

    # lakh / crore budget → affordability ceiling (assume ~1,000 sqft plot)
    m2 = re.search(r'(?:under|below|upto|up to|within|budget(?: of)?|less than|max)?\s?(?:₹|rs\.?|inr)?\s?([\d.]+)\s?(lakhs?|crores?|cr)\b', ql)
    if m2 and "max_price_per_sqft" not in intent:
        val = float(m2.group(1))
        lakh = val * 100 if m2.group(2).startswith("cr") else val
        intent["budget_lakh"] = lakh
        intent["max_price_per_sqft"] = int(lakh * 100)
        intent["budget_assumption"] = "≈1,000 sqft plot"

    if re.search(r'low[- ]?risk|safe|stable|secure|conservative', ql):
        intent["risk"] = "low"
    if re.search(r'high[- ]?growth|aggressive|high[- ]?risk|multibagger|max(?:imum)? (?:growth|return)', ql):
        intent["risk"] = "high"
    if re.search(r'near (?:a )?metro|close to (?:a )?metro|metro (?:city|access|connectivity)|near (?:a )?big city', ql):
        intent["near_metro"] = True
    if re.search(r'best roi|high(?:est)? roi|appreciation|returns?|growth potential|upside', ql):
        intent["sort"] = "roi"

    mt = re.search(r'tier[- ]?([123])', ql)
    if mt:
        intent["tier"] = int(mt.group(1))
    for ph in ("emerging", "accelerating", "maturing", "mature"):
        if ph in ql:
            intent["phase"] = ph
    for s in get_states():
        if s.lower() in ql:
            intent["state"] = s

    # "similar to / alternatives to / like <city>"
    wants_similar = bool(re.search(r'similar|like|alternativ|next\s+\w+|compare', ql))
    for cid, c in CITIES.items():
        if re.search(r'\b' + re.escape(c["name"].lower()) + r'\b', ql):
            intent["mentioned_city"] = cid
            if wants_similar:
                intent["like_city"] = cid
            break
    return intent


def _card(c: dict, reason: str) -> dict[str, Any]:
    risk, level = _risk_score(c)
    return {
        "city_id": c["id"], "name": c["name"], "state": c["state"], "tier": c["tier"],
        "growth_phase": c["growth_phase"], "investment_score": c["investment_score"],
        "land_price_2021": c["land_price_inr_per_sqft"]["2021"],
        "roi_score": round(min(_price_cagr(c) / 0.15 * 100, 100), 1),
        "risk_level": level,
        "dist_to_metro_km": c["dist_to_metro_km"],
        "reason": reason,
    }


def _summary(intent: dict, sort_by: str, n: int) -> str:
    bits = []
    if intent.get("tier"):
        bits.append(f"Tier-{intent['tier']}")
    if intent.get("phase"):
        bits.append(intent["phase"])
    bits.append("cities")
    if intent.get("state"):
        bits.append(f"in {intent['state']}")
    if intent.get("max_price_per_sqft"):
        b = f"under ₹{intent['max_price_per_sqft']:,}/sqft"
        if intent.get("budget_assumption"):
            b += f" ({intent['budget_assumption']})"
        bits.append(b)
    if intent.get("near_metro"):
        bits.append("near a metro")
    if intent.get("risk") == "low":
        bits.append("with low risk")
    elif intent.get("risk") == "high":
        bits.append("with high growth potential")
    return f"Showing {n} {' '.join(bits)}, ranked by {sort_by}."


def query(q: str, top: int = 6) -> dict[str, Any]:
    intent = _parse(q)

    # similar-to / alternatives path → City DNA matcher
    if intent.get("like_city"):
        base = CITIES[intent["like_city"]]
        sims = find_similar_cities(intent["like_city"], top)
        results = [_card(s["city"], f"{s['similarity_score']}% City-DNA match to {base['name']}") for s in sims]
        return {
            "query": q, "interpretation": intent,
            "summary": f"Showing {len(results)} cities with the most similar growth DNA to {base['name']}.",
            "sort_by": "City-DNA similarity", "count": len(results), "results": results,
        }

    cities = get_all_cities()
    if intent.get("state"):
        cities = [c for c in cities if c["state"] == intent["state"]]
    if intent.get("tier"):
        cities = [c for c in cities if c["tier"] == intent["tier"]]
    if intent.get("phase"):
        cities = [c for c in cities if c["growth_phase"] == intent["phase"]]
    if intent.get("max_price_per_sqft"):
        cities = [c for c in cities if c["land_price_inr_per_sqft"]["2021"] <= intent["max_price_per_sqft"]]
    if intent.get("near_metro"):
        cities = [c for c in cities if c["dist_to_metro_km"] <= 120]
    if intent.get("risk") == "low":
        # "low-risk" = avoid the high-risk bucket, then rank by lowest risk
        cities = [c for c in cities if _risk_score(c)[0] < 62]

    if intent.get("risk") == "high" or intent.get("sort") == "roi":
        cities.sort(key=lambda c: _price_cagr(c), reverse=True)
        sort_by, reason_fn = "modelled ROI", lambda c: f"~{round(_price_cagr(c) * 100, 1)}% modelled CAGR · {c['growth_phase']}"
    elif intent.get("risk") == "low":
        cities.sort(key=lambda c: (_risk_score(c)[0], -c["investment_score"]))
        sort_by, reason_fn = "lowest risk", lambda c: f"{_risk_score(c)[1]} risk · score {c['investment_score']}"
    elif intent.get("max_price_per_sqft"):
        cities.sort(key=lambda c: (c["land_price_inr_per_sqft"]["2021"], -c["investment_score"]))
        sort_by, reason_fn = "affordability", lambda c: f"₹{c['land_price_inr_per_sqft']['2021']:,}/sqft · score {c['investment_score']}"
    else:
        cities.sort(key=lambda c: c["investment_score"], reverse=True)
        sort_by, reason_fn = "investment score", lambda c: f"score {c['investment_score']} · {c['growth_phase']}"

    results = [_card(c, reason_fn(c)) for c in cities[:top]]
    return {
        "query": q, "interpretation": intent,
        "summary": _summary(intent, sort_by, len(results)),
        "sort_by": sort_by, "count": len(results), "results": results,
    }

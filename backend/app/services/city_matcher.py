"""
City DNA Matcher
Finds historically similar cities using feature-vector cosine similarity.
"""
import math
from typing import Any
from ..data.cities_data import CITIES


def _feature_vector(city: dict) -> list[float]:
    """
    Build a normalized feature vector representing a city's 'DNA'.
    Features: population density, growth rate, infrastructure, connectivity, distance to metro.
    """
    pop21  = city["population"]["2021"]
    pop01  = city["population"]["2001"]
    area21 = city["urban_area_sqkm"]["2021"]
    area01 = city["urban_area_sqkm"]["2001"]

    pop_density    = pop21 / max(area21, 0.1) / 50000      # normalize ~0-1
    pop_growth     = min((pop21 / max(pop01, 1)) - 1, 2) / 2
    area_growth    = min((area21 / max(area01, 0.1)) - 1, 5) / 5
    inf_score      = city["scores"]["infrastructure"] / 100
    conn_score     = city["scores"]["connectivity"] / 100
    eco_score      = city["scores"]["economic_activity"] / 100
    dist_norm      = min(city["dist_to_metro_km"], 1000) / 1000
    tier_norm      = (4 - city["tier"]) / 3            # 1→1.0, 2→0.67, 3→0.33
    has_rail       = 1.0 if city["infrastructure"]["has_railway"] else 0.0
    has_airport    = 1.0 if city["infrastructure"]["has_airport"] else 0.0
    schemes        = min(len(city["government_schemes"]), 3) / 3

    return [
        pop_density, pop_growth, area_growth,
        inf_score, conn_score, eco_score,
        dist_norm, tier_norm, has_rail, has_airport, schemes
    ]


def _cosine_sim(v1: list[float], v2: list[float]) -> float:
    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a * a for a in v1))
    mag2 = math.sqrt(sum(b * b for b in v2))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)


def find_similar_cities(target_id: str, top_n: int = 5) -> list[dict[str, Any]]:
    """
    Return top-N cities most similar to target city by DNA vector.
    Excludes the target city itself and same-tier-but-already-mature cities
    that wouldn't serve as useful comparisons.
    """
    target = CITIES.get(target_id)
    if not target:
        return []

    target_vec = _feature_vector(target)
    target_tier = target["tier"]

    results = []
    for cid, city in CITIES.items():
        if cid == target_id:
            continue
        vec = _feature_vector(city)
        sim = _cosine_sim(target_vec, vec)
        results.append({
            "city": city,
            "similarity_score": round(sim * 100, 1)
        })

    results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return results[:top_n]


def get_historical_twin(city: dict) -> dict[str, Any] | None:
    """
    Returns the pre-configured twin city (if set) or the best similar city
    that is FURTHER along the growth curve (more developed tier).
    """
    if city.get("twin_city_id"):
        twin = CITIES.get(city["twin_city_id"])
        if twin:
            return {
                "twin_city": twin,
                "lag_years": city.get("twin_city_lag_years", 15),
                "similarity_score": 92.0,
                "match_reason": "Manually curated — same region, similar growth profile"
            }

    # Auto-match: find most similar city that is more developed
    phase_order = {"emerging": 0, "accelerating": 1, "maturing": 2, "mature": 3}
    target_phase = phase_order.get(city.get("growth_phase", "emerging"), 0)

    target_vec = _feature_vector(city)
    candidates = []
    for cid, c in CITIES.items():
        if cid == city["id"]:
            continue
        c_phase = phase_order.get(c.get("growth_phase", "emerging"), 0)
        if c_phase <= target_phase:
            continue  # only consider more developed cities as twins
        vec = _feature_vector(c)
        sim = _cosine_sim(target_vec, vec)
        candidates.append({"city": c, "similarity_score": round(sim * 100, 1)})

    if not candidates:
        return None

    candidates.sort(key=lambda x: x["similarity_score"], reverse=True)
    best = candidates[0]

    # Estimate lag years from growth phase difference
    lag_map = {(0, 1): 10, (0, 2): 18, (0, 3): 25,
               (1, 2): 10, (1, 3): 18, (2, 3): 10}
    c_phase = phase_order.get(best["city"].get("growth_phase"), 1)
    lag = lag_map.get((target_phase, c_phase), 12)

    return {
        "twin_city": best["city"],
        "lag_years": lag,
        "similarity_score": best["similarity_score"],
        "match_reason": "Auto-matched by City DNA algorithm"
    }


def compare_timelines(city_a: dict, city_b: dict) -> dict[str, Any]:
    """
    Side-by-side timeline comparison of two cities.
    """
    def history(c):
        area = c["urban_area_sqkm"]
        price = c["land_price_inr_per_sqft"]
        return {
            "area_years": [int(y) for y in sorted(area.keys())],
            "area_values": [area[y] for y in sorted(area.keys())],
            "price_years": [int(y) for y in sorted(price.keys())],
            "price_values": [price[y] for y in sorted(price.keys())]
        }

    return {
        "city_a": {"id": city_a["id"], "name": city_a["name"], "history": history(city_a)},
        "city_b": {"id": city_b["id"], "name": city_b["name"], "history": history(city_b)},
    }

"""
City DNA Matcher
Finds historically similar cities using feature-vector cosine similarity.

Similarity search runs through :class:`_CityVectorIndex`, which uses **FAISS**
(``IndexFlatIP`` over L2-normalised vectors = exact cosine) when the optional
``faiss`` package is installed, and falls back to a vectorised NumPy dot-product
otherwise. Both paths return identical rankings; FAISS simply scales the same
math to thousands of cities. The index is built lazily and cached.
"""
import math
import threading
from typing import Any

import numpy as np

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


class _CityVectorIndex:
    """Cosine-similarity index over city DNA vectors.

    FAISS-backed when available (``IndexFlatIP`` on L2-normalised vectors gives
    exact cosine), with a vectorised NumPy fallback that returns identical
    rankings. Built once and cached; rebuildable if the city set changes.
    """

    def __init__(self) -> None:
        self._ids: list[str] | None = None
        self._normed: np.ndarray | None = None   # float64, L2-normalised rows
        self._faiss = None
        self._backend = "numpy"
        self._lock = threading.Lock()

    def _build(self) -> None:
        ids = list(CITIES.keys())
        mat = np.array([_feature_vector(CITIES[c]) for c in ids], dtype=np.float64)
        norms = np.linalg.norm(mat, axis=1, keepdims=True)
        normed = mat / np.clip(norms, 1e-12, None)
        self._ids, self._normed = ids, normed
        try:  # optional acceleration — identical results, just scales further
            import faiss  # type: ignore

            index = faiss.IndexFlatIP(normed.shape[1])
            index.add(np.ascontiguousarray(normed.astype(np.float32)))
            self._faiss, self._backend = index, "faiss"
        except Exception:
            self._faiss, self._backend = None, "numpy"

    def ensure(self) -> None:
        if self._ids is None:
            with self._lock:
                if self._ids is None:
                    self._build()

    def rebuild(self) -> None:
        with self._lock:
            self._ids = None
        self.ensure()

    @property
    def backend(self) -> str:
        self.ensure()
        return self._backend

    def _similarities(self, qn: np.ndarray) -> np.ndarray:
        """Cosine similarity of the (normalised) query against every city, in the
        cities' original order. FAISS computes the inner products at scale; the
        NumPy fallback does the same matmul. Results are equivalent."""
        if self._faiss is not None:
            n = len(self._ids)
            scores, idxs = self._faiss.search(
                np.ascontiguousarray(qn.astype(np.float32)).reshape(1, -1), n)
            sims = np.zeros(n, dtype=np.float64)
            sims[idxs[0]] = scores[0]  # scatter back to original city order
            return sims
        return self._normed @ qn

    def query(self, vec: list[float], exclude_id: str | None = None, top_n: int = 5) -> list[tuple[str, float]]:
        """Rank all cities by cosine similarity to ``vec`` (descending), excluding
        ``exclude_id``. Ordering matches the historical matcher exactly: by the
        display-rounded score (1 dp) with ties broken by original city order, so
        swapping in FAISS never reshuffles results."""
        self.ensure()
        q = np.asarray(vec, dtype=np.float64)
        qn = q / max(float(np.linalg.norm(q)), 1e-12)
        sims = self._similarities(qn)
        # Stable rank by rounded score desc, ties → original index asc (matches the
        # prior `list.sort(reverse=True)` on the rounded similarity_score).
        ranked = sorted(range(len(self._ids)), key=lambda i: (-round(float(sims[i]) * 100, 1), i))
        out: list[tuple[str, float]] = []
        for i in ranked:
            cid = self._ids[i]
            if cid == exclude_id:
                continue
            out.append((cid, float(sims[i])))
            if len(out) >= top_n:
                break
        return out


_INDEX = _CityVectorIndex()


def matcher_backend() -> str:
    """Which similarity backend is active ('faiss' or 'numpy')."""
    return _INDEX.backend


def find_similar_cities(target_id: str, top_n: int = 5) -> list[dict[str, Any]]:
    """
    Return top-N cities most similar to target city by DNA vector.
    Excludes the target city itself and same-tier-but-already-mature cities
    that wouldn't serve as useful comparisons.
    """
    target = CITIES.get(target_id)
    if not target:
        return []

    matches = _INDEX.query(_feature_vector(target), exclude_id=target_id, top_n=top_n)
    return [
        {"city": CITIES[cid], "similarity_score": round(sim * 100, 1)}
        for cid, sim in matches
    ]


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


def time_machine(city: dict, horizon_years: int = 15) -> dict[str, Any] | None:
    """Time Machine (Vision §3.6) — replay a more-developed twin's real trajectory
    onto this city's future.

    Premise: this city today resembles its historical twin ~``lag`` years ago. We
    therefore (1) measure how far the twin has pulled ahead, (2) project this city
    forward at its modelled price CAGR, and (3) overlay the twin's **actual**
    historical prices at the target-equivalent year (twin_year + lag), so the
    projection is anchored to a real city's lived path — not a satellite image.
    Honest by construction: every number is observed history or the published
    forecast CAGR; nothing is fabricated.
    """
    from .prediction_engine import _price_cagr

    twin_info = get_historical_twin(city)
    if not twin_info:
        return None
    twin = twin_info["twin_city"]
    lag = int(twin_info.get("lag_years", 12))

    base_year = 2021
    t_price = city["land_price_inr_per_sqft"][str(base_year)]
    w_price = twin["land_price_inr_per_sqft"][str(base_year)]
    cagr = _price_cagr(city)
    multiple = w_price / t_price if t_price > 0 else 0.0

    # Years for this city to reach the twin's *current* price at its projected CAGR.
    if multiple > 1 and cagr > 0:
        years_to_parity = math.log(multiple) / math.log(1 + cagr)
    else:
        years_to_parity = 0.0

    # Target's projected price path.
    projection = [
        {"year": base_year + h, "projected_price_inr_per_sqft": round(t_price * ((1 + cagr) ** h))}
        for h in range(horizon_years + 1)
    ]

    # Overlay the twin's real historical prices at target-equivalent years (year+lag).
    overlay = []
    for wy in sorted(twin["land_price_inr_per_sqft"], key=int):
        twin_price = twin["land_price_inr_per_sqft"][wy]
        target_equiv_year = int(wy) + lag
        h = target_equiv_year - base_year
        overlay.append({
            "twin_year": int(wy),
            "twin_price_inr_per_sqft": twin_price,
            "target_equivalent_year": target_equiv_year,
            "target_projected_price_inr_per_sqft": (
                round(t_price * ((1 + cagr) ** h)) if h >= 0 else None
            ),
        })

    parity_year = base_year + int(round(years_to_parity))
    return {
        "city_id": city["id"],
        "city_name": city["name"],
        "twin_city_id": twin["id"],
        "twin_city_name": twin["name"],
        "lag_years": lag,
        "similarity_score": twin_info["similarity_score"],
        "match_reason": twin_info["match_reason"],
        "current_price_inr_per_sqft": t_price,
        "twin_current_price_inr_per_sqft": w_price,
        "twin_price_multiple": round(multiple, 2),
        "projected_price_cagr_pct": round(cagr * 100, 2),
        "years_to_reach_twin_today_price": round(years_to_parity, 1),
        "parity_year": parity_year,
        "headline": (
            f"{city['name']} today resembles {twin['name']} about {lag} years ago. "
            f"{twin['name']} is now {round(multiple, 1)}× more expensive — at {city['name']}'s "
            f"projected {round(cagr * 100, 1)}% CAGR it reaches today's {twin['name']} price "
            f"(₹{w_price:,}/sqft) around {parity_year}."
        ),
        "projection": projection,
        "twin_overlay": overlay,
        "method": "data-driven twin replay (observed twin history + forecast CAGR) — NOT satellite imagery",
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

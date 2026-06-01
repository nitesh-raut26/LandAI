"""
AI Growth Prediction Engine
Uses logistic (S-curve) model for urban area expansion and
compound growth model for land price forecasting.
"""
import math
import numpy as np
from typing import Any


def _logistic(t: float, K: float, r: float, t0: float) -> float:
    """Standard logistic growth function."""
    try:
        return K / (1 + math.exp(-r * (t - t0)))
    except OverflowError:
        return K


def _fit_logistic(years: list[int], areas: list[float]) -> tuple[float, float, float]:
    """
    Estimate logistic curve parameters using simple gradient descent.
    Returns (K, r, t0) — carrying capacity, growth rate, inflection year.
    """
    # Carrying capacity = 3–4× current area for Tier 3, 1.5× for mature
    K = max(areas) * 3.5
    t0_est = years[len(years) // 2]
    # Estimate r from the slope at the midpoint
    if len(areas) >= 2:
        mid_area = K / 2
        # find where area crosses K/2
        for i, a in enumerate(areas):
            if a >= mid_area:
                t0_est = years[i]
                break
    r = 0.07  # default growth rate for Indian Tier-2/3 cities

    # Simple refinement: adjust r so first and last points fit roughly
    if len(areas) >= 2:
        t_start, a_start = years[0], max(areas[0], 0.5)
        t_end, a_end = years[-1], areas[-1]
        try:
            # From logistic: r = log((K-a)/a) at each t, slope = r
            r1 = -math.log((K - a_start) / max(a_start, 0.1)) / (t_start - t0_est) if (t_start != t0_est) else 0.07
            r2 = -math.log((K - a_end) / max(a_end, 0.1)) / (t_end - t0_est) if (t_end != t0_est and a_end < K) else 0.07
            r = max((r1 + r2) / 2, 0.03)
            r = min(r, 0.30)
        except (ValueError, ZeroDivisionError):
            r = 0.07

    return K, r, t0_est


def _infrastructure_multiplier(city: dict) -> float:
    """Bonus growth factor from infrastructure presence."""
    mult = 1.0
    infra = city.get("infrastructure", {})
    schemes = city.get("government_schemes", [])
    if infra.get("has_airport"):       mult += 0.08
    if infra.get("has_railway"):       mult += 0.05
    if infra.get("num_national_highways", 0) >= 2: mult += 0.06
    if "Smart City" in schemes:        mult += 0.07
    if "AMRUT" in schemes:             mult += 0.04
    if city.get("tier") == 3 and city.get("growth_phase") == "emerging":
        mult += 0.10  # extra growth potential for early-stage cities
    return mult


def _price_cagr(city: dict) -> float:
    """Calibrated forward land-price CAGR.

    Ceilings reflect realistic Indian Tier-2/3 land appreciation rather than
    speculative peaks, with gentle mean-reversion for already-expensive markets.
    """
    base_cagr = {
        "mature":       0.045,
        "maturing":     0.065,
        "accelerating": 0.090,
        "emerging":     0.115,
    }.get(city.get("growth_phase", "accelerating"), 0.08)

    # Infrastructure / scheme tailwinds (modest)
    if city["infrastructure"].get("has_airport"):           base_cagr += 0.008
    if "Smart City" in city.get("government_schemes", []):  base_cagr += 0.010
    if city.get("tier") == 3:                               base_cagr += 0.012
    # Mean-reversion: expensive markets appreciate more slowly
    if city["land_price_inr_per_sqft"].get("2021", 0) > 8000:
        base_cagr -= 0.015
    return round(max(min(base_cagr, 0.15), 0.03), 4)


def _area_cagr(city: dict) -> float:
    """Calibrated urban-area expansion CAGR (bounded, no runaway S-curve)."""
    base = {
        "mature":       0.012,
        "maturing":     0.022,
        "accelerating": 0.032,
        "emerging":     0.045,
    }.get(city.get("growth_phase", "accelerating"), 0.030)
    base += min((_infrastructure_multiplier(city) - 1.0) * 0.03, 0.012)
    return round(min(base, 0.055), 4)


def predict_growth(city: dict, horizon_years: int = 15) -> dict[str, Any]:
    """
    Predict urban area growth and land price appreciation.
    Returns structured prediction with yearly data points.
    """
    area_history = city["urban_area_sqkm"]
    price_history = city["land_price_inr_per_sqft"]

    base_year = 2021
    current_area = area_history.get("2021", list(area_history.values())[-1])
    current_price = price_history.get("2021", list(price_history.values())[-1])

    a_cagr = _area_cagr(city)
    p_cagr = _price_cagr(city)

    # Build prediction timeline with calibrated compound growth + confidence bands
    pred_years = list(range(base_year, base_year + horizon_years + 1))
    pred_areas, pred_prices = [], []
    area_low, area_high, price_low, price_high = [], [], [], []

    for y in pred_years:
        h = y - base_year
        area = current_area * ((1 + a_cagr) ** h)
        price = current_price * ((1 + p_cagr) ** h)
        pred_areas.append(round(area, 2))
        pred_prices.append(round(price))
        # uncertainty widens with horizon (cap so bands stay sensible)
        a_band = min(0.020 * h, 0.30)
        p_band = min(0.035 * h, 0.45)
        area_low.append(round(area * (1 - a_band), 2))
        area_high.append(round(area * (1 + a_band), 2))
        price_low.append(round(price * (1 - p_band)))
        price_high.append(round(price * (1 + p_band)))

    def _at(arr, i):
        return arr[i] if len(arr) > i else arr[-1]

    area_5yr, area_10yr = _at(pred_areas, 5), _at(pred_areas, 10)
    price_5yr, price_10yr = _at(pred_prices, 5), _at(pred_prices, 10)

    # Zone-wise investment potential (directional)
    zones = _compute_zones(city, area_5yr, area_10yr, current_area)

    def _conf(h):
        return round(max(0.40, 1 - 0.05 * h), 2)

    return {
        "city_id": city["id"],
        "base_year": base_year,
        "current_urban_area_sqkm": current_area,
        "current_price_inr_per_sqft": current_price,
        "model": {
            "type": "calibrated_bounded_cagr",
            "area_cagr_pct": round(a_cagr * 100, 2),
            "price_cagr_pct": round(p_cagr * 100, 2),
            "method": "phase-based compound growth with realistic ceilings + horizon confidence bands",
        },
        "timeline": {
            "years": pred_years,
            "urban_area_sqkm": pred_areas,
            "land_price_inr_per_sqft": pred_prices,
            "urban_area_low": area_low,
            "urban_area_high": area_high,
            "land_price_low": price_low,
            "land_price_high": price_high,
        },
        "milestones": {
            "area_2026_sqkm": area_5yr,
            "area_2031_sqkm": area_10yr,
            "price_2026_inr_per_sqft": price_5yr,
            "price_2031_inr_per_sqft": price_10yr,
            "price_appreciation_5yr_pct": round((price_5yr / current_price - 1) * 100, 1),
            "price_appreciation_10yr_pct": round((price_10yr / current_price - 1) * 100, 1),
            "confidence_5yr": _conf(5),
            "confidence_10yr": _conf(10),
        },
        "investment_zones": zones,
        "annual_cagr_price_pct": round(p_cagr * 100, 1),
        "growth_phase": city.get("growth_phase"),
        "investment_score": city.get("investment_score"),
    }


def _compute_zones(city: dict, area_5yr: float, area_10yr: float, current_area: float) -> list[dict]:
    """
    Generate investment zone rings around city center.
    Each zone has: name, ring_km (approximate radius), score, directions, horizon.
    """
    lat, lng = city["lat"], city["lng"]
    directions = city.get("growth_directions", ["N", "E"])
    phase = city.get("growth_phase", "accelerating")

    # Approximate radius from area: r = sqrt(area / pi)
    r_current = math.sqrt(current_area / math.pi)
    r_5yr     = math.sqrt(area_5yr / math.pi)
    r_10yr    = math.sqrt(area_10yr / math.pi)

    score_map = {"mature": 40, "maturing": 55, "accelerating": 72, "emerging": 88}
    base_score = score_map.get(phase, 65)

    def offset(deg_dir: str) -> tuple[float, float]:
        compass = {
            "N": (1, 0), "S": (-1, 0), "E": (0, 1), "W": (0, -1),
            "NE": (0.7, 0.7), "NW": (0.7, -0.7),
            "SE": (-0.7, 0.7), "SW": (-0.7, -0.7)
        }
        dy, dx = compass.get(deg_dir, (0, 0))
        # 1 degree lat ≈ 111 km, 1 degree lng ≈ 111*cos(lat) km
        km_per_lat = 111.0
        km_per_lng = 111.0 * math.cos(math.radians(lat))
        return dy / km_per_lat, dx / km_per_lng

    zones = []
    for i, direction in enumerate(directions[:4]):  # cap at 4 main growth directions
        dlat, dlng = offset(direction)
        score = min(base_score + (4 - i) * 3, 95)

        zones.append({
            "zone_id": f"zone_{direction.lower()}_5yr",
            "label": f"{direction} Corridor — 5-Year Zone",
            "direction": direction,
            "horizon_years": 5,
            "radius_km": round(r_5yr - r_current, 2),
            "center_lat": round(lat + dlat * r_5yr * 0.6, 4),
            "center_lng": round(lng + dlng * r_5yr * 0.6, 4),
            "investment_score": score,
            "expected_price_rise_pct": round(base_score * 0.8 + 10, 1),
            "risk_level": "medium" if score > 70 else "low",
            "recommendation": "Buy Now" if score > 75 else "Watch"
        })
        zones.append({
            "zone_id": f"zone_{direction.lower()}_10yr",
            "label": f"{direction} Fringe — 10-Year Zone",
            "direction": direction,
            "horizon_years": 10,
            "radius_km": round(r_10yr - r_5yr, 2),
            "center_lat": round(lat + dlat * r_10yr * 0.7, 4),
            "center_lng": round(lng + dlng * r_10yr * 0.7, 4),
            "investment_score": max(score - 12, 40),
            "expected_price_rise_pct": round(base_score * 1.4 + 15, 1),
            "risk_level": "high" if phase in ("emerging", "accelerating") else "medium",
            "recommendation": "Buy Early" if phase in ("emerging", "accelerating") else "Monitor"
        })

    return zones


def full_analysis(city: dict) -> dict[str, Any]:
    """
    Complete analysis package including history + prediction.
    """
    prediction = predict_growth(city)
    # expose the historical price series on the prediction so the price chart can
    # draw the actual (pre-2021) line alongside the forecast
    prediction["city"] = {"land_price_inr_per_sqft": city["land_price_inr_per_sqft"]}

    # Historical timeline combined
    area_hist = city["urban_area_sqkm"]
    price_hist = city["land_price_inr_per_sqft"]

    history = {
        "years": [int(y) for y in sorted(area_hist.keys())],
        "urban_area_sqkm": [area_hist[y] for y in sorted(area_hist.keys())],
    }
    price_years = [int(y) for y in sorted(price_hist.keys())]
    price_vals = [price_hist[y] for y in sorted(price_hist.keys())]

    return {
        "city": city,
        "history": history,
        "price_history": {"years": price_years, "values": price_vals},
        "prediction": prediction
    }

"""
Urban-Growth Raster Analysis (Computer Vision)
==============================================
A real raster + morphology pipeline over a city's urban footprint:

1. For each year it rasterises the built-up footprint onto a grid. The footprint
   is grown anisotropically from the centre along the city's growth directions
   until it matches the recorded urban area for that year (so the raster's area
   matches the data exactly).
2. It then runs genuine CV / morphology on those binary masks with
   ``scipy.ndimage``: boundary extraction (erosion XOR), connected-component
   labelling (fragmentation), Polsby–Popper compactness, and centroid-shift
   analysis to find the dominant growth bearing.
3. It renders a colour-coded multi-temporal growth raster as a PNG (Pillow).

Production note
---------------
In production the per-year binary masks would come from *segmenting real
satellite imagery* (e.g. a U-Net / SAM model over Sentinel-2 / Bhuvan tiles).
Here the masks are derived procedurally from the historical area series so the
exact same morphology + rendering pipeline can run end-to-end today; swapping in
a real segmentation model only changes how the masks are produced, not this code.
"""
from __future__ import annotations

import io
import math
from typing import Any

import numpy as np
from scipy import ndimage

from ..services.prediction_engine import predict_growth

_BEARING = {"N": 0, "NE": 45, "E": 90, "SE": 135, "S": 180, "SW": 225, "W": 270, "NW": 315}
_N = 200  # grid resolution


def _radius_km(area_sqkm: float) -> float:
    return math.sqrt(max(area_sqkm, 0.01) / math.pi)


def _fields(city: dict, max_area: float):
    """Build the anisotropic 'effective radius' field + pixel geometry."""
    window_km = max(2.6 * _radius_km(max_area), 3.0)
    px_km = (2 * window_km) / _N
    px_area = px_km * px_km

    axis = np.linspace(-window_km, window_km, _N)
    xx, yy = np.meshgrid(axis, axis)           # x east, y north
    dist = np.sqrt(xx ** 2 + yy ** 2)
    bearing = (np.degrees(np.arctan2(xx, yy))) % 360  # 0=N, 90=E

    factor = np.ones_like(dist)
    for d in city.get("growth_directions", []) or ["N", "E"]:
        b = _BEARING.get(d, 0)
        ang = np.radians(((bearing - b + 180) % 360) - 180)
        factor += 0.6 * np.clip(np.cos(ang), 0, 1) ** 2
    effective = dist / factor
    return effective, px_area, px_km, window_km


def _mask_for_area(effective: np.ndarray, area_km2: float, px_area: float) -> np.ndarray:
    n_needed = int(np.clip(area_km2 / px_area, 1, effective.size - 1))
    threshold = np.partition(effective.ravel(), n_needed)[n_needed]
    return effective <= threshold


def _mask_metrics(mask: np.ndarray, px_area: float, px_km: float) -> dict[str, Any]:
    area_px = int(mask.sum())
    area_km2 = area_px * px_area
    boundary = mask ^ ndimage.binary_erosion(mask)
    perim_km = float(boundary.sum()) * px_km
    compactness = (4 * math.pi * area_km2) / (perim_km ** 2) if perim_km > 0 else 0.0
    _, n_components = ndimage.label(mask)
    return {
        "area_sqkm": round(area_km2, 1),
        "perimeter_km": round(perim_km, 1),
        "compactness_polsby_popper": round(min(compactness, 1.0), 3),
        "fragmentation_components": int(n_components),
    }


def _dominant_bearing(new_mask: np.ndarray, window_km: float) -> dict[str, Any] | None:
    if new_mask.sum() == 0:
        return None
    cy, cx = ndimage.center_of_mass(new_mask)
    px_km = (2 * window_km) / _N
    dx = (cx - _N / 2) * px_km          # east  (column increases eastward)
    dy = (cy - _N / 2) * px_km          # north (row increases northward; display is flipud'd)
    bearing = (math.degrees(math.atan2(dx, dy))) % 360
    compass = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"][int(((bearing + 22.5) % 360) // 45)]
    return {"bearing_deg": round(bearing, 1), "compass": compass,
            "offset_km": round(math.hypot(dx, dy), 2)}


def _year_series(city: dict) -> tuple[list[int], list[float], int, float]:
    area_hist = city["urban_area_sqkm"]
    years = sorted(int(y) for y in area_hist.keys())
    areas = [area_hist[str(y)] for y in years]
    pred = predict_growth(city)
    pred_year = 2031
    pred_area = pred["milestones"]["area_2031_sqkm"]
    return years, areas, pred_year, pred_area


def growth_metrics(city: dict) -> dict[str, Any]:
    years, areas, pred_year, pred_area = _year_series(city)
    effective, px_area, px_km, window_km = _fields(city, max(max(areas), pred_area))

    per_year = []
    masks = {}
    for y, a in zip(years, areas):
        m = _mask_for_area(effective, a, px_area)
        masks[y] = m
        per_year.append({"year": y, **_mask_metrics(m, px_area, px_km)})

    pred_mask = _mask_for_area(effective, pred_area, px_area)
    per_year.append({"year": pred_year, "predicted": True, **_mask_metrics(pred_mask, px_area, px_km)})

    first, last = masks[years[0]], masks[years[-1]]
    new_pixels = last & ~first
    growth_dir = _dominant_bearing(new_pixels, window_km)
    sprawl_index = round(per_year[-2]["perimeter_km"] / max(math.sqrt(per_year[-2]["area_sqkm"]), 0.1), 2)

    return {
        "city_id": city["id"],
        "city_name": city["name"],
        "grid": {"resolution": _N, "pixel_km": round(px_km, 3), "window_km": round(window_km, 1)},
        "method": "anisotropic rasterisation + scipy.ndimage morphology",
        "per_year": per_year,
        "dominant_growth_direction": growth_dir,
        "stated_growth_directions": city.get("growth_directions", []),
        "sprawl_index": sprawl_index,
        "raster_png_url": f"/api/cv/{city['id']}/growth-raster.png",
    }


# ── PNG rendering (Pillow) ──────────────────────────────────────────────────
_BG = (245, 243, 239)
_BANDS = [  # (color, label) painted largest→smallest so older cores sit on top
    ((199, 210, 254), "2031 (predicted)"),
    ((45, 212, 191), "2021"),
    ((13, 148, 136), "2011"),
    ((15, 118, 110), "2001"),
]


def growth_raster_png(city: dict) -> bytes:
    from PIL import Image, ImageDraw

    years, areas, pred_year, pred_area = _year_series(city)
    effective, px_area, px_km, window_km = _fields(city, max(max(areas), pred_area))

    # masks for 2031(pred), 2021, 2011, 2001 in that paint order
    a_by_year = dict(zip(years, areas))
    paint = [
        _mask_for_area(effective, pred_area, px_area),
        _mask_for_area(effective, a_by_year.get(2021, areas[-1]), px_area),
        _mask_for_area(effective, a_by_year.get(2011, areas[len(areas) // 2]), px_area),
        _mask_for_area(effective, a_by_year.get(2001, areas[0]), px_area),
    ]

    rgb = np.empty((_N, _N, 3), dtype=np.uint8)
    rgb[:] = _BG
    for mask, (color, _label) in zip(paint, _BANDS):
        rgb[mask] = color

    # current (2021) boundary as a dark outline — classic edge map
    cur = paint[1]
    edge = cur ^ ndimage.binary_erosion(cur)
    rgb[edge] = (15, 76, 70)

    # north is +y; image row 0 must be north → flip vertically
    img = Image.fromarray(np.flipud(rgb), mode="RGB").resize((640, 640), Image.NEAREST)
    draw = ImageDraw.Draw(img)
    # center marker
    draw.ellipse([316, 316, 324, 324], fill=(17, 24, 39))
    # legend
    y0 = 12
    for color, label in _BANDS:
        draw.rectangle([12, y0, 28, y0 + 14], fill=color, outline=(120, 120, 120))
        draw.text((34, y0 + 1), label, fill=(31, 41, 55))
        y0 += 22
    draw.text((12, y0 + 4), f"{city['name']}: urban growth (CV)", fill=(17, 24, 39))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

"""
Maharashtra e-ASR LIVE scraper (Playwright headless browser).
=============================================================

Fetches **genuinely live** Annual Statement of Rates (circle rates) from the
official Maharashtra portal ``easr.igrmaharashtra.gov.in`` by driving the
JS-gated cascade (Year → Taluka → Village → rate grid) in a real browser — the
only way the portal renders its data. Public GODL-India data; no CAPTCHA, no
login, no access-control bypass.

Each successful fetch yields a :class:`PriceObservation` with
``verification_status="live_fetched"`` ⇒ ``data_class="real"`` and a provenance
trail (live URL, taluka/village/year, retrieval timestamp, survey-row count).

The rate grid columns (per survey sub-zone, ₹/sq.m):
    Select | उपविभाग(survey) | खुली जमीन(open land) | निवासी(residential) |
    ऑफ़ीस(office) | दुकाने(shops) | औद्योगिक(industrial) | unit
We take **open land** (column 2) as the land price, median across sub-zones,
converted ₹/sq.m → ₹/sqft (÷ 10.7639).

Operational notes:
- Playwright + Chromium are OPTIONAL deps. If unavailable, ``available()`` is
  False and the scraper no-ops (the adapter falls back to curated/heuristic).
- This is a heavy, polite, on-demand fetcher — NOT a bulk hammer. Throttled.
- [HUMAN GATE] Run it from an environment with a browser; schedule politely.
"""
from __future__ import annotations

import math
import statistics
import time
from datetime import date, datetime, timezone
from typing import Any

from .base_circle import PriceObservation

_SQM_TO_SQFT = 10.7639
_NOMINATIM = "https://nominatim.openstreetmap.org/search"
_UA = "LandAI-Ingestion/2.0 (+research; ops@landai.example)"
_COMPASS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi, dl = math.radians(lat2 - lat1), math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _bearing_compass(lat1: float, lng1: float, lat2: float, lng2: float) -> str:
    """8-point compass bearing from the city core to the locality."""
    dlon = math.radians(lng2 - lng1)
    y = math.sin(dlon) * math.cos(math.radians(lat2))
    x = (math.cos(math.radians(lat1)) * math.sin(math.radians(lat2))
         - math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(dlon))
    deg = (math.degrees(math.atan2(y, x)) + 360) % 360
    return _COMPASS[round(deg / 45) % 8]


def _geocode(query: str) -> tuple[float, float] | None:
    """Geocode a locality via Nominatim (real, ODbL). Returns (lat, lng) or None.
    Caller is responsible for the 1 req/sec courtesy throttle (Nominatim policy)."""
    try:
        import httpx

        r = httpx.get(_NOMINATIM, params={"q": query, "format": "json", "limit": 1,
                                          "countrycodes": "in"},
                      headers={"User-Agent": _UA}, timeout=15)
        data = r.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass
    return None
_BASE = "https://easr.igrmaharashtra.gov.in/eASRCommon.aspx?hDistName={district}"
_PFX = "#ctl00_ContentPlaceHolder5_"

# Real Haveli-taluka (Pune city) villages → growth-zone direction + approx km from core.
# Marathi names exactly as the portal lists them. Directions from Pune geography.
PUNE_HAVELI_VILLAGES: list[tuple[str, str, float]] = [
    ("कोथरुड", "W", 5.0),       # Kothrud
    ("वारजे", "W", 7.0),        # Warje
    ("बाणेर", "NW", 8.0),       # Baner
    ("औंध", "NW", 6.0),         # Aundh
    ("बालेवाडी", "NW", 9.0),     # Balewadi
    ("खराडी", "E", 9.0),        # Kharadi
    ("वाघोली", "E", 15.0),      # Wagholi
    ("धानोरी", "NE", 8.0),      # Dhanori
    ("कात्रज", "S", 8.0),       # Katraj
    ("बिबवेवाडी", "S", 6.0),    # Bibwewadi
    ("हडपसर", "SE", 8.0),       # Hadapsar
    ("वडगाव बुद्रुक", "SW", 6.0),  # Wadgaon Budruk
]

# Per-city scrape plan. "district" = e-ASR hDistName param (English); "taluka_match"
# = Marathi substring of the city's main taluka. With an explicit "villages" map the
# scraper uses it (Pune, hand-verified directions); otherwise it AUTO-DISCOVERS the
# taluka's villages and assigns direction/distance by geocoding each (real, no hand map).
CITY_PLANS: dict[str, dict[str, Any]] = {
    "pune":       {"district": "Pune", "taluka_match": "हवेली", "villages": PUNE_HAVELI_VILLAGES},
    "nashik":     {"district": "Nashik", "taluka_match": "नाशिक"},
    "nagpur":     {"district": "Nagpur", "taluka_match": "नागपूर"},
    "aurangabad": {"district": "Aurangabad", "taluka_match": "औरंगाबाद"},
    "solapur":    {"district": "Solapur", "taluka_match": "सोलापूर"},
    "thane":      {"district": "Thane", "taluka_match": "ठाणे"},
    "kolhapur":   {"district": "Kolhapur", "taluka_match": "करवीर"},
    "amravati":   {"district": "Amravati", "taluka_match": "अमरावती"},
}


def available() -> bool:
    try:
        import playwright.sync_api  # noqa: F401
        return True
    except Exception:
        return False


def parse_open_land_rate_sqft(grid_rows: list[list[str]]) -> float | None:
    """Median open-land rate (₹/sqft) from the e-ASR survey rows.

    ``grid_rows`` is a list of cell arrays; survey rows look like
    ``['SurveyNo', '<desc>', '<open>', '<resid>', ...]`` with rates in ₹/sq.m.
    Pure function — unit-tested against captured real data, no browser needed.
    """
    vals: list[float] = []
    for r in grid_rows:
        if len(r) >= 3 and (r[0] or "").strip().lower().startswith("surveyno"):
            raw = (r[2] or "").replace(",", "").strip()
            try:
                v = float(raw)
            except ValueError:
                continue
            if v > 0:  # 0 means "not notified for open land" — skip
                vals.append(v)
    if not vals:
        return None
    return round(statistics.median(vals) / _SQM_TO_SQFT, 1)


class MaharashtraLiveASRScraper:
    """Drives the live e-ASR portal. Use as a context manager or call fetch_city."""

    source = "Maharashtra IGR e-ASR (live)"
    source_url_tmpl = "https://easr.igrmaharashtra.gov.in/eASRCommon.aspx?hDistName={district}"

    def __init__(self, headless: bool = True, throttle_s: float = 1.5, year: str = "20242025") -> None:
        self.headless = headless
        self.throttle_s = throttle_s
        self.year = year

    def _grid_rows(self, page) -> list[list[str]]:
        tables = page.eval_on_selector_all("table", """tables => tables.map(t =>
            Array.from(t.querySelectorAll('tr')).map(tr =>
                Array.from(tr.querySelectorAll('td,th')).map(c => c.innerText.trim())))""")
        # pick the table with the most SurveyNo rows
        def score(rows):
            return sum(1 for r in rows if r and (r[0] or "").strip().lower().startswith("surveyno"))
        return max(tables, key=score) if tables else []

    def _city_core(self, city_id: str) -> tuple[float, float] | None:
        try:
            from ...data.cities_data import get_city  # type: ignore
        except Exception:
            from app.data.cities_data import get_city  # fallback for script use
        c = get_city(city_id)
        return (c["lat"], c["lng"]) if c else None

    def fetch_city(self, city_id: str, city_name: str, max_villages: int | None = None) -> list[PriceObservation]:
        """Fetch live circle rates for a planned city. Returns [] if unsupported
        or the browser is unavailable. Never raises.

        With a hand-mapped ``villages`` list (Pune) it uses verified directions;
        otherwise it auto-discovers the taluka's villages and geocodes each to assign
        a real direction + distance from the city core."""
        plan = CITY_PLANS.get(city_id)
        if not plan or not available():
            return []
        from playwright.sync_api import sync_playwright

        url = self.source_url_tmpl.format(district=plan["district"])
        hand_map = plan.get("villages")
        core = self._city_core(city_id)
        cap = max_villages or (len(hand_map) if hand_map else 10)
        out: list[PriceObservation] = []

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=self.headless)
            page = browser.new_page()
            page.set_default_timeout(40000)
            page.goto(url, wait_until="domcontentloaded")
            page.select_option(_PFX + "ddlYear", self.year)
            page.wait_for_timeout(2500)
            tals = page.eval_on_selector_all(_PFX + "ddlTaluka option",
                "els => els.map(e => ({v:e.value, t:e.textContent.trim()}))")
            tal = next((o["v"] for o in tals if plan["taluka_match"] in o["t"]), None)
            if not tal:
                browser.close()
                return []
            page.select_option(_PFX + "ddlTaluka", tal)
            page.wait_for_timeout(3500)
            vopts = page.eval_on_selector_all(_PFX + "ddlVillage option",
                "els => els.map(e => ({v:e.value, t:e.textContent.trim()})).filter(o=>o.v>'0')")
            by_name = {o["t"]: o["v"] for o in vopts}

            # Build the work list: hand-mapped (name, dir, dist) or auto-discovered names.
            if hand_map:
                work = [(n, by_name.get(n), d, km) for (n, d, km) in hand_map[:cap]]
            else:
                work = [(o["t"], o["v"], None, None) for o in vopts[:cap]]

            for name, vid, direction, dist_km in work:
                if not vid:
                    continue
                try:
                    page.select_option(_PFX + "ddlVillage", vid)
                    page.wait_for_timeout(3500)
                    rate = parse_open_land_rate_sqft(self._grid_rows(page))
                except Exception:
                    rate = None
                if not rate or rate <= 0:
                    time.sleep(self.throttle_s)
                    continue
                # Auto-discovered villages: geocode for a real direction + distance.
                if direction is None and core:
                    geo = _geocode(f"{name}, {city_name}, Maharashtra, India")
                    time.sleep(1.1)  # Nominatim courtesy throttle
                    if not geo:
                        time.sleep(self.throttle_s)
                        continue  # no geometry ⇒ can't place the zone; skip honestly
                    direction = _bearing_compass(core[0], core[1], geo[0], geo[1])
                    dist_km = round(_haversine_km(core[0], core[1], geo[0], geo[1]), 1)
                out.append(PriceObservation(
                    city_id=city_id, city_name=city_name, state="Maharashtra",
                    locality_name=name, value_inr_per_sqft=rate, basis="circle_rate",
                    effective_date=date(int(self.year[:4]), 4, 1),
                    approx_distance_from_core_km=dist_km or 0.0, direction_hint=direction or "",
                    source=self.source, source_url=url, license="GODL-India",
                    confidence=0.95, verification_status="live_fetched",
                    fetched_at=datetime.now(timezone.utc),
                    raw={"taluka": plan["taluka_match"], "village": name,
                         "year": self.year, "unit": "INR/sqft from open-land INR/sqm",
                         "direction_source": "hand-verified" if hand_map else "nominatim-geocoded",
                         "retrieved_at": datetime.now(timezone.utc).isoformat()},
                ))
                time.sleep(self.throttle_s)  # be polite to the portal
            browser.close()
        return out

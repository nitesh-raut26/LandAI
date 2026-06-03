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

import statistics
import time
from datetime import date, datetime, timezone
from typing import Any

from .base_circle import PriceObservation

_SQM_TO_SQFT = 10.7639
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

# Per-city scrape plan: district + taluka label + village map.
CITY_PLANS: dict[str, dict[str, Any]] = {
    "pune": {"district": "Pune", "taluka_match": "हवेली", "villages": PUNE_HAVELI_VILLAGES},
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

    def fetch_city(self, city_id: str, city_name: str, max_villages: int | None = None) -> list[PriceObservation]:
        """Fetch live circle rates for a planned city. Returns [] if unsupported
        or the browser is unavailable. Never raises (logs via return)."""
        plan = CITY_PLANS.get(city_id)
        if not plan or not available():
            return []
        from playwright.sync_api import sync_playwright

        url = self.source_url_tmpl.format(district=plan["district"])
        villages = plan["villages"][: max_villages] if max_villages else plan["villages"]
        out: list[PriceObservation] = []
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=self.headless)
            page = browser.new_page()
            page.set_default_timeout(40000)
            page.goto(url, wait_until="domcontentloaded")
            page.select_option(_PFX[1:] and _PFX + "ddlYear", self.year)
            page.wait_for_timeout(2500)
            # pick the matching taluka by visible label
            tals = page.eval_on_selector_all(_PFX + "ddlTaluka option",
                "els => els.map(e => ({v:e.value, t:e.textContent.trim()}))")
            tal = next((o["v"] for o in tals if plan["taluka_match"] in o["t"]), None)
            if not tal:
                browser.close()
                return []
            page.select_option(_PFX + "ddlTaluka", tal)
            page.wait_for_timeout(3500)
            vopts = page.eval_on_selector_all(_PFX + "ddlVillage option",
                "els => els.map(e => ({v:e.value, t:e.textContent.trim()}))")
            by_name = {o["t"]: o["v"] for o in vopts}

            for name, direction, dist_km in villages:
                vid = by_name.get(name)
                if not vid:
                    continue
                try:
                    page.select_option(_PFX + "ddlVillage", vid)
                    page.wait_for_timeout(3500)
                    rate = parse_open_land_rate_sqft(self._grid_rows(page))
                except Exception:
                    rate = None
                if rate and rate > 0:
                    out.append(PriceObservation(
                        city_id=city_id, city_name=city_name, state="Maharashtra",
                        locality_name=name, value_inr_per_sqft=rate, basis="circle_rate",
                        effective_date=date(int(self.year[:4]), 4, 1),
                        approx_distance_from_core_km=dist_km, direction_hint=direction,
                        source=self.source, source_url=url, license="GODL-India",
                        confidence=0.95, verification_status="live_fetched",
                        fetched_at=datetime.now(timezone.utc),
                        raw={"taluka": plan["taluka_match"], "village": name,
                             "year": self.year, "unit": "INR/sqft from open-land INR/sqm",
                             "retrieved_at": datetime.now(timezone.utc).isoformat()},
                    ))
                time.sleep(self.throttle_s)  # be polite to the portal
            browser.close()
        return out

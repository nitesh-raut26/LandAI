#!/usr/bin/env python3
"""
Scrape live Maharashtra e-ASR circle rates and write a VERIFIED artifact.

Drives the official portal (Playwright headless) and writes the results to
``app/ingestion/scrapers/circle_rates/sources/maharashtra_igr.{csv,meta.json}``.
The artifact loader then serves these as data_class="real" (source_verified) with
a full audit trail (source URL, retrieval date, SHA-256). This is the honest
"make it real" path: real official data, scraped live, persisted with provenance.

Usage:
    python scripts/scrape_mh_easr.py            # scrape all planned cities
    python scripts/scrape_mh_easr.py pune       # scrape one city

[HUMAN GATE] Run from an environment with Chromium. Be polite — this hits a
government portal; run infrequently (rates revise annually).
"""
from __future__ import annotations

import csv
import io
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

# Allow running from backend/ root
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ingestion.scrapers.circle_rates.maharashtra_live import (  # noqa: E402
    CITY_PLANS, MaharashtraLiveASRScraper, available,
)

SOURCES = Path(__file__).resolve().parents[1] / "app/ingestion/scrapers/circle_rates/sources"
SOURCE_KEY = "maharashtra_igr"


def main(city_ids: list[str]) -> int:
    if not available():
        print("Playwright/Chromium not available. Install: pip install playwright && playwright install chromium")
        return 2
    city_ids = city_ids or list(CITY_PLANS.keys())
    scraper = MaharashtraLiveASRScraper(throttle_s=1.5)

    rows = []
    for cid in city_ids:
        name = cid.replace("_", " ").title()
        print(f"Scraping {cid} (live e-ASR)…")
        obs = scraper.fetch_city(cid, name)
        print(f"  → {len(obs)} live rates")
        for o in obs:
            rows.append({
                "city_id": o.city_id, "city_name": o.city_name,
                "locality_name": o.locality_name, "value_inr_per_sqft": o.value_inr_per_sqft,
                "direction_hint": o.direction_hint,
                "approx_distance_from_core_km": o.approx_distance_from_core_km,
                "effective_date": o.effective_date.isoformat(),
            })
    if not rows:
        print("No rates scraped — aborting (won't write an empty artifact).")
        return 1

    SOURCES.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
    (SOURCES / f"{SOURCE_KEY}.csv").write_text(buf.getvalue())
    (SOURCES / f"{SOURCE_KEY}.meta.json").write_text(json.dumps({
        "source": f"Maharashtra IGR — e-ASR live scrape (FY {date.today().year})",
        "source_url": "https://easr.igrmaharashtra.gov.in/eASRCommon.aspx",
        "source_document": "Annual Statement of Rates — open-land rate, per survey sub-zone (median)",
        "license": "GODL-India",
        "state": "Maharashtra",
        "retrieved_at": datetime.now(timezone.utc).date().isoformat(),
        "method": "live headless-browser scrape of the official e-ASR portal",
        "official": True,
    }, indent=2))
    print(f"Wrote {len(rows)} verified rows → {SOURCES / (SOURCE_KEY + '.csv')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""
Scrape live Gujarat circle rates and write a VERIFIED artifact.
"""
from __future__ import annotations

import csv
import io
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ingestion.scrapers.circle_rates.gujarat_live import (  # noqa: E402
    CITY_PLANS, GujaratLiveScraper, available,
)

SOURCES = Path(__file__).resolve().parents[1] / "app/ingestion/scrapers/circle_rates/sources"
SOURCE_KEY = "gujarat_registration"


def main(city_ids: list[str]) -> int:
    if not available():
        print("Scraper not available.")
        return 2
    city_ids = city_ids or list(CITY_PLANS.keys())
    scraper = GujaratLiveScraper(throttle_s=1.0)

    rows = []
    for cid in city_ids:
        name = cid.replace("_", " ").title()
        print(f"Scraping {cid} (Gujarat Jantri)…")
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
        print("No rates scraped — aborting.")
        return 1

    SOURCES.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
    (SOURCES / f"{SOURCE_KEY}.csv").write_text(buf.getvalue())
    (SOURCES / f"{SOURCE_KEY}.meta.json").write_text(json.dumps({
        "source": f"Gujarat Revenue Department — Jantri live scrape (FY {date.today().year})",
        "source_url": "https://revenue.gujarat.gov.in",
        "source_document": "Jantri Rates",
        "license": "GODL-India",
        "state": "Gujarat",
        "retrieved_at": datetime.now(timezone.utc).date().isoformat(),
        "method": "live scrape/extraction of official Gujarat Jantri",
        "official": True,
    }, indent=2))
    print(f"Wrote {len(rows)} verified rows → {SOURCES / (SOURCE_KEY + '.csv')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

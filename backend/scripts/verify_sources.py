#!/usr/bin/env python3
"""
Verify circle-rate source artifacts — only trust what we can actually verify.
=============================================================================

The artifact gate (``official: true``) is a self-assertion; it does not prove the
numbers came from an official source. This pass applies *objective* verification
and rewrites each source's meta so the loader only serves genuinely-verified data
as ``data_class="real"``. Everything else is honestly downgraded to curated
(``official: false``) until it is truly verified — preserving the honesty contract.

Verification criteria (BOTH required for "real"):
  1. has_live_scraper — we have a proven, runnable scraper for this state
     (currently only Maharashtra e-ASR; see maharashtra_live.CITY_PLANS).
  2. genuine_extraction — the artifact shows real per-locality variation
     (>1 distinct distance-from-core). Templated/generated data uses a single
     placeholder distance for every locality, which is impossible for real data.

Run:  python scripts/verify_sources.py            # verify + rewrite metas
      python scripts/verify_sources.py --dry-run  # report only
"""
from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "app/ingestion/scrapers/circle_rates/sources"

# Sources backed by a proven, runnable live scraper (extend as scrapers are added).
LIVE_SCRAPER_SOURCES = {"maharashtra_igr"}


def _distinct_distances(csv_path: Path) -> int:
    try:
        rows = list(csv.DictReader(csv_path.read_text().splitlines()))
    except OSError:
        return 0
    return len({(r.get("approx_distance_from_core_km") or "").strip() for r in rows})


def verify_source(source_key: str) -> dict:
    csv_path = SOURCES / f"{source_key}.csv"
    has_scraper = source_key in LIVE_SCRAPER_SOURCES
    distinct = _distinct_distances(csv_path)
    genuine = distinct > 1
    verified = has_scraper and genuine
    return {
        "source_key": source_key,
        "has_live_scraper": has_scraper,
        "distinct_distance_values": distinct,
        "genuine_extraction": genuine,
        "verified": verified,
    }


def main(argv: list[str]) -> int:
    dry = "--dry-run" in argv
    metas = sorted(SOURCES.glob("*.meta.json"))
    if not metas:
        print("No source metas found.")
        return 1

    verified_n = 0
    print(f"{'source':30s} {'scraper':8s} {'distances':10s} {'VERDICT'}")
    for meta_path in metas:
        key = meta_path.stem.replace(".meta", "")
        v = verify_source(key)
        verdict = "✅ REAL" if v["verified"] else "🟡 curated (unverified)"
        print(f"{key:30s} {str(v['has_live_scraper']):8s} {v['distinct_distance_values']:<10d} {verdict}")
        if v["verified"]:
            verified_n += 1
        if dry:
            continue

        meta = json.loads(meta_path.read_text())
        if v["verified"]:
            meta["official"] = True
            meta["verified"] = True
            meta["verification_note"] = (
                "Verified: backed by a proven live scraper; per-locality distances vary "
                "(genuine extraction)."
            )
        else:
            # Preserve the original claim for transparency, then tell the truth.
            if "method" in meta and "claimed_method" not in meta:
                meta["claimed_method"] = meta["method"]
            meta["official"] = False           # ← loader will now serve this as curated, not real
            meta["verified"] = False
            reason = []
            if not v["has_live_scraper"]:
                reason.append("no live scraper / portal not reachable from ingestion env")
            if not v["genuine_extraction"]:
                reason.append("uniform placeholder distance (not a genuine extraction)")
            meta["method"] = "UNVERIFIED — " + "; ".join(reason) + \
                "; served as curated until verified against an official rate book"
        meta["verification_checked_at"] = datetime.now(timezone.utc).date().isoformat()
        meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False))

    print(f"\nVerified (kept as REAL): {verified_n} / {len(metas)} sources.")
    if not dry:
        print("Metas rewritten. Unverified sources now load as curated (honesty contract intact).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

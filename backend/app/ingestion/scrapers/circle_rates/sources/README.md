# Verified circle-rate source artifacts

Drop an **official, published** circle-rate / guidance-value extract here and the
adapter promotes that state's data from 🟡 `curated` (unverified transcription)
to 🟢 `real` (`verification_status="source_verified"`) — with a full, auditable
provenance trail (source URL, official document name, retrieval date, and a
**SHA-256** of the file so anyone can re-verify it against the gazette).

> **Honesty rule:** only put numbers here that are transcribed from the official
> published rate book / portal export. The hash + source URL make the data
> *auditable* — a reviewer can re-download the official document and compare.
> Do **not** invent values; that would re-introduce the fabrication the
> verification gate exists to prevent.

## Files per source (both required to activate)

For a source key like `maharashtra_igr`:

### `maharashtra_igr.csv`
```csv
city_id,locality_name,value_inr_per_sqft,direction_hint,approx_distance_from_core_km,effective_date
pune,Kothrud,1240,W,2.5,2024-04-01
pune,Wakad,1080,NW,7.0,2024-04-01
```
- `city_id` must match `cities_data.py` (e.g. `pune`, `bengaluru`).
- `value_inr_per_sqft` — convert from the gazette's ₹/sq.m by ÷ 10.7639.
- `direction_hint` ∈ N|NE|E|SE|S|SW|W|NW (compass bearing of the locality from the city core).
- `effective_date` — the rate book's effective date (ISO `YYYY-MM-DD`).

### `maharashtra_igr.meta.json`
```json
{
  "source": "Maharashtra IGR — Annual Statement of Rates (ASR) 2024-25",
  "source_url": "https://easr.igrmaharashtra.gov.in/",
  "source_document": "ASR 2024-25 — Pune district rate book (PDF)",
  "license": "GODL-India",
  "retrieved_at": "2026-06-03",
  "official": true
}
```

`official` must be `true`. If `official` is missing/false, the loader refuses to
mark the rows `real` (they stay curated) — the gate fails closed.

## Recognised source keys
| key | state | official portal |
|---|---|---|
| `maharashtra_igr` | Maharashtra | igrmaharashtra.gov.in / easr |
| `karnataka_kaveri` | Karnataka | kaverionline.karnataka.gov.in |
| `telangana_igrs` | Telangana | registration.telangana.gov.in (Dharani) |

This directory ships **empty of data on purpose** — no committed numbers means no
unverifiable "real" claims. Add a real artifact to make a state genuinely real.

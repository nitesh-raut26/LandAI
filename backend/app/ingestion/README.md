# LAND AI — Real Data Ingestion Layer

Turns LAND AI from a *curated* dataset into a platform that ingests **real,
continuously-refreshable, legally-sourced** intelligence — starting with live
**OpenStreetMap** amenity & infrastructure data.

> **The data contract:** every dataset that enters the platform is wrapped in a
> `Provenance` envelope (`source · source_url · license · fetched_at ·
> confidence · freshness_score · legality_note`). Nothing is invented or
> randomly generated. If a source is unavailable we return an explicit
> `available: false` envelope — **never** fabricated numbers.

---

## Architecture

```
ingestion/
  provenance.py          # Provenance + Unavailable models; freshness/confidence helpers
  compliance.py          # SOURCE_REGISTRY (licence + legal status per source) + RobotsGate
  config.py              # env-driven settings (endpoints, UA, cache, radius, timeouts)
  cache.py               # async file-based TTL cache (atomic writes)
  http_client.py         # async httpx client: per-host throttle + retry/backoff + Retry-After
  scrapers/
    base.py              # BaseAdapter: compliance-gated, cached, throttled, provenance-wrapped
    overpass.py          # REAL amenity/infra pull from OpenStreetMap (Overpass API)
    nominatim.py         # geocode place -> coords/bbox (OpenStreetMap Nominatim)
    listings_gated.py    # ToS-protected listing portals — DISABLED BY DESIGN
  normalizers/osm.py     # raw Overpass elements -> canonical amenity POIs (dedup, classify)
  enrichers/amenities.py # haversine distances + derived density/accessibility/livability scores
  pipelines/
    amenities_pipeline.py# city/point -> Overpass -> normalize -> enrich -> Provenance
```

Flow: **`/api/live/amenities/{city_id}` → pipeline → OverpassAdapter (gated,
cached, throttled) → normalizer → enricher → Provenance-wrapped JSON.**

---

## Sources & legality

| Source | Key | Licence | Status | Notes |
|---|---|---|---|---|
| OpenStreetMap (Overpass API) | `osm_overpass` | ODbL 1.0 | ✅ permitted | amenities/infra; attribution required; rate-limited |
| OpenStreetMap (Nominatim) | `osm_nominatim` | ODbL 1.0 | ✅ permitted | geocoding; ≤1 req/s + identifying UA mandatory |
| 99acres / MagicBricks / Housing / CommonFloor | `99acres` … | proprietary | ⛔ **disabled** | ToS prohibit automated extraction — adapter **refuses to run** |

`GET /api/live/sources` returns this registry live, plus a demonstration that the
listing portals are gated (they return `blocked: true`, never data).

### Listing prices — the compliant path
Listing portals forbid scraping in their Terms of Service, so we do **not** scrape
them. `scrapers/listings_gated.py` is the enforced boundary *and* the documented
seam for a **licensed feed / official API**: register it as a new permitted source
in `SOURCE_REGISTRY`, then point a dedicated adapter at it. Until then, curated
prices stay clearly labelled as curated.

---

## API

| Endpoint | Description |
|---|---|
| `GET /api/live/health` | switch state + UA + endpoint list |
| `GET /api/live/sources` | full source registry + ToS-gate demonstration |
| `GET /api/live/amenities/{city_id}` | live amenities for a curated city (uses its stored coords) |
| `GET /api/live/amenities?lat=&lng=` | live amenities for any point |

Query params: `radius_m` (500–60000), `max_pois` (0–500). Example response (trimmed):

```json
{
  "available": true,
  "query": {"lat": 47.3769, "lng": 8.5417, "radius_m": 4000, "city_id": "..."},
  "amenities": {
    "total_amenities": 581,
    "counts_by_category": {"school": 194, "hospital": 9, "metro_station": 33, "...": 0},
    "nearest_km": {"metro_station": 0.827, "airport": 8.367, "railway_station": 0.191},
    "scores": {"amenity_density": 100.0, "accessibility": 100.0, "livability": 100.0},
    "score_method": {"livability": "0.30·education + 0.30·healthcare + 0.15·retail + 0.25·density", "...": "..."},
    "poi_sample": [{"category": "clinic", "name": "MRI Bahnhofplatz", "distance_km": 0.078}]
  },
  "provenance": {
    "source": "OpenStreetMap (Overpass API)", "license": "ODbL 1.0",
    "confidence": 0.991, "freshness_score": 1.0, "cache_hit": false,
    "legality_note": "Queried via the public Overpass API under ODbL 1.0 …"
  }
}
```

### Derived scores (transparent by design)
All scores are **0–100 indicators derived from real OSM counts/distances** — not
prices, not forecasts. Formulas are echoed back under `score_method`:
- `amenity_density = 100·min(total/60, 1)`
- `education = 100·min((schools+universities)/25, 1)`
- `healthcare = 100·min((hospitals+clinics)/15, 1)`
- `accessibility = 0.35·metro + 0.25·rail + 0.20·airport + 0.20·highway` (each a proximity score)
- `livability = 0.30·education + 0.30·healthcare + 0.15·retail + 0.25·density`

### Provenance confidence (transparent by design)
`confidence = 0.55 + 0.25·named_fraction + 0.20·coverage` where `coverage =
min(total/40, 1)`; returns `0.2` when the area appears unmapped (0 results).
`freshness_score = 1 − age/ttl` (clamped), so cached data visibly decays.

---

## Reliability & politeness
- **Caching** — responses cached on disk (TTL: amenities 7d, geocode 30d). Repeat
  calls are instant and don't re-hit upstream.
- **Rate limiting** — per-host minimum interval (Overpass 1.0s, Nominatim 1.1s).
- **Retries** — exponential backoff + jitter on 429/5xx/transport errors; honours
  `Retry-After`.
- **Failover** — Overpass tries each configured endpoint in order.
- **Honest failure** — upstream down ⇒ `available: false` envelope, not fake data.

---

## Configuration
See [`backend/.env.example`](../../.env.example). Key vars: `LIVE_INGESTION_ENABLED`,
`OVERPASS_ENDPOINTS`, `INGESTION_CONTACT`, `INGESTION_AMENITY_RADIUS_M`.

> **Note on Overpass reachability:** `OVERPASS_ENDPOINTS` must be **global**
> instances. `overpass-api.de` is the canonical default; some networks/CDNs block
> it (or specific egress IPs), so configure a reachable global mirror or a
> self-hosted Overpass in production. Regional mirrors (e.g. `overpass.osm.ch`,
> Swiss-only) must **not** be used as a general endpoint — they silently return
> empty results outside their region.

---

## Adding a new source
1. Register it in `SOURCE_REGISTRY` (`compliance.py`) with licence + legal status.
   If its ToS forbids automated access, set `allowed=False` — adapters will refuse.
2. Write an adapter subclassing `BaseAdapter` (you get gating, cache, throttle,
   retry, and provenance for free).
3. Add a normalizer (raw → canonical) and, if needed, an enricher (derived features).
4. Wire a pipeline + an `/api/live/*` route.
5. Add tests (see `backend/tests/`).

## Tests
```bash
cd backend && ./venv/bin/python -m pytest tests -q
```
All tests run **offline** (HTTP mocked via `httpx.MockTransport`; the gate/normalizer/
enricher are pure). Network is never required for CI.

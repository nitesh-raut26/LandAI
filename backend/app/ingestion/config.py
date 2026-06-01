"""
Ingestion configuration — environment-driven, with safe defaults.

Everything here can be overridden via environment variables (see
``backend/.env.example``). Defaults are chosen so the engine runs out-of-the-box
against the public OSM endpoints while staying within their usage policies.
"""
from __future__ import annotations

import os
from pathlib import Path


def _bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


# Identifying contact for outbound requests. Nominatim's usage policy REQUIRES a
# valid identifying User-Agent. We default to a NON-personal placeholder — set
# INGESTION_CONTACT to a real ops mailbox in production. (We never bake a
# personal email into outbound traffic.)
INGESTION_CONTACT: str = os.getenv("INGESTION_CONTACT", "ops@landai.example")

USER_AGENT: str = os.getenv(
    "INGESTION_USER_AGENT",
    f"LandAI-Ingestion/2.0 (+https://landai.example; {INGESTION_CONTACT})",
)

# Cache lives under backend/.cache/ingestion by default.
CACHE_DIR: str = os.getenv(
    "INGESTION_CACHE_DIR",
    str(Path(__file__).resolve().parents[2] / ".cache" / "ingestion"),
)

# Overpass endpoints, tried in order (failover). These MUST be GLOBAL-coverage
# instances — a regional mirror (e.g. overpass.osm.ch, which hosts a Swiss-only
# extract) would silently return empty results for Indian queries, which we
# never want to mistake for "no amenities". Override with OVERPASS_ENDPOINTS in
# environments where a particular host is unreachable, or point at a self-hosted
# Overpass for production-scale use.
OVERPASS_ENDPOINTS: list[str] = [
    e.strip()
    for e in os.getenv(
        "OVERPASS_ENDPOINTS",
        "https://overpass-api.de/api/interpreter,"
        "https://overpass.kumi.systems/api/interpreter,"
        "https://overpass.private.coffee/api/interpreter",
    ).split(",")
    if e.strip()
]
OVERPASS_URL: str = os.getenv("OVERPASS_URL", OVERPASS_ENDPOINTS[0])
NOMINATIM_URL: str = os.getenv("NOMINATIM_URL", "https://nominatim.openstreetmap.org")

# Kept modest so an interactive request fails fast and honestly when an upstream
# is slow/unreachable: we rely on endpoint *failover* (try the next mirror) rather
# than hammering one dead endpoint with long retries.
HTTP_TIMEOUT: float = float(os.getenv("INGESTION_HTTP_TIMEOUT", "15"))
HTTP_MAX_RETRIES: int = int(os.getenv("INGESTION_HTTP_MAX_RETRIES", "1"))

# Master switch. When false, /api/live/* endpoints report disabled instead of
# making outbound calls (useful for offline / CI environments).
LIVE_INGESTION_ENABLED: bool = _bool(os.getenv("LIVE_INGESTION_ENABLED"), default=True)

# Default search radius (metres) for intra-city amenities.
AMENITY_RADIUS_M: int = int(os.getenv("INGESTION_AMENITY_RADIUS_M", "8000"))

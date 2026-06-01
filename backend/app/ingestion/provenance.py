"""
Provenance envelope — the anti-"fake-data" contract.
=====================================================

No dataset crosses into the LAND AI platform without a :class:`Provenance`
record stating *where* it came from, *when*, under *what licence*, *how
confident* we are, and *how fresh* it is.

All scoring formulas in this module are intentionally simple and documented so
that confidence/freshness numbers are explainable — never opaque.
"""
from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


# ── time helpers (UTC, ISO-8601 with trailing Z) ────────────────────────────
def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def utcnow_iso() -> str:
    return utcnow().isoformat().replace("+00:00", "Z")


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def freshness_score(fetched_at: datetime, ttl_seconds: int) -> float:
    """Linear decay from 1.0 (just fetched) to 0.0 (>= TTL old).

    Transparent by design: ``freshness = 1 - age/ttl``, clamped to [0, 1].
    A value of 1.0 means "fetched moments ago"; 0.0 means "as stale as the TTL
    allows". Callers surface this to the UI as a freshness meter.
    """
    if ttl_seconds <= 0:
        return 1.0
    age = (utcnow() - fetched_at).total_seconds()
    return clamp01(1.0 - age / ttl_seconds)


class Provenance(BaseModel):
    """Metadata attached to every ingested dataset. Serialised into every
    ``/api/live/*`` response so the frontend can render source attribution,
    a confidence meter, and a "last updated" / freshness badge."""

    source: str                       # human label, e.g. "OpenStreetMap (Overpass API)"
    source_key: str                   # registry key, e.g. "osm_overpass"
    source_url: str | None = None
    license: str | None = None        # e.g. "ODbL 1.0"
    attribution: str | None = None    # e.g. "© OpenStreetMap contributors"
    fetched_at: str = Field(default_factory=utcnow_iso)  # ISO-8601 UTC
    confidence: float = Field(ge=0.0, le=1.0)
    freshness_score: float = Field(ge=0.0, le=1.0)
    legality_note: str
    cache_hit: bool = False
    ttl_seconds: int | None = None
    record_count: int | None = None
    notes: list[str] = Field(default_factory=list)


class Unavailable(BaseModel):
    """Returned (instead of fabricated data) when a real source cannot be
    reached. Honesty over hallucination."""

    available: bool = False
    source: str
    source_key: str
    reason: str
    checked_at: str = Field(default_factory=utcnow_iso)
    legality_note: str | None = None

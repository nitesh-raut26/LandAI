"""
Base class and data types for circle-rate (guidance value) scrapers.

Every state adapter inherits :class:`CircleRateAdapter` and returns a list of
:class:`PriceObservation` objects — the canonical price row that flows into
the zone price-index upgrade and the PDF report layer.

Honesty contract — STRICT VERIFICATION GATE
--------------------------------------------
A government *source type* being real does NOT make hand-transcribed numbers real.
``data_class`` is therefore **derived from ``verification_status``**, not asserted:

- ``verification_status="unverified_transcription"`` → ``data_class="curated"``.
  The numbers are believed to come from a published gazette but are NOT yet
  machine-verified against a committed source artifact, so they are honestly
  labelled *curated* (expert dataset, not live/auditable). The DataStatusBadge
  shows 🟡 Govt guidance (unverified) — never a plain green 🟢 Real.
- ``verification_status in {"source_verified", "live_fetched"}`` → ``data_class="real"``.
  Only emitted when a verifiable source artifact (a committed CSV extracted from the
  official gazette, with a recorded SHA-256 + retrieval date) or a live portal fetch
  backs the observation.

[HUMAN GATE] To promote a state's dataset to ``"real"``: commit the official
gazette extract under ``app/ingestion/scrapers/circle_rates/sources/<state>.csv``
with its source URL + SHA-256, then set the adapter's ``verification_status =
"source_verified"``. Until then the data stays honestly *curated*.

- ``basis`` = ``"circle_rate"`` means the figure originates from a government
  guidance-value table (the legal stamp-duty floor), not a listing portal.
- ``confidence`` encodes extraction quality: 1.0 = machine-readable structured table;
  0.75 = parsed from a published PDF/gazette; 0.5 = manual transcription.
"""
from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Any

from ...scrapers.base import BaseAdapter

# A data point is only "real" when its provenance is verifiable. Government
# *source type* alone is not sufficient — the transcription must be backed by a
# committed source artifact or a live fetch.
VERIFIED_STATUSES = frozenset({"source_verified", "live_fetched"})


def resolve_data_class(verification_status: str) -> str:
    """Derive the honest data_class from the verification status.

    real ⇐ verifiable provenance (source artifact / live fetch);
    curated ⇐ believed-government but unverified transcription.
    """
    return "real" if verification_status in VERIFIED_STATUSES else "curated"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class PriceObservation:
    """One circle-rate observation for a locality within a city.

    Canonical schema — all adapters produce this type. The zone matcher then
    joins it onto growth-zone sectors.
    """
    # Identity
    city_id: str                  # matches cities_data.py id (e.g. "pune", "bengaluru")
    city_name: str
    state: str
    locality_name: str            # sub-city area / ward / mandal / village

    # Price
    value_inr_per_sqft: float    # ≥ 100, ≤ 100 000 (clamped; raw stored separately)
    basis: str = "circle_rate"   # circle_rate | registered_txn | listing | curated
    effective_date: date = field(default_factory=date.today)

    # Geometry hint (optional — enriched by LocalityZoneMatcher)
    approx_distance_from_core_km: float = 0.0
    direction_hint: str = ""     # N|NE|E|SE|S|SW|W|NW or ""

    # Provenance
    source: str = ""
    source_url: str | None = None
    license: str = "GODL-India"
    confidence: float = 0.75
    # verification_status is the source of truth; data_class is DERIVED from it in
    # __post_init__ so a "real" label can never be set without verifiable provenance.
    verification_status: str = "unverified_transcription"
    data_class: str = "curated"  # derived — do not trust a passed-in value
    fetched_at: datetime = field(default_factory=_utcnow)

    # Audit
    raw: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Enforce the honesty gate at construction time.
        self.data_class = resolve_data_class(self.verification_status)

    def recompute_data_class(self) -> None:
        self.data_class = resolve_data_class(self.verification_status)

    def as_dict(self) -> dict[str, Any]:
        return {
            "city_id": self.city_id,
            "city_name": self.city_name,
            "state": self.state,
            "locality_name": self.locality_name,
            "value_inr_per_sqft": self.value_inr_per_sqft,
            "basis": self.basis,
            "effective_date": self.effective_date.isoformat(),
            "approx_distance_from_core_km": self.approx_distance_from_core_km,
            "direction_hint": self.direction_hint,
            "source": self.source,
            "source_url": self.source_url,
            "license": self.license,
            "confidence": self.confidence,
            "verification_status": self.verification_status,
            "data_class": self.data_class,
            "fetched_at": self.fetched_at.isoformat().replace("+00:00", "Z"),
        }


def _clamp_price(value: float) -> float:
    """Clamp to a plausible Indian land-price range (₹100–₹1,00,000/sqft).
    Values outside this range signal a parsing error and are clamped rather than
    silently accepted — the raw value is preserved in ``raw`` for audit.
    """
    return max(100.0, min(100_000.0, float(value)))


class CircleRateAdapter(BaseAdapter, ABC):
    """Abstract base for state guidance-value adapters.

    Concrete adapters override :meth:`fetch_observations` and return a list of
    :class:`PriceObservation` objects.  The base class handles the compliance
    gate, cache, provenance envelope, and price clamping.
    """

    # Subclasses set these:
    state_name: str = ""         # e.g. "Maharashtra"
    data_source_label: str = ""  # e.g. "IGR Maharashtra ASR"
    data_source_url: str | None = None
    extraction_confidence: float = 0.75   # 0.75 = published gazette/PDF
    # Honesty gate: hand-transcribed seed data is "unverified_transcription" until a
    # committed source artifact backs it. [HUMAN GATE] flip to "source_verified".
    verification_status: str = "unverified_transcription"

    # TTL: circle rates are revised annually — 30-day cache is safe and polite
    _TTL = 30 * 24 * 3600

    @abstractmethod
    def fetch_observations(
        self, city_id: str, city_name: str, state: str
    ) -> list[PriceObservation]:
        """Return circle-rate observations for the given city.

        Adapters must NOT fabricate data: if the city is not covered, return [].
        The data_class is DERIVED from the adapter's ``verification_status`` —
        adapters never assert "real" directly.
        """
        ...

    def get_observations(
        self, city_id: str, city_name: str, state: str
    ) -> list[PriceObservation]:
        """Public entry point — compliance + clamping + provenance.

        Resolution order (honesty-gated):
        1. A **verified official artifact** for this city (``sources/<key>.csv`` +
           ``.meta.json``) → ``source_verified`` → ``data_class="real"``.
        2. Otherwise the adapter's hand-transcribed seed → ``unverified_transcription``
           → ``data_class="curated"``.
        """
        from .artifact_loader import load_verified_observations

        artifact = [o for o in load_verified_observations(self.source_key) if o.city_id == city_id]
        raw_obs = artifact if artifact else self.fetch_observations(city_id, city_name, state)

        result = []
        for obs in raw_obs:
            # Clamp price, preserve raw for audit
            clamped = _clamp_price(obs.value_inr_per_sqft)
            if clamped != obs.value_inr_per_sqft:
                obs.raw["original_price"] = obs.value_inr_per_sqft
            obs.value_inr_per_sqft = clamped
            # Stamp provenance defaults without overwriting artifact-supplied values.
            obs.source = obs.source or self.data_source_label
            obs.source_url = obs.source_url or self.data_source_url
            obs.license = obs.license or self.policy.license
            obs.fetched_at = _utcnow()
            # Apply the adapter's default verification only to seed rows that didn't
            # set one. Artifact rows already carry "source_verified" — never clobber.
            if obs.verification_status == "unverified_transcription" and \
                    self.verification_status != "unverified_transcription":
                obs.verification_status = self.verification_status
            obs.recompute_data_class()
            result.append(obs)
        return result

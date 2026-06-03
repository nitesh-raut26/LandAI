"""
Base class and data types for circle-rate (guidance value) scrapers.

Every state adapter inherits :class:`CircleRateAdapter` and returns a list of
:class:`PriceObservation` objects — the canonical price row that flows into
the zone price-index upgrade and the PDF report layer.

Honesty contract
----------------
- ``basis`` = ``"circle_rate"`` means data originates from a government guidance-value
  table, not from a listing portal. Circle rates are the legal floor for stamp duty
  registration, so they are *conservative* (actual transaction prices may be higher)
  and *real* (government-published, not estimated).
- ``confidence`` encodes extraction quality: 1.0 = machine-readable structured table;
  0.75 = parsed from a published PDF/gazette; 0.5 = manual transcription.
- ``data_class`` = ``"real"`` because the source is a government authority (GODL-India),
  not a heuristic formula. This flips the DataStatusBadge from 🟠 Heuristic → 🟢 Real.
"""
from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Any

from ...scrapers.base import BaseAdapter


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
    data_class: str = "real"     # always "real" for government-published circle rates
    fetched_at: datetime = field(default_factory=_utcnow)

    # Audit
    raw: dict[str, Any] = field(default_factory=dict)

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

    # TTL: circle rates are revised annually — 30-day cache is safe and polite
    _TTL = 30 * 24 * 3600

    @abstractmethod
    def fetch_observations(
        self, city_id: str, city_name: str, state: str
    ) -> list[PriceObservation]:
        """Return circle-rate observations for the given city.

        Adapters must NOT fabricate data: if the city is not covered, return [].
        Data class must always be "real" (government source).
        """
        ...

    def get_observations(
        self, city_id: str, city_name: str, state: str
    ) -> list[PriceObservation]:
        """Public entry point — wraps fetch with compliance + clamping + provenance."""
        # compliance gate already enforced in BaseAdapter.__init__
        raw_obs = self.fetch_observations(city_id, city_name, state)
        result = []
        for obs in raw_obs:
            # Clamp price, preserve raw for audit
            clamped = _clamp_price(obs.value_inr_per_sqft)
            if clamped != obs.value_inr_per_sqft:
                obs.raw["original_price"] = obs.value_inr_per_sqft
            obs.value_inr_per_sqft = clamped
            # Stamp provenance from policy
            obs.source = obs.source or self.data_source_label
            obs.source_url = obs.source_url or self.data_source_url
            obs.license = self.policy.license
            obs.fetched_at = _utcnow()
            obs.data_class = "real"
            result.append(obs)
        return result

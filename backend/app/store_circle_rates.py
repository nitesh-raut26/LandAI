"""
Price observation store — in-process dict store for circle-rate data.

This is the runtime registry that the zone-price-index function queries to
decide whether to use a real government circle rate (data_class='real') or
fall back to the existing distance-decay heuristic (data_class='heuristic').

Design decisions
----------------
- In-process by default: zero external dependencies, works in dev/test.
- No shared state between replicas (same pattern as the existing metrics
  collector). Move to Redis+Postgres persistence when deploying multi-replica.
- The store is seeded at startup for all three covered states and can be
  refreshed on demand via the /api/data/coverage endpoint.
"""
from __future__ import annotations

import threading
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from .ingestion.scrapers.circle_rates import (
    MaharashtraASRAdapter,
    KarnatakaKaveriAdapter,
    TelanganaIGRSAdapter,
    PriceObservation,
)
from .data.cities_data import get_all_cities


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PriceObservationStore:
    """Thread-safe in-process store for PriceObservation objects.

    Keyed by city_id. Each city holds a list of observations from all
    covered adapters. The store is idempotent: seeding it twice is safe.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._data: dict[str, list[PriceObservation]] = defaultdict(list)
        self._last_refresh: dict[str, datetime] = {}
        self._seeded = False

    def put(self, obs: PriceObservation) -> None:
        with self._lock:
            self._data[obs.city_id].append(obs)
            self._last_refresh[obs.city_id] = _utcnow()

    def put_many(self, observations: list[PriceObservation]) -> None:
        with self._lock:
            for obs in observations:
                self._data[obs.city_id].append(obs)
                self._last_refresh[obs.city_id] = _utcnow()

    def get_for_city(self, city_id: str) -> list[PriceObservation]:
        with self._lock:
            return list(self._data.get(city_id, []))

    def last_refresh(self, city_id: str) -> datetime | None:
        with self._lock:
            return self._last_refresh.get(city_id)

    def covered_cities(self) -> list[str]:
        with self._lock:
            return [cid for cid, obs in self._data.items() if obs]

    def coverage_stats(self) -> dict[str, Any]:
        """Global coverage statistics for the /api/data/coverage endpoint."""
        cities = get_all_cities()
        total = len(cities)
        with self._lock:
            covered = [c for c in cities if self._data.get(c["id"])]
        covered_states = sorted({c["state"] for c in covered})
        return {
            "total_cities": total,
            "covered_cities": len(covered),
            "covered_states": covered_states,
            "coverage_pct": round(len(covered) / total * 100, 1) if total else 0.0,
            "seeded": self._seeded,
            "last_seeded": self._last_refresh.get("__seed__", None),
        }

    def clear_city(self, city_id: str) -> None:
        with self._lock:
            self._data.pop(city_id, None)
            self._last_refresh.pop(city_id, None)

    def seed_all(self) -> dict[str, int]:
        """Seed the store with all three state adapters for every covered city.

        Safe to call multiple times (clears then reseeds covered cities).
        Returns a dict of {city_id: observation_count} for covered cities.
        """
        cities = get_all_cities()
        adapters = [
            MaharashtraASRAdapter(),
            KarnatakaKaveriAdapter(),
            TelanganaIGRSAdapter(),
        ]
        results: dict[str, int] = {}
        for city in cities:
            cid = city["id"]
            city_name = city["name"]
            state = city["state"]
            new_obs: list[PriceObservation] = []
            for adapter in adapters:
                try:
                    obs = adapter.get_observations(cid, city_name, state)
                    new_obs.extend(obs)
                except Exception:
                    pass
            if new_obs:
                with self._lock:
                    self._data[cid] = new_obs  # replace (idempotent)
                    self._last_refresh[cid] = _utcnow()
                results[cid] = len(new_obs)

        with self._lock:
            self._seeded = True
            self._last_refresh["__seed__"] = _utcnow()
        return results


# ── Global singleton ─────────────────────────────────────────────────────────
# Shared by the API routes and geo/spatial.py via import.
PRICE_STORE = PriceObservationStore()

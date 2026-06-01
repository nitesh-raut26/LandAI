"""
BaseAdapter — the contract every source adapter inherits.

Guarantees enforced for all subclasses:
  * construction **refuses** if the source is disallowed by compliance policy
  * web sources are checked against ``robots.txt`` before any fetch
  * responses are cached (TTL from policy) and throttled (interval from policy)
  * every result is wrapped in a :class:`Provenance` envelope
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Awaitable, Callable

from .. import config
from ..cache import FileCache
from ..compliance import ComplianceError, RobotsGate, SourcePolicy, require_allowed
from ..http_client import HttpClient
from ..provenance import Provenance, freshness_score, utcnow
from ...metrics import METRICS


class BaseAdapter:
    source_key: str = ""

    def __init__(
        self,
        source_key: str | None = None,
        http: HttpClient | None = None,
        cache: FileCache | None = None,
        robots: RobotsGate | None = None,
    ) -> None:
        self.source_key = source_key or type(self).source_key
        if not self.source_key:
            raise ValueError("Adapter must define a source_key")
        # Refuses (raises ComplianceError) if the source is disallowed:
        self.policy: SourcePolicy = require_allowed(self.source_key)
        self._http = http or HttpClient()
        self._cache = cache or FileCache(config.CACHE_DIR, namespace=self.source_key)
        self._robots = robots or RobotsGate(config.USER_AGENT)

    async def aclose(self) -> None:
        await self._http.aclose()

    def _guard_robots(self, url: str) -> None:
        if self.policy.check_robots and not self._robots.can_fetch(url):
            raise ComplianceError(
                f"robots.txt disallows fetching {url} (source '{self.source_key}')"
            )

    async def cached_json(
        self,
        cache_key: str,
        ttl: int,
        fetch: Callable[[], Awaitable[Any]],
    ) -> tuple[Any, dict]:
        """Return ``(payload, meta)``.

        ``meta`` = ``{cache_hit: bool, age_seconds: float, fetched_at: datetime}``.
        On a cache hit ``fetched_at`` is reconstructed from the entry's age so
        the freshness score reflects when the data was actually retrieved.
        """
        hit = await self._cache.get(cache_key, ttl)
        if hit is not None:
            METRICS.incr("ingestion_cache_hit")
            payload, age = hit
            return payload, {
                "cache_hit": True,
                "age_seconds": age,
                "fetched_at": utcnow() - timedelta(seconds=age),
            }
        METRICS.incr("ingestion_cache_miss")
        payload = await fetch()
        await self._cache.set(cache_key, payload)
        return payload, {"cache_hit": False, "age_seconds": 0.0, "fetched_at": utcnow()}

    def make_provenance(
        self,
        *,
        confidence: float,
        fetched_at: datetime,
        cache_hit: bool,
        ttl: int,
        record_count: int | None = None,
        notes: list[str] | None = None,
    ) -> Provenance:
        return Provenance(
            source=self.policy.name,
            source_key=self.policy.key,
            source_url=self.policy.url,
            license=self.policy.license,
            attribution=self.policy.attribution,
            fetched_at=fetched_at.isoformat().replace("+00:00", "Z"),
            confidence=round(float(confidence), 3),
            freshness_score=round(freshness_score(fetched_at, ttl), 3),
            legality_note=self.policy.legality_note,
            cache_hit=cache_hit,
            ttl_seconds=ttl,
            record_count=record_count,
            notes=notes or [],
        )

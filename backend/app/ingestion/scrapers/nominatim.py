"""
Nominatim adapter — geocode a place name to coordinates + bounding box.

Used for places not already in the curated city DB (arbitrary names / lat-lng
lookups). For known cities we use their stored coordinates directly and skip the
geocode round-trip. Nominatim's usage policy (≤1 req/s, identifying User-Agent)
is enforced by the shared HttpClient + SourcePolicy.
"""
from __future__ import annotations

from ..provenance import Provenance
from .base import BaseAdapter


class NominatimAdapter(BaseAdapter):
    source_key = "osm_nominatim"

    async def geocode(self, query: str) -> tuple[dict | None, Provenance]:
        cache_key = f"geocode:{query.strip().lower()}"

        async def _do():
            self._guard_robots(self.policy.url)
            resp = await self._http.get(
                f"{self.policy.url}/search",
                params={"q": query, "format": "jsonv2", "limit": 1, "addressdetails": 1},
                min_interval=self.policy.min_interval_seconds,
            )
            resp.raise_for_status()
            return resp.json()

        raw, meta = await self.cached_json(cache_key, self.policy.default_ttl_seconds, _do)

        result = None
        if isinstance(raw, list) and raw:
            r0 = raw[0]
            try:
                result = {
                    "display_name": r0.get("display_name"),
                    "lat": float(r0["lat"]),
                    "lng": float(r0["lon"]),
                    "bbox": [float(x) for x in r0.get("boundingbox", [])] or None,
                    "type": r0.get("type"),
                    "osm_type": r0.get("osm_type"),
                }
            except (KeyError, ValueError, TypeError):
                result = None

        prov = self.make_provenance(
            confidence=0.85 if result else 0.2,
            fetched_at=meta["fetched_at"],
            cache_hit=meta["cache_hit"],
            ttl=self.policy.default_ttl_seconds,
            record_count=1 if result else 0,
        )
        return result, prov

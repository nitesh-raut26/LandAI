"""
Overpass adapter — REAL amenity/infrastructure data from OpenStreetMap.

One Overpass QL request pulls schools, colleges/universities, hospitals/clinics,
malls, metro/rail stations, airports, industrial land, and motorway junctions
around a point. ``out center tags;`` gives every way/relation a centroid so we
can compute distances uniformly with nodes.
"""
from __future__ import annotations

from .. import config
from ..provenance import Provenance, clamp01
from ...metrics import METRICS
from .base import BaseAdapter


class OverpassAdapter(BaseAdapter):
    source_key = "osm_overpass"

    @staticmethod
    def build_query(
        lat: float,
        lng: float,
        radius_m: int,
        metro_radius_m: int,
        airport_radius_m: int,
        highway_radius_m: int,
    ) -> str:
        r, mr, ar, hr = int(radius_m), int(metro_radius_m), int(airport_radius_m), int(highway_radius_m)
        c = f"{lat:.6f},{lng:.6f}"
        return f"""[out:json][timeout:25];
(
  nwr(around:{r},{c})[amenity=school];
  nwr(around:{r},{c})[amenity=college];
  nwr(around:{r},{c})[amenity=university];
  nwr(around:{r},{c})[amenity=hospital];
  nwr(around:{r},{c})[amenity=clinic];
  nwr(around:{r},{c})[shop=mall];
  nwr(around:{mr},{c})[railway=station];
  nwr(around:{mr},{c})[railway=subway_entrance];
  nwr(around:{mr},{c})[station=subway];
  nwr(around:{ar},{c})[aeroway=aerodrome];
  nwr(around:{r},{c})[landuse=industrial];
  nwr(around:{hr},{c})[highway=motorway_junction];
);
out center tags;"""

    @staticmethod
    def fetch_confidence(elements: list[dict]) -> float:
        """Transparent OSM data-quality confidence for the raw pull.

        ``confidence = 0.55 + 0.25·named_fraction + 0.20·coverage`` where
        ``named_fraction`` is the share of POIs carrying a ``name`` tag and
        ``coverage = min(total/40, 1)`` (≈40 in-radius POIs ⇒ a well-mapped
        urban area). Returns 0.2 when nothing was found (we reached OSM but the
        area appears unmapped) — never a fabricated high score.
        """
        total = len(elements)
        if total == 0:
            return 0.2
        named = sum(1 for e in elements if (e.get("tags") or {}).get("name"))
        named_fraction = named / total
        coverage = min(total / 40.0, 1.0)
        return clamp01(0.55 + 0.25 * named_fraction + 0.20 * coverage)

    async def fetch_amenities(
        self,
        lat: float,
        lng: float,
        radius_m: int | None = None,
    ) -> tuple[list[dict], Provenance]:
        radius = int(radius_m or config.AMENITY_RADIUS_M)
        metro_r = max(radius, 15000)
        airport_r = 60000
        highway_r = max(radius, 15000)
        query = self.build_query(lat, lng, radius, metro_r, airport_r, highway_r)
        cache_key = f"amenities:{lat:.4f},{lng:.4f}:r{radius}"

        fetch_meta: dict = {}

        async def _do():
            self._guard_robots(self.policy.url)
            last_exc: Exception | None = None
            for endpoint in config.OVERPASS_ENDPOINTS:
                try:
                    resp = await self._http.post(
                        endpoint,
                        data={"data": query},
                        headers={"Accept": "application/json"},
                        min_interval=self.policy.min_interval_seconds,
                    )
                    resp.raise_for_status()
                    fetch_meta["endpoint"] = endpoint
                    return resp.json()
                except Exception as exc:  # failover to the next mirror
                    METRICS.incr("ingestion_source_failure")
                    last_exc = exc
            raise last_exc if last_exc else RuntimeError("No Overpass endpoints configured")

        raw, meta = await self.cached_json(cache_key, self.policy.default_ttl_seconds, _do)
        elements = raw.get("elements", []) if isinstance(raw, dict) else []
        notes = [f"Overpass around-radius: local {radius} m, transit {metro_r} m, airport {airport_r} m."]
        if not meta["cache_hit"] and fetch_meta.get("endpoint"):
            notes.append(f"endpoint={fetch_meta['endpoint']}")
        prov = self.make_provenance(
            confidence=self.fetch_confidence(elements),
            fetched_at=meta["fetched_at"],
            cache_hit=meta["cache_hit"],
            ttl=self.policy.default_ttl_seconds,
            record_count=len(elements),
            notes=notes,
        )
        return elements, prov

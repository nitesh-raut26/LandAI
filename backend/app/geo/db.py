"""
PostGIS Backend (optional)
==========================
The platform is *PostGIS-ready*. When a ``DATABASE_URL`` pointing at a
PostgreSQL/PostGIS instance is provided, this module creates a spatial
``cities`` table (with a ``GEOMETRY(Point, 4326)`` column) and seeds it, and the
geo API can run spatial SQL. When no database is configured — as in the default
local/dev setup — the platform transparently uses the in-memory shapely engine
in :mod:`app.geo.spatial`, so nothing breaks.

A ready-to-use PostGIS service is provided in ``docker-compose.yml``; set
``DATABASE_URL=postgresql+psycopg://landai:landai@db:5432/landai`` to activate.

All imports are guarded; importing this module never fails even if SQLAlchemy /
GeoAlchemy2 are absent.
"""
from __future__ import annotations

import os
from typing import Any

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

_ENGINE = None
_AVAILABLE = False
_REASON = "no DATABASE_URL set"

try:
    if DATABASE_URL:
        from geoalchemy2 import Geometry  # noqa: F401  (import proves the stack is present)
        from sqlalchemy import create_engine, text

        _ENGINE = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
        # probe connection + PostGIS extension
        with _ENGINE.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
            conn.commit()
        _AVAILABLE = True
        _REASON = "connected"
except Exception as exc:  # pragma: no cover - depends on external DB
    _AVAILABLE = False
    _REASON = f"unavailable: {exc.__class__.__name__}"


def is_postgis_available() -> bool:
    return _AVAILABLE


def spatial_backend_status() -> dict[str, Any]:
    return {
        "postgis_available": _AVAILABLE,
        "database_url_set": bool(DATABASE_URL),
        "status": _REASON,
        "active_backend": "postgis" if _AVAILABLE else "shapely-in-memory",
        "note": "Set DATABASE_URL to a PostGIS instance (see docker-compose.yml) to activate SQL spatial queries.",
    }


def init_and_seed(cities: list[dict]) -> dict[str, Any]:
    """Create + seed the spatial cities table. No-op when PostGIS is absent."""
    if not _AVAILABLE:
        return {"seeded": False, **spatial_backend_status()}

    from sqlalchemy import text  # local import; only when available

    with _ENGINE.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS cities (
                id TEXT PRIMARY KEY,
                name TEXT, state TEXT, tier INT,
                growth_phase TEXT, investment_score REAL,
                geom geometry(Point, 4326)
            )
        """))
        conn.execute(text("CREATE INDEX IF NOT EXISTS cities_geom_idx ON cities USING GIST (geom)"))
        for c in cities:
            conn.execute(text("""
                INSERT INTO cities (id, name, state, tier, growth_phase, investment_score, geom)
                VALUES (:id, :name, :state, :tier, :phase, :score,
                        ST_SetSRID(ST_MakePoint(:lng, :lat), 4326))
                ON CONFLICT (id) DO UPDATE SET
                    investment_score = EXCLUDED.investment_score,
                    geom = EXCLUDED.geom
            """), {
                "id": c["id"], "name": c["name"], "state": c["state"], "tier": c["tier"],
                "phase": c["growth_phase"], "score": c["investment_score"],
                "lng": c["lng"], "lat": c["lat"],
            })
    return {"seeded": True, "rows": len(cities), **spatial_backend_status()}


def nearby_cities(lng: float, lat: float, radius_km: float = 200) -> list[dict] | None:
    """Spatial KNN query via PostGIS. Returns None when PostGIS is not active."""
    if not _AVAILABLE:
        return None
    from sqlalchemy import text

    with _ENGINE.connect() as conn:
        rows = conn.execute(text("""
            SELECT id, name, state, investment_score,
                   ST_Distance(geom::geography, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography) / 1000.0 AS dist_km
            FROM cities
            WHERE ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography, :radius_m)
            ORDER BY dist_km ASC
        """), {"lng": lng, "lat": lat, "radius_m": radius_km * 1000}).mappings().all()
    return [dict(r) for r in rows]

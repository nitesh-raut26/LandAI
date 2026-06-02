"""
SQLAlchemy database layer for the auth / platform tables.

**SQLite by default** (zero-setup — works and tests immediately). Point
``AUTH_DATABASE_URL`` (or ``DATABASE_URL``) at PostgreSQL for production; the ORM
is identical. This is distinct from the optional PostGIS spatial DB in app.geo.

For production, drive schema with Alembic instead of ``init_db()``'s create_all
(see ``backend/migrations/`` — ``alembic upgrade head`` for a fresh DB, or
``alembic stamp head`` to adopt an existing create_all database). create_all is
kept for zero-setup dev and tests.
"""
from __future__ import annotations

import os
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

AUTH_DATABASE_URL = (
    os.getenv("AUTH_DATABASE_URL")
    or os.getenv("DATABASE_URL")
    or "sqlite:///./landai_auth.db"
)

_connect_args = {"check_same_thread": False} if AUTH_DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(AUTH_DATABASE_URL, connect_args=_connect_args, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from .auth import models as _models  # noqa: F401  (register auth/platform tables)
    from .ml import registry as _registry  # noqa: F401  (register model_registry table)

    Base.metadata.create_all(bind=engine)


def schema_status() -> dict:
    """Best-effort migration health: is the DB at the Alembic head revision?

    Honest about the dev default: a create_all database has no alembic_version,
    so we report ``not-initialised`` (and how to adopt migrations) rather than
    pretending the schema is governed. Never raises."""
    try:
        import os

        from alembic.config import Config
        from alembic.migration import MigrationContext
        from alembic.script import ScriptDirectory

        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cfg = Config(os.path.join(backend_dir, "alembic.ini"))
        cfg.set_main_option("script_location", os.path.join(backend_dir, "migrations"))
        head = ScriptDirectory.from_config(cfg).get_current_head()
        with engine.connect() as conn:
            current = MigrationContext.configure(conn).get_current_revision()
        if current is None:
            return {"alembic": "not-initialised", "current": None, "head": head,
                    "note": "DB built via create_all (dev). Run `alembic stamp head` to adopt migrations."}
        return {"alembic": "up-to-date" if current == head else "behind", "current": current, "head": head}
    except Exception as exc:  # pragma: no cover - defensive
        return {"alembic": "unknown", "error": type(exc).__name__}

"""
SQLAlchemy database layer for the auth / platform tables.

**SQLite by default** (zero-setup — works and tests immediately). Point
``AUTH_DATABASE_URL`` (or ``DATABASE_URL``) at PostgreSQL for production; the ORM
is identical. This is distinct from the optional PostGIS spatial DB in app.geo.

For production, replace ``init_db()``'s create_all with Alembic migrations
(scaffold documented in the README) — create_all is used here so the platform
runs with no migration step in dev.
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
    from .auth import models as _models  # noqa: F401  (register tables on Base)

    Base.metadata.create_all(bind=engine)

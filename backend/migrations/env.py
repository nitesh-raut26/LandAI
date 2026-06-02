"""Alembic environment for the LandAI auth/platform schema.

Resolves the DB URL the same way app.db does (AUTH_DATABASE_URL / DATABASE_URL /
SQLite default) and registers every ORM model on Base.metadata so autogenerate
sees the full schema. Dev/tests still use create_all (app.db.init_db); Alembic is
the production migration path.
"""
from __future__ import annotations

import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Make `app` importable when alembic runs from the backend/ directory.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import AUTH_DATABASE_URL, Base  # noqa: E402
import app.auth.models  # noqa: E402,F401  (register auth/platform tables on Base)
import app.ml.registry  # noqa: E402,F401  (register model_registry table on Base)

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
DB_URL = os.getenv("AUTH_DATABASE_URL") or os.getenv("DATABASE_URL") or AUTH_DATABASE_URL


def run_migrations_offline() -> None:
    context.configure(
        url=DB_URL, target_metadata=target_metadata, literal_binds=True,
        dialect_opts={"paramstyle": "named"}, compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    section = config.get_section(config.config_ini_section) or {}
    section["sqlalchemy.url"] = DB_URL
    connectable = engine_from_config(section, prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata,
            compare_type=True, render_as_batch=connection.dialect.name == "sqlite",
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

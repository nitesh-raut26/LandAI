"""Migration governance: prove `alembic upgrade head` produces exactly the same
schema as `create_all`, so create_all can be retired in production with confidence."""
import os
import subprocess
import sys
from pathlib import Path

from sqlalchemy import create_engine, inspect

BACKEND = Path(__file__).resolve().parents[1]


def _columns_by_table(db_path: Path) -> dict[str, list[str]]:
    eng = create_engine(f"sqlite:///{db_path}")
    insp = inspect(eng)
    schema = {
        t: sorted(c["name"] for c in insp.get_columns(t))
        for t in insp.get_table_names()
        if t != "alembic_version"
    }
    eng.dispose()
    return schema


def _alembic_head_schema(tmp_path) -> dict[str, list[str]]:
    db = tmp_path / "alembic.db"
    env = {**os.environ, "AUTH_DATABASE_URL": f"sqlite:///{db}"}
    # Run in a subprocess so alembic's logging/env setup can't leak into the test process.
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=str(BACKEND), env=env, check=True, capture_output=True, text=True,
    )
    return _columns_by_table(db)


def _create_all_schema(tmp_path) -> dict[str, list[str]]:
    db = tmp_path / "createall.db"
    eng = create_engine(f"sqlite:///{db}")
    from app.db import Base
    import app.auth.models   # noqa: F401  (register tables)
    import app.ml.registry   # noqa: F401
    Base.metadata.create_all(eng)
    insp = inspect(eng)
    schema = {t: sorted(c["name"] for c in insp.get_columns(t)) for t in insp.get_table_names()}
    eng.dispose()
    return schema


def test_alembic_head_matches_create_all(tmp_path):
    alembic_schema = _alembic_head_schema(tmp_path)
    createall_schema = _create_all_schema(tmp_path)
    # Same tables...
    assert set(alembic_schema) == set(createall_schema), (
        f"table mismatch: alembic-only={set(alembic_schema) - set(createall_schema)}, "
        f"createall-only={set(createall_schema) - set(alembic_schema)}"
    )
    # ...and the same columns in each table.
    for table in createall_schema:
        assert alembic_schema[table] == createall_schema[table], f"column mismatch in {table}"
    # Sanity: the platform tables we expect are present.
    assert {"users", "api_keys", "refresh_sessions", "audit_logs", "usage_daily", "model_registry"} <= set(alembic_schema)


def test_schema_status_reports_state():
    from app.db import schema_status
    st = schema_status()
    assert st["alembic"] in ("up-to-date", "behind", "not-initialised", "unknown")

# Database migrations (Alembic)

Alembic is the **production** migration path for the auth/platform schema
(`app.db.Base`). Dev and tests still use `create_all` via `app.db.init_db()` for
zero-setup; in production you should disable that and drive schema changes here.

The DB URL is resolved in `migrations/env.py` exactly like the app
(`AUTH_DATABASE_URL` → `DATABASE_URL` → SQLite default), so migrations always
target the same database the app uses.

## Common commands (run from `backend/`)

```bash
# Apply all migrations to a fresh database
alembic upgrade head

# Adopt Alembic on an EXISTING database that was created by create_all:
# mark it as already at head WITHOUT re-creating tables, then migrate forward.
alembic stamp head

# After changing an ORM model, generate a migration and review it before applying
alembic revision --autogenerate -m "describe the change"
alembic upgrade head

# Roll back one revision
alembic downgrade -1
```

## Notes
- `env.py` registers every ORM model (`app.auth.models`, `app.ml.registry`) on
  `Base.metadata` so autogenerate sees the full schema. The PostGIS `cities`
  table (separate Base in `app.geo`) is intentionally **not** managed here.
- SQLite uses batch mode (`render_as_batch`) so future `ALTER`s work.
- Initial revision: `d4a67b1ff461_initial_platform_schema` (all 12 platform tables).

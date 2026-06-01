import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]

# Disable the global inbound limiter for the shared app instance so a growing
# suite can't trip cumulative 429s. The limiter itself is tested directly in
# test_ratelimit.py with its own app + explicit middleware.
os.environ.setdefault("RATELIMIT_ENABLED", "false")

# Isolated SQLite DB for auth/platform tables (wiped fresh each run).
os.environ.setdefault("AUTH_DATABASE_URL", f"sqlite:///{BACKEND}/test_auth.db")

# Put backend/ on sys.path so `import app...` works no matter where pytest runs.
sys.path.insert(0, str(BACKEND))

_dbfile = BACKEND / "test_auth.db"
if _dbfile.exists():
    _dbfile.unlink()
from app.db import init_db  # noqa: E402

init_db()

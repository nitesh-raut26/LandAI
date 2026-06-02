"""
Distributed counter / denylist store — with an honest in-process fallback.
=========================================================================

Used for ephemeral, hot-path state that must be shared across replicas in
production: rate-limit counters, login brute-force counters, and the access-token
revocation denylist.

- If ``REDIS_URL`` is set **and** the ``redis`` client is importable and reachable,
  this is backed by Redis (correct across N replicas).
- Otherwise it falls back to a process-local TTL dict. That is correct for a
  single replica / local dev, but is **NOT shared across replicas** — so we never
  silently imply distributed state we don't have. ``backend_name()`` exposes which
  mode is active and the system API reports it.

Durable source-of-truth state (sessions, quotas, audit) lives in the SQL database
(see app.auth.models); this store is only a cache/accelerator. If Redis is down we
fail safe to the in-process path rather than locking users out.
"""
from __future__ import annotations

import os
import threading
import time

REDIS_URL = os.getenv("REDIS_URL")

_redis = None
if REDIS_URL:
    try:  # pragma: no cover - exercised only when a real Redis is configured
        import redis  # type: ignore

        _client = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=2)
        _client.ping()
        _redis = _client
    except Exception:
        _redis = None  # honest fallback — never crash the app over a cache


def backend_name() -> str:
    return "redis" if _redis is not None else "in-process"


def is_distributed() -> bool:
    return _redis is not None


def use_redis(client) -> None:
    """Inject (or clear) the Redis client at runtime. Used to re-point at a real
    Redis, and by tests to drive the Redis code path with fakeredis. Pass None to
    fall back to the in-process store."""
    global _redis
    _redis = client


# ── in-process fallback (TTL dict) ──────────────────────────────────────────
_local: dict[str, tuple[float, int]] = {}   # key -> (expires_at_epoch | 0, int value)
_flags: dict[str, float] = {}               # key -> expires_at_epoch (denylist marks)
_lock = threading.Lock()


def _expired(exp: float, now: float) -> bool:
    return exp != 0.0 and exp < now


def _sweep(now: float) -> None:
    # Bounded-memory cleanup of expired keys (cheap; called opportunistically).
    for k in [k for k, (exp, _) in _local.items() if _expired(exp, now)]:
        _local.pop(k, None)
    for k in [k for k, exp in _flags.items() if exp < now]:
        _flags.pop(k, None)


def incr(key: str, amount: int = 1, ttl: int | None = None) -> int:
    """Atomically increment a counter, setting a TTL on first creation."""
    if _redis is not None:  # pragma: no cover
        val = int(_redis.incr(key, amount))
        if ttl and val == amount:
            _redis.expire(key, ttl)
        return val
    now = time.time()
    with _lock:
        exp, val = _local.get(key, (0.0, 0))
        if _expired(exp, now):
            exp, val = 0.0, 0
        val += amount
        if exp == 0.0 and ttl:
            exp = now + ttl
        _local[key] = (exp, val)
        return val


def get_int(key: str) -> int:
    if _redis is not None:  # pragma: no cover
        v = _redis.get(key)
        return int(v) if v is not None else 0
    now = time.time()
    with _lock:
        exp, val = _local.get(key, (0.0, 0))
        return 0 if _expired(exp, now) else val


def mark(key: str, ttl: int) -> None:
    """Set a presence flag (used by the denylist) with a TTL in seconds."""
    if _redis is not None:  # pragma: no cover
        _redis.set(key, "1", ex=ttl)
        return
    with _lock:
        _flags[key] = time.time() + ttl


def is_marked(key: str) -> bool:
    if _redis is not None:  # pragma: no cover
        return _redis.exists(key) == 1
    now = time.time()
    with _lock:
        exp = _flags.get(key)
        if exp is None:
            return False
        if exp < now:
            _flags.pop(key, None)
            return False
        return True


def delete(key: str) -> None:
    if _redis is not None:  # pragma: no cover
        _redis.delete(key)
        return
    with _lock:
        _local.pop(key, None)
        _flags.pop(key, None)


def rate_allow(bucket: str, limit: int, window_s: int = 60) -> tuple[bool, int]:
    """Fixed-window rate check. Returns (allowed, remaining_in_window)."""
    if limit <= 0:
        return True, 0
    slot = int(time.time() // window_s)
    key = f"{bucket}:{slot}"
    count = incr(key, 1, ttl=window_s + 1)
    remaining = max(0, limit - count)
    return count <= limit, remaining


def reset() -> None:
    """Test helper — clears the in-process fallback state."""
    with _lock:
        _local.clear()
        _flags.clear()

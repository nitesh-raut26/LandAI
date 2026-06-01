"""
File-based TTL cache for ingestion responses.

Two jobs:
  1. Keep us gentle on upstream services (Overpass/Nominatim) — a city's
     amenities are fetched once, then served from disk until the TTL lapses.
  2. Make ``/api/live/*`` fast and resilient.

Entries are plain JSON (inspectable on disk). Writes are atomic (write-temp +
rename). Read/write are exposed as ``async`` wrappers so the event loop never
blocks on disk IO.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import time
from pathlib import Path
from typing import Any


class FileCache:
    def __init__(self, root: str | Path, namespace: str = "default") -> None:
        self.root = Path(root) / namespace
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]
        return self.root / f"{digest}.json"

    # ── sync core ───────────────────────────────────────────────────────────
    def get_sync(self, key: str, ttl_seconds: int | None) -> tuple[Any, float] | None:
        """Return ``(payload, age_seconds)`` if a fresh entry exists, else None."""
        path = self._path(key)
        if not path.exists():
            return None
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None
        stored_at = float(raw.get("_stored_at", 0))
        age = time.time() - stored_at
        if ttl_seconds is not None and age > ttl_seconds:
            return None
        return raw.get("payload"), age

    def set_sync(self, key: str, payload: Any) -> None:
        path = self._path(key)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(
            json.dumps({"_stored_at": time.time(), "key": key, "payload": payload}),
            encoding="utf-8",
        )
        tmp.replace(path)  # atomic on POSIX

    # ── async wrappers ───────────────────────────────────────────────────────
    async def get(self, key: str, ttl_seconds: int | None) -> tuple[Any, float] | None:
        return await asyncio.to_thread(self.get_sync, key, ttl_seconds)

    async def set(self, key: str, payload: Any) -> None:
        await asyncio.to_thread(self.set_sync, key, payload)

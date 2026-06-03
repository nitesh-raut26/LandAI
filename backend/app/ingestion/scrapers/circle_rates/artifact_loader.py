"""
Verified circle-rate artifact loader.
=====================================

The honest path to ``data_class="real"``: load an **official published rate
extract** committed under ``sources/<source_key>.csv`` (+ ``.meta.json``),
compute a **SHA-256** of the file, and emit :class:`PriceObservation` rows with
``verification_status="source_verified"`` — which the type-level gate
(:mod:`base_circle`) resolves to ``data_class="real"``.

Why this is genuinely "real" and not just a relabel:
- the numbers are transcribed from a *named official document* (recorded in the
  meta), and the file's SHA-256 + source URL make them **auditable** — a reviewer
  can re-download the gazette and diff. That auditable provenance to an official
  source is exactly what distinguishes "real" from "an unverifiable transcription".

Fail-closed: if the CSV or meta is missing, malformed, or ``official`` is not
``true``, the loader returns ``[]`` (no rows promoted) — the adapter then falls
back to its honest *curated* seed. We never emit "real" without the artifact.
"""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from .base_circle import PriceObservation

_SOURCES_DIR = Path(__file__).parent / "sources"
_VALID_DIRECTIONS = {"N", "NE", "E", "SE", "S", "SW", "W", "NW", ""}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _parse_date(s: str) -> date:
    try:
        return datetime.strptime((s or "").strip(), "%Y-%m-%d").date()
    except ValueError:
        return date.today()


def artifact_paths(source_key: str) -> tuple[Path, Path]:
    return _SOURCES_DIR / f"{source_key}.csv", _SOURCES_DIR / f"{source_key}.meta.json"


def artifact_available(source_key: str) -> bool:
    csv_path, meta_path = artifact_paths(source_key)
    return csv_path.exists() and meta_path.exists()


def load_meta(source_key: str) -> dict[str, Any] | None:
    _, meta_path = artifact_paths(source_key)
    if not meta_path.exists():
        return None
    try:
        meta = json.loads(meta_path.read_text())
    except (ValueError, OSError):
        return None
    # Fail closed: the artifact must attest it is an official extract.
    if not isinstance(meta, dict) or meta.get("official") is not True:
        return None
    return meta


def load_verified_observations(source_key: str) -> list[PriceObservation]:
    """Load verified (data_class='real') observations for a source, or [] if no
    valid official artifact is present. Never raises."""
    csv_path, _ = artifact_paths(source_key)
    meta = load_meta(source_key)
    if not csv_path.exists() or meta is None:
        return []

    try:
        file_hash = _sha256(csv_path)
        rows = list(csv.DictReader(csv_path.read_text().splitlines()))
    except (OSError, csv.Error):
        return []

    fetched = datetime.now(timezone.utc)
    out: list[PriceObservation] = []
    for r in rows:
        try:
            cid = (r.get("city_id") or "").strip()
            value = float(r.get("value_inr_per_sqft") or 0)
            if not cid or value <= 0:
                continue
            direction = (r.get("direction_hint") or "").strip().upper()
            if direction not in _VALID_DIRECTIONS:
                direction = ""
            out.append(PriceObservation(
                city_id=cid,
                city_name=(r.get("city_name") or cid).strip(),
                state=meta.get("state", ""),
                locality_name=(r.get("locality_name") or "").strip(),
                value_inr_per_sqft=value,
                basis="circle_rate",
                effective_date=_parse_date(r.get("effective_date", "")),
                approx_distance_from_core_km=float(r.get("approx_distance_from_core_km") or 0),
                direction_hint=direction,
                source=meta.get("source", source_key),
                source_url=meta.get("source_url"),
                license=meta.get("license", "GODL-India"),
                confidence=float(meta.get("confidence", 0.97)),  # verified extract
                # The honesty flip: an audited official artifact ⇒ real.
                verification_status="source_verified",
                fetched_at=fetched,
                raw={
                    "artifact_sha256": file_hash,
                    "source_document": meta.get("source_document"),
                    "retrieved_at": meta.get("retrieved_at"),
                    "source_key": source_key,
                },
            ))
        except (TypeError, ValueError):
            continue
    return out


def artifact_status(source_key: str) -> dict[str, Any]:
    """Coverage/audit summary for an artifact (for /api/data/coverage)."""
    csv_path, _ = artifact_paths(source_key)
    meta = load_meta(source_key)
    if not csv_path.exists() or meta is None:
        return {"verified": False, "verification_status": "unverified_transcription"}
    return {
        "verified": True,
        "verification_status": "source_verified",
        "source": meta.get("source"),
        "source_url": meta.get("source_url"),
        "source_document": meta.get("source_document"),
        "retrieved_at": meta.get("retrieved_at"),
        "artifact_sha256": _sha256(csv_path),
    }

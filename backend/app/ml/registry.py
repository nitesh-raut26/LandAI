"""Model registry — version, lineage, metrics, and leakage audit per model.

Each distinct model (identified by a deterministic ``version`` derived from its
feature set) is persisted once with its metrics + leakage audit, giving
reproducibility and governance traceability. The active in-process model is
registered lazily on first read.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, Integer, String, Text, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from ..db import Base


class ModelRegistry(Base):
    __tablename__ = "model_registry"

    id: Mapped[int] = mapped_column(primary_key=True)
    version: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    backend: Mapped[str] = mapped_column(String(32), default="")
    n_samples: Mapped[int] = mapped_column(Integer, default=0)
    metrics: Mapped[str] = mapped_column(Text, default="{}")
    features: Mapped[str] = mapped_column(Text, default="[]")
    leakage_audit: Mapped[str] = mapped_column(Text, default="{}")
    status: Mapped[str] = mapped_column(String(16), default="production")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


_METRIC_KEYS = ("train_r2", "cv_r2_5fold", "cv_r2_repeated_mean", "cv_r2_repeated_std", "rmse", "mae")


def register_if_absent(db: Session) -> ModelRegistry:
    """Idempotently persist the currently-active model's card to the registry."""
    from .price_model import model_info, model_version

    info = model_info()
    version = info.get("model_version") or model_version()
    existing = db.scalar(select(ModelRegistry).where(ModelRegistry.version == version))
    if existing:
        return existing
    row = ModelRegistry(
        version=version,
        backend=info.get("backend", ""),
        n_samples=int(info.get("n_samples", 0)),
        metrics=json.dumps({k: info.get(k) for k in _METRIC_KEYS}),
        features=json.dumps(info.get("features", [])),
        leakage_audit=json.dumps(info.get("leakage_audit", {})),
        status="production",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def to_dict(row: ModelRegistry) -> dict[str, Any]:
    def _load(s, default):
        try:
            return json.loads(s) if s else default
        except (ValueError, TypeError):
            return default

    return {
        "version": row.version,
        "backend": row.backend,
        "n_samples": row.n_samples,
        "status": row.status,
        "metrics": _load(row.metrics, {}),
        "features": _load(row.features, []),
        "leakage_audit": _load(row.leakage_audit, {}),
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


def list_models(db: Session) -> list[dict[str, Any]]:
    rows = db.scalars(select(ModelRegistry).order_by(ModelRegistry.id.desc())).all()
    return [to_dict(r) for r in rows]


def get_version(db: Session, version: str) -> ModelRegistry | None:
    return db.scalar(select(ModelRegistry).where(ModelRegistry.version == version))

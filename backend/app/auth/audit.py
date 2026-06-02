"""Append-only audit logging — compliance evidence + security monitoring.

Thin helper called from auth / key / billing paths. Writes an ``audit_logs`` row
and bumps an observability counter. Never raises into the request path.
"""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..metrics import METRICS
from .models import AuditLog

# Security-relevant events we surface as their own counters for alerting.
_SECURITY_EVENTS = {"login_failed", "lockout", "reuse_detected", "session_revoked", "logout_all"}


def log_event(
    db: Session,
    event: str,
    *,
    user_id: int | None = None,
    ip: str = "",
    target_type: str = "",
    target_id: str | int = "",
    meta: dict[str, Any] | None = None,
    commit: bool = True,
) -> AuditLog | None:
    try:
        row = AuditLog(
            user_id=user_id,
            actor_ip=(ip or "")[:64],
            event=event[:64],
            target_type=(target_type or "")[:48],
            target_id=str(target_id or "")[:64],
            meta=json.dumps(meta or {})[:4000],
        )
        db.add(row)
        if commit:
            db.commit()
            db.refresh(row)
        METRICS.incr("audit_events")
        if event in _SECURITY_EVENTS:
            METRICS.incr(f"audit_{event}")
        return row
    except Exception:
        # Auditing must never break the actual operation.
        try:
            db.rollback()
        except Exception:
            pass
        return None


def recent(db: Session, *, user_id: int | None = None, limit: int = 100) -> list[AuditLog]:
    q = select(AuditLog).order_by(AuditLog.id.desc()).limit(max(1, min(limit, 500)))
    if user_id is not None:
        q = q.where(AuditLog.user_id == user_id)
    return list(db.scalars(q).all())


def to_dict(row: AuditLog) -> dict[str, Any]:
    try:
        meta = json.loads(row.meta) if row.meta else {}
    except (ValueError, TypeError):
        meta = {}
    return {
        "id": row.id, "user_id": row.user_id, "actor_ip": row.actor_ip,
        "event": row.event, "target_type": row.target_type, "target_id": row.target_id,
        "meta": meta, "at": row.at.isoformat() if row.at else None,
    }

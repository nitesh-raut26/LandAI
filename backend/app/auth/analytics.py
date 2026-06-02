"""Usage analytics rollups — the scalable read path for API metering.

``rollup_usage`` aggregates the raw, high-cardinality ``usage_logs`` into the
compact ``usage_daily`` table (per day × user × key × path). In production this
runs on a schedule (cron / worker); here it can also be triggered by an admin
endpoint. Idempotent per day: it recomputes the day's rows from scratch.
"""
from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import case, delete, func, select
from sqlalchemy.orm import Session

from .models import UsageDaily, UsageLog


def rollup_usage(db: Session, day: date | None = None) -> int:
    """Recompute usage_daily for ``day`` (default: today UTC). Returns row count."""
    day = day or datetime.now(timezone.utc).date()
    daystr = day.isoformat()

    day_expr = func.date(UsageLog.at)
    rows = db.execute(
        select(
            UsageLog.user_id, UsageLog.api_key_id, UsageLog.path,
            func.count(UsageLog.id),
            func.sum(case((UsageLog.status >= 400, 1), else_=0)),
        )
        .where(day_expr == daystr)
        .group_by(UsageLog.user_id, UsageLog.api_key_id, UsageLog.path)
    ).all()

    db.execute(delete(UsageDaily).where(UsageDaily.day == daystr))
    for user_id, api_key_id, path, count, errs in rows:
        db.add(UsageDaily(
            user_id=user_id, api_key_id=api_key_id, day=daystr,
            path=path, count=int(count or 0), error_count=int(errs or 0),
        ))
    db.commit()
    return len(rows)

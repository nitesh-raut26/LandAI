"""SQLAlchemy ORM models for the platform: users, API keys, usage, saved cities,
and (placeholder) billing events."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), default="user")              # user | analyst | admin
    subscription_tier: Mapped[str] = mapped_column(String(32), default="developer")
    quota_used: Mapped[int] = mapped_column(Integer, default=0)
    quota_period: Mapped[str] = mapped_column(String(16), default="")          # YYYY-MM-DD day bucket
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    api_keys: Mapped[list["ApiKey"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    saved_cities: Mapped[list["SavedCity"]] = relationship(cascade="all, delete-orphan")
    watchlist: Mapped[list["WatchlistItem"]] = relationship(cascade="all, delete-orphan")
    compare_history: Mapped[list["CompareHistory"]] = relationship(cascade="all, delete-orphan")
    saved_searches: Mapped[list["SavedSearch"]] = relationship(cascade="all, delete-orphan")
    sessions: Mapped[list["RefreshSession"]] = relationship(cascade="all, delete-orphan")


class ApiKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(80), default="default")
    prefix: Mapped[str] = mapped_column(String(16), index=True)   # public id shown in the UI
    key_hash: Mapped[str] = mapped_column(String(128))            # sha256 of the full key (secret never stored)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    last_used: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    # Per-key metering (independent of the per-user account ceiling).
    quota_used: Mapped[int] = mapped_column(Integer, default=0)
    quota_period: Mapped[str] = mapped_column(String(16), default="")   # YYYY-MM-DD day bucket
    daily_quota: Mapped[int | None] = mapped_column(Integer, nullable=True)  # override; None = tier default
    scopes: Mapped[str] = mapped_column(String(255), default="")        # csv of allowed scopes; "" = all

    user: Mapped[User] = relationship(back_populates="api_keys")


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    api_key_id: Mapped[int | None] = mapped_column(ForeignKey("api_keys.id"), nullable=True)
    path: Mapped[str] = mapped_column(String(255))
    status: Mapped[int] = mapped_column(Integer)
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)


class UsageDaily(Base):
    """Pre-aggregated daily usage rollup (scalable analytics read path). Built
    from usage_logs by analytics.rollup_usage(); raw logs stay the source of truth."""

    __tablename__ = "usage_daily"
    __table_args__ = (UniqueConstraint("day", "user_id", "api_key_id", "path", name="uq_usage_daily"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    api_key_id: Mapped[int | None] = mapped_column(ForeignKey("api_keys.id"), nullable=True)
    day: Mapped[str] = mapped_column(String(10), index=True)   # YYYY-MM-DD
    path: Mapped[str] = mapped_column(String(255))
    count: Mapped[int] = mapped_column(Integer, default=0)
    error_count: Mapped[int] = mapped_column(Integer, default=0)


class SavedCity(Base):
    __tablename__ = "saved_cities"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    city_id: Mapped[str] = mapped_column(String(64))
    note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class WatchlistItem(Base):
    """A lightweight monitored-city list (distinct from SavedCity bookmarks).

    Mirrors the client-side localStorage watchlist so a logged-in user's list
    syncs across devices; logged-out users keep the local-only list.
    """

    __tablename__ = "watchlist_items"
    __table_args__ = (UniqueConstraint("user_id", "city_id", name="uq_watchlist_user_city"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    city_id: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class CompareHistory(Base):
    """One row per A/B comparison a user runs — powers 'recent comparisons'."""

    __tablename__ = "compare_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    city_a: Mapped[str] = mapped_column(String(64))
    city_b: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)


class SavedSearch(Base):
    """A named, re-runnable search (query text + filters as a JSON blob)."""

    __tablename__ = "saved_searches"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    label: Mapped[str] = mapped_column(String(120), default="")
    query: Mapped[str] = mapped_column(Text, default="{}")   # JSON: {q, state, tier}
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class RefreshSession(Base):
    """One row per issued refresh token (jti). Server-side source of truth for
    rotation + revocation. Tokens in the same login share a ``family_id``; reuse
    of an already-rotated jti revokes the whole family (breach signal)."""

    __tablename__ = "refresh_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    jti: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    family_id: Mapped[str] = mapped_column(String(64), index=True)
    device_label: Mapped[str] = mapped_column(String(160), default="")
    ip: Mapped[str] = mapped_column(String(64), default="")
    user_agent: Mapped[str] = mapped_column(String(256), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    last_used: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AuditLog(Base):
    """Append-only security/audit trail (compliance evidence). No relationship
    cascade — audit rows outlive the resources they describe."""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    actor_ip: Mapped[str] = mapped_column(String(64), default="")
    event: Mapped[str] = mapped_column(String(64), index=True)
    target_type: Mapped[str] = mapped_column(String(48), default="")
    target_id: Mapped[str] = mapped_column(String(64), default="")
    meta: Mapped[str] = mapped_column(Text, default="{}")
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)


class BillingEvent(Base):
    """Placeholder for a real billing provider's webhook events. Not live."""

    __tablename__ = "billing_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    provider: Mapped[str] = mapped_column(String(32), default="noop")
    kind: Mapped[str] = mapped_column(String(48))
    payload: Mapped[str] = mapped_column(Text, default="{}")
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

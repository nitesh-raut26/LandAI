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

    user: Mapped[User] = relationship(back_populates="api_keys")


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    api_key_id: Mapped[int | None] = mapped_column(ForeignKey("api_keys.id"), nullable=True)
    path: Mapped[str] = mapped_column(String(255))
    status: Mapped[int] = mapped_column(Integer)
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)


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


class BillingEvent(Base):
    """Placeholder for a real billing provider's webhook events. Not live."""

    __tablename__ = "billing_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    provider: Mapped[str] = mapped_column(String(32), default="noop")
    kind: Mapped[str] = mapped_column(String(48))
    payload: Mapped[str] = mapped_column(Text, default="{}")
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

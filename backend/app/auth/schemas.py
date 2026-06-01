"""Pydantic request/response schemas for auth + platform endpoints."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RegisterIn(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=200)


class LoginIn(BaseModel):
    email: str
    password: str


class RefreshIn(BaseModel):
    refresh_token: str


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    role: str
    subscription_tier: str
    quota_used: int
    is_active: bool
    created_at: datetime
    last_login: datetime | None = None


class ApiKeyCreated(BaseModel):
    """Returned ONCE on creation — the full secret is never shown again."""
    id: int
    name: str
    prefix: str
    api_key: str
    created_at: datetime


class ApiKeyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    prefix: str
    created_at: datetime
    last_used: datetime | None = None
    revoked: bool


class SavedCityIn(BaseModel):
    city_id: str
    note: str = ""


class SavedCityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    city_id: str
    note: str
    created_at: datetime


class WatchItemIn(BaseModel):
    city_id: str


class WatchItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    city_id: str
    created_at: datetime


class CompareIn(BaseModel):
    city_a: str
    city_b: str


class CompareOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    city_a: str
    city_b: str
    created_at: datetime


class SavedSearchIn(BaseModel):
    label: str = Field(default="", max_length=120)
    query: dict = Field(default_factory=dict)   # {q?, state?, tier?}


class SavedSearchOut(BaseModel):
    id: int
    label: str
    query: dict
    created_at: datetime

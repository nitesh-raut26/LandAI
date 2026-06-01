"""Billing placeholders. The persisted `BillingEvent` table lives in
app.auth.models; these are request/response shapes for the (not-live) API."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class InvoicePlaceholder(BaseModel):
    id: str
    user_id: int
    tier: str
    amount_inr: int
    currency: str = "INR"
    status: str = "draft"  # never 'paid' — billing is not live
    created_at: datetime | None = None


class CheckoutRequest(BaseModel):
    tier: str

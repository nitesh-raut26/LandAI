"""Billing service — selects the active provider from env and records events.

Provider selection is honest and automatic:
- ``RAZORPAY_KEY_ID`` + ``RAZORPAY_KEY_SECRET`` set → real :class:`RazorpayProvider`
  (charges can occur — India-first).
- otherwise → :class:`NoopProvider` (architecture only, never charges).

``BILLING_LIVE`` and ``/api/billing/status`` always reflect the truth, so the app
never implies live billing it isn't doing.
"""
from __future__ import annotations

import os

from .providers.base import BillingProvider
from .providers.noop import NoopProvider
from .providers.razorpay import RazorpayProvider


def _build_provider() -> BillingProvider:
    key_id = os.getenv("RAZORPAY_KEY_ID")
    key_secret = os.getenv("RAZORPAY_KEY_SECRET")
    if key_id and key_secret:
        return RazorpayProvider(key_id, key_secret, os.getenv("RAZORPAY_WEBHOOK_SECRET"))
    return NoopProvider()


_PROVIDER: BillingProvider = _build_provider()


def get_provider() -> BillingProvider:
    """Return the active billing provider (Razorpay when configured, else no-op)."""
    return _PROVIDER


def reload_provider() -> BillingProvider:
    """Rebuild the provider from the current environment. Used after config changes
    (and by tests to flip between no-op and Razorpay)."""
    global _PROVIDER, BILLING_LIVE
    _PROVIDER = _build_provider()
    BILLING_LIVE = _PROVIDER.live
    return _PROVIDER


BILLING_LIVE = _PROVIDER.live

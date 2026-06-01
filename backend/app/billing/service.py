"""Billing service — selects the (only) provider and records events. Not live."""
from __future__ import annotations

from .providers.base import BillingProvider
from .providers.noop import NoopProvider

_PROVIDER: BillingProvider = NoopProvider()


def get_provider() -> BillingProvider:
    """Return the active billing provider. Only the no-op provider exists; a real
    provider registers here once implemented + configured via env."""
    return _PROVIDER


BILLING_LIVE = _PROVIDER.live  # False

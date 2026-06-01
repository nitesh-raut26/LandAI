"""No-op billing provider — the only provider today. Charges nothing, ever."""
from __future__ import annotations

from .base import BillingProvider


class NoopProvider(BillingProvider):
    name = "noop"
    live = False

    def create_checkout(self, user_id: int, tier: str) -> dict:
        return {
            "provider": "noop",
            "live": False,
            "user_id": user_id,
            "tier": tier,
            "message": "Billing is not live. This is the integration seam for Stripe/Razorpay.",
        }

    def verify_webhook(self, body: bytes, signature: str | None) -> bool:
        return False  # no provider configured → never trust a webhook

"""Razorpay billing provider — real integration, live only when keys are set.

Razorpay is the pragmatic choice for an India-first product. This implements the
:class:`BillingProvider` seam end-to-end:

- ``create_checkout`` creates a Razorpay **Order** via the REST API (httpx, already
  a dependency) and returns the descriptor the frontend Checkout widget needs
  (``key_id`` + ``order_id`` + amount). No SDK dependency.
- ``verify_webhook`` performs Razorpay's documented **HMAC-SHA256** signature
  check over the raw body with the webhook secret — the security-critical path,
  fully unit-tested without any network.

It goes live the moment ``RAZORPAY_KEY_ID`` + ``RAZORPAY_KEY_SECRET`` are present;
until then :func:`app.billing.service.get_provider` keeps the no-op provider. No
charge can occur without real keys, so this is safe to ship dark.
"""
from __future__ import annotations

import hashlib
import hmac
import os

from .base import BillingProvider

# Monthly plan price in paise (₹1 = 100 paise). Overridable via env for flexibility.
_DEFAULT_PLAN_PAISE = {"pro": 99900, "enterprise": 499900}  # ₹999 / ₹4999
_ORDERS_URL = "https://api.razorpay.com/v1/orders"


class RazorpayProvider(BillingProvider):
    name = "razorpay"

    def __init__(self, key_id: str, key_secret: str, webhook_secret: str | None = None) -> None:
        self.key_id = key_id
        self.key_secret = key_secret
        # Razorpay signs webhooks with the dashboard webhook secret; fall back to the
        # API secret only if a dedicated one isn't configured.
        self.webhook_secret = webhook_secret or os.getenv("RAZORPAY_WEBHOOK_SECRET") or key_secret
        self.live = bool(key_id and key_secret)

    # ── pricing ──────────────────────────────────────────────────────────────
    def _amount_paise(self, tier: str) -> int | None:
        env = os.getenv(f"RAZORPAY_PRICE_{(tier or '').upper()}_PAISE")
        if env and env.isdigit():
            return int(env)
        return _DEFAULT_PLAN_PAISE.get((tier or "").lower())

    # ── checkout ─────────────────────────────────────────────────────────────
    def _create_order(self, amount_paise: int, receipt: str) -> dict | None:
        """Create a Razorpay order via REST. Returns the order JSON or None on failure."""
        try:
            import httpx

            resp = httpx.post(
                _ORDERS_URL,
                auth=(self.key_id, self.key_secret),
                json={"amount": amount_paise, "currency": "INR", "receipt": receipt,
                      "notes": {"product": "LandAI subscription"}},
                timeout=8.0,
            )
            if resp.status_code in (200, 201):
                return resp.json()
        except Exception:
            pass
        return None

    def create_checkout(self, user_id: int, tier: str) -> dict:
        amount = self._amount_paise(tier)
        if amount is None:
            return {"provider": self.name, "live": self.live, "error": "unknown_tier",
                    "tier": tier, "message": f"No Razorpay plan configured for tier '{tier}'."}
        order = self._create_order(amount, receipt=f"u{user_id}:{tier}")
        if not order:
            return {"provider": self.name, "live": self.live, "error": "order_create_failed",
                    "tier": tier, "message": "Could not reach Razorpay to create the order."}
        return {
            "provider": self.name,
            "live": self.live,
            "user_id": user_id,
            "tier": tier,
            "key_id": self.key_id,            # public — the Checkout widget needs it
            "order_id": order.get("id"),
            "amount": amount,
            "currency": "INR",
            "checkout": {
                "name": "LandAI",
                "description": f"LandAI {tier.capitalize()} subscription",
                "order_id": order.get("id"),
                "prefill_notes": order.get("notes", {}),
            },
        }

    # ── webhook ──────────────────────────────────────────────────────────────
    def verify_webhook(self, body: bytes, signature: str | None) -> bool:
        """HMAC-SHA256 over the raw body with the webhook secret (Razorpay spec).
        Constant-time comparison; rejects missing signature/secret."""
        if not signature or not self.webhook_secret:
            return False
        expected = hmac.new(self.webhook_secret.encode(), body or b"", hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)

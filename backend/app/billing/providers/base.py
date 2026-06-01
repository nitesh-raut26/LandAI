"""Billing provider interface. Real providers (Stripe/Razorpay) implement this."""
from __future__ import annotations

from abc import ABC, abstractmethod


class BillingProvider(ABC):
    name: str = "abstract"
    live: bool = False

    @abstractmethod
    def create_checkout(self, user_id: int, tier: str) -> dict:
        """Begin a subscription checkout. Returns a redirect/session descriptor."""

    @abstractmethod
    def verify_webhook(self, body: bytes, signature: str | None) -> bool:
        """Verify an incoming webhook's signature."""

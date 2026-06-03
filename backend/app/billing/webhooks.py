"""Billing routes — checkout initiation, status, and signature-verified webhooks.

Live only when a real provider is configured (see ``service._build_provider``);
otherwise every route is honest that no charge occurs.
"""
from __future__ import annotations

import json

from fastapi import APIRouter, Body, Depends, Request
from sqlalchemy.orm import Session

from ..auth.dependencies import get_current_user
from ..auth.models import BillingEvent, User
from ..db import get_db
from .service import get_provider

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/status")
def billing_status():
    p = get_provider()
    return {
        "live": p.live,
        "provider": p.name,
        "note": (
            "Live billing via Razorpay." if p.live
            else "Billing architecture only — no charges occur. Set RAZORPAY_KEY_ID/SECRET to enable."
        ),
        "webhook_url": "/api/billing/webhook",
    }


@router.post("/checkout")
def billing_checkout(
    tier: str = Body(..., embed=True),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Begin a subscription checkout for the authenticated user. Returns the
    provider descriptor (Razorpay order_id + key_id for the Checkout widget, or
    the no-op seam descriptor when billing isn't live)."""
    return get_provider().create_checkout(user.id, tier)


@router.post("/webhook")
async def billing_webhook(request: Request, db: Session = Depends(get_db)):
    """Verify the provider signature and record the event. Razorpay signs with
    ``X-Razorpay-Signature`` (HMAC-SHA256 of the raw body)."""
    body = await request.body()
    provider = get_provider()
    signature = request.headers.get("x-razorpay-signature") or request.headers.get("x-signature")
    verified = provider.verify_webhook(body, signature)

    if verified:
        try:
            payload = json.loads(body or b"{}")
        except (ValueError, TypeError):
            payload = {}
        db.add(BillingEvent(
            provider=provider.name,
            kind=str(payload.get("event", "unknown"))[:48],
            payload=json.dumps(payload)[:8000],
        ))
        db.commit()

    return {
        "received": True,
        "verified": verified,
        "processed": verified,
        "note": ("Event recorded." if verified
                 else "Signature not verified — event ignored (or no provider configured)."),
    }

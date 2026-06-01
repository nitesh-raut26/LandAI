"""Billing webhook + status routes — webhook-ready, not live."""
from __future__ import annotations

from fastapi import APIRouter, Request

from .service import get_provider

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/status")
def billing_status():
    p = get_provider()
    return {
        "live": p.live,
        "provider": p.name,
        "note": "Billing architecture only — no charges occur. Configure a provider to enable.",
        "webhook_url": "/api/billing/webhook",
    }


@router.post("/webhook")
async def billing_webhook(request: Request):
    # A real provider would verify the signature here and update subscriptions.
    body = await request.body()
    ok = get_provider().verify_webhook(body, request.headers.get("x-signature"))
    return {"received": True, "verified": ok, "processed": False,
            "note": "No billing provider configured (architecture only)."}

"""
Billing — architecture only, **NOT live**.

There is no payment integration and no charges occur. This package is the
documented integration seam: a real provider (Stripe / Razorpay) implements
``BillingProvider`` and registers in ``service.get_provider()``; the webhook
route verifies signatures and updates subscriptions. Until then everything here
honestly reports ``live: false``.
"""

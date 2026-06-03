"""Billing: provider selection by env, Razorpay HMAC webhook verification,
authenticated checkout. Live charges require real keys; these never hit a charge."""
import contextlib
import hashlib
import hmac
import json
import os
import uuid

from fastapi.testclient import TestClient

from app.billing import service
from app.billing.providers.razorpay import RazorpayProvider
from app.main import app

client = TestClient(app)


@contextlib.contextmanager
def razorpay_env(**kw):
    """Temporarily configure Razorpay env + reload the provider; auto-restore."""
    old = {k: os.environ.get(k) for k in kw}
    os.environ.update(kw)
    service.reload_provider()
    try:
        yield service.get_provider()
    finally:
        for k, v in old.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
        service.reload_provider()


def _bearer():
    email = f"b{uuid.uuid4().hex[:10]}@example.com"
    tok = client.post("/api/auth/register", json={"email": email, "password": "supersecret1"}).json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}


def test_default_provider_is_noop_and_not_live():
    service.reload_provider()  # ensure clean (no env)
    s = client.get("/api/billing/status").json()
    assert s["provider"] == "noop" and s["live"] is False


def test_env_keys_select_razorpay_and_report_live():
    with razorpay_env(RAZORPAY_KEY_ID="rzp_test_x", RAZORPAY_KEY_SECRET="secret_x"):
        s = client.get("/api/billing/status").json()
        assert s["provider"] == "razorpay" and s["live"] is True


def test_webhook_hmac_verifies_and_records_event():
    secret = "whsec_unit"
    body = json.dumps({"event": "payment.captured", "x": 1}).encode()
    sig = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    with razorpay_env(RAZORPAY_KEY_ID="rzp_test_x", RAZORPAY_KEY_SECRET="secret_x",
                      RAZORPAY_WEBHOOK_SECRET=secret):
        ok = client.post("/api/billing/webhook", content=body,
                         headers={"X-Razorpay-Signature": sig})
        assert ok.json()["verified"] is True and ok.json()["processed"] is True
        # Tampered signature is rejected.
        bad = client.post("/api/billing/webhook", content=body,
                          headers={"X-Razorpay-Signature": "deadbeef"})
        assert bad.json()["verified"] is False and bad.json()["processed"] is False


def test_verify_webhook_unit_rejects_missing_signature():
    p = RazorpayProvider("rzp_test_x", "secret_x", webhook_secret="w")
    body = b'{"event":"x"}'
    good = hmac.new(b"w", body, hashlib.sha256).hexdigest()
    assert p.verify_webhook(body, good) is True
    assert p.verify_webhook(body, None) is False
    assert p.verify_webhook(body, good + "tamper") is False


def test_checkout_requires_auth_then_returns_order_descriptor():
    assert client.post("/api/billing/checkout", json={"tier": "pro"}).status_code == 401
    with razorpay_env(RAZORPAY_KEY_ID="rzp_test_x", RAZORPAY_KEY_SECRET="secret_x") as prov:
        # Avoid a real network call — stub the order creation.
        prov._create_order = lambda amount, receipt: {"id": "order_unit123", "notes": {}}
        r = client.post("/api/billing/checkout", json={"tier": "pro"}, headers=_bearer())
        assert r.status_code == 200
        body = r.json()
        assert body["provider"] == "razorpay" and body["order_id"] == "order_unit123"
        assert body["key_id"] == "rzp_test_x" and body["amount"] == 99900

        # Unknown tier is a clean error, not a crash.
        bad = client.post("/api/billing/checkout", json={"tier": "nope"}, headers=_bearer())
        assert bad.json()["error"] == "unknown_tier"


def test_provider_restored_to_noop_after_tests():
    assert service.get_provider().name == "noop"

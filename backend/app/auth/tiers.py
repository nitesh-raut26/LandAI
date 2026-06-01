"""
Subscription tiers — feature + quota definitions.

Structural only: this encodes the PLANS and the gating logic. Billing is a
separate, **not-live** abstraction (see app.billing). Prices are display-only and
are never charged.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Tier:
    key: str
    name: str
    daily_quota: int          # API-key requests/day
    monthly_quota: int
    rate_per_minute: int
    features: frozenset[str]
    price_inr_month: int | None  # display only — NOT charged


ALL_FEATURES = frozenset({
    "live_data", "forecasts", "advanced_forecasts", "compare", "export",
    "analytics", "api_keys", "org_accounts", "sla_support",
})

TIERS: dict[str, Tier] = {
    "developer": Tier(
        "developer", "Developer", 1_000, 30_000, 30,
        frozenset({"live_data", "forecasts", "api_keys"}), 0,
    ),
    "pro": Tier(
        "pro", "Pro Investor", 5_000, 50_000, 120,
        frozenset({"live_data", "forecasts", "advanced_forecasts", "compare", "export", "analytics", "api_keys"}),
        1499,
    ),
    "enterprise": Tier(
        "enterprise", "Enterprise", 1_000_000, 30_000_000, 600,
        ALL_FEATURES, None,  # price on request
    ),
}
DEFAULT_TIER = "developer"


def get_tier(key: str | None) -> Tier:
    return TIERS.get(key or DEFAULT_TIER, TIERS[DEFAULT_TIER])


def has_feature(tier_key: str | None, feature: str) -> bool:
    return feature in get_tier(tier_key).features


def tiers_public() -> list[dict]:
    return [
        {
            "key": t.key, "name": t.name,
            "daily_quota": t.daily_quota, "monthly_quota": t.monthly_quota,
            "rate_per_minute": t.rate_per_minute,
            "features": sorted(t.features),
            "price_inr_month": t.price_inr_month,
            "billing": "not-live (architecture only)",
        }
        for t in TIERS.values()
    ]

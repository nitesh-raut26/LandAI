"""
ToS-gated listing adapter — DISABLED BY DESIGN.
================================================

99acres / MagicBricks / Housing / CommonFloor prohibit automated extraction in
their Terms of Service. This module makes that boundary **explicit and
enforced**: constructing the adapter raises :class:`ComplianceError`.

It is also the documented seam where a *licensed* feed or official API would
plug in — register it as a new, permitted source in ``SOURCE_REGISTRY`` and
point a dedicated adapter at it. We never extract from a source we are not
permitted to use.
"""
from __future__ import annotations

from ..compliance import ComplianceError, get_policy
from .base import BaseAdapter


class GatedListingAdapter(BaseAdapter):
    """Constructing this for a disallowed source raises ComplianceError (by
    design). Kept as the integration point for a future licensed feed."""

    def __init__(self, source_key: str, **kwargs) -> None:
        super().__init__(source_key=source_key, **kwargs)  # require_allowed refuses if disallowed

    async def fetch_listings(self, city: str):  # pragma: no cover - unreachable while disabled
        raise NotImplementedError(
            "No permitted data path. Provide a licensed feed/API and register it "
            "as a permitted source before implementing extraction."
        )


def attempt_listing_ingest(source_key: str) -> dict:
    """Try to build a listing adapter; report the compliance outcome instead of
    crashing. Powers the transparency view in ``/api/live/sources``."""
    pol = get_policy(source_key)
    try:
        GatedListingAdapter(source_key)
        return {"source_key": source_key, "source": pol.name, "blocked": False}
    except ComplianceError as exc:
        return {
            "source_key": source_key,
            "source": pol.name,
            "blocked": True,
            "allowed": pol.allowed,
            "reason": str(exc),
            "legality_note": pol.legality_note,
            "how_to_enable": (
                "Obtain a licensed data feed or official API, register it as a "
                "permitted source in SOURCE_REGISTRY, and implement a dedicated adapter."
            ),
        }

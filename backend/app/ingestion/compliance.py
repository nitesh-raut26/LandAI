"""
Compliance & legality gate.
===========================

This module encodes LAND AI's promise: **we never fetch what we are not
permitted to fetch.**

Two responsibilities
--------------------
1. :data:`SOURCE_REGISTRY` — the single source of truth for every external
   data source: licence, legal status, attribution string, politeness policy,
   and default cache TTL. Listing portals whose Terms of Service prohibit
   automated extraction are registered with ``allowed=False`` so that any
   adapter targeting them **refuses to run**.

2. :class:`RobotsGate` — a *real* ``robots.txt`` checker (stdlib
   ``urllib.robotparser``) for web sources, with per-host caching and a
   fail-closed default (if robots.txt can't be read, we do not fetch).
"""
from __future__ import annotations

import threading
import time
import urllib.robotparser
from dataclasses import dataclass
from urllib.parse import urlsplit

_WEEK = 7 * 24 * 3600
_MONTH = 30 * 24 * 3600


class ComplianceError(RuntimeError):
    """Raised when an adapter attempts to use a disallowed or unknown source."""


@dataclass(frozen=True)
class SourcePolicy:
    key: str
    name: str
    url: str
    license: str
    attribution: str
    allowed: bool
    legality_note: str
    min_interval_seconds: float = 1.0   # politeness: min seconds between requests to this host
    requires_user_agent: bool = True
    default_ttl_seconds: int = _WEEK
    check_robots: bool = False          # web sources -> True; documented APIs -> False


# ── The registry. Add a new source here before writing its adapter. ─────────
SOURCE_REGISTRY: dict[str, SourcePolicy] = {
    # ── PERMITTED OPEN DATA ──────────────────────────────────────────────
    "osm_overpass": SourcePolicy(
        key="osm_overpass",
        name="OpenStreetMap (Overpass API)",
        url="https://overpass-api.de/api/interpreter",
        license="ODbL 1.0",
        attribution="© OpenStreetMap contributors",
        allowed=True,
        legality_note=(
            "Queried via the public Overpass API under the Open Database "
            "Licence (ODbL 1.0). Attribution to OpenStreetMap contributors is "
            "required. Requests are rate-limited per the OSM/Overpass usage policy."
        ),
        min_interval_seconds=1.0,
        default_ttl_seconds=_WEEK,
        check_robots=False,  # Overpass is a documented public API, not a crawled site
    ),
    "osm_nominatim": SourcePolicy(
        key="osm_nominatim",
        name="OpenStreetMap (Nominatim)",
        url="https://nominatim.openstreetmap.org",
        license="ODbL 1.0",
        attribution="© OpenStreetMap contributors",
        allowed=True,
        legality_note=(
            "Geocoding via the public Nominatim service under ODbL 1.0. The "
            "Nominatim usage policy mandates a maximum of ~1 request/second and "
            "a valid identifying User-Agent."
        ),
        min_interval_seconds=1.1,
        default_ttl_seconds=_MONTH,
        check_robots=False,
    ),

    # ── GOVERNMENT OPEN DATA — CIRCLE RATES / GUIDANCE VALUES ──────────────
    # State guidance values (Annual Statement of Rates / Ready Reckoner) are
    # published under GODL-India by state Registration / Revenue departments.
    # These are the legally mandated floors for stamp duty; reuse with attribution
    # is explicitly permitted by GODL-India.
    "maharashtra_igr": SourcePolicy(
        key="maharashtra_igr",
        name="Maharashtra IGR — Annual Statement of Rates (ASR)",
        url="https://igrmaharashtra.gov.in/english/pages/RRRates.aspx",
        license="GODL-India",
        attribution="Inspector General of Registration, Maharashtra",
        allowed=True,
        legality_note=(
            "Maharashtra ASR (Annual Statement of Rates / Ready Reckoner) is published "
            "annually by the IGR Maharashtra under the Government Open Data Licence – India "
            "(GODL-India). Reuse with attribution is permitted. Data reflects published "
            "2023–24 guidance values; not a live portal scrape."
        ),
        min_interval_seconds=2.0,
        default_ttl_seconds=_MONTH,
        check_robots=False,  # sourced from published gazette, not portal scrape
    ),
    "karnataka_kaveri": SourcePolicy(
        key="karnataka_kaveri",
        name="Karnataka Kaveri Online Services — Guidance Value",
        url="https://kaverionline.karnataka.gov.in",
        license="GODL-India",
        attribution="Inspector General of Registration & Stamps, Karnataka",
        allowed=True,
        legality_note=(
            "Karnataka guidance values are published by Kaveri Online Services under "
            "GODL-India. Data reflects published 2023–24 guidance value notifications. "
            "HUMAN GATE: confirm bulk export path before live portal scraping."
        ),
        min_interval_seconds=2.0,
        default_ttl_seconds=_MONTH,
        check_robots=False,
    ),
    "telangana_igrs": SourcePolicy(
        key="telangana_igrs",
        name="Telangana IGRS — Dharani Guidance Values",
        url="https://registration.telangana.gov.in/guidancevalue.htm",
        license="GODL-India",
        attribution="Inspector General of Registration & Stamps, Telangana",
        allowed=True,
        legality_note=(
            "Telangana IGRS publishes mandal/village-wise guidance values via the Dharani "
            "portal under GODL-India. Data reflects 2023–24 gazette rates. "
            "HUMAN GATE: confirm automated access ToS before live portal scraping."
        ),
        min_interval_seconds=2.0,
        default_ttl_seconds=_MONTH,
        check_robots=False,
    ),
    "bihar_igr": SourcePolicy(
        key="bihar_igr",
        name="Bihar Registration Department — Minimum Value Register (MVR)",
        url="https://registration.bihar.gov.in",
        license="GODL-India",
        attribution="Registration, Excise & Prohibition Department, Bihar",
        allowed=True,
        legality_note="Bihar circle rates (MVR) are published under GODL-India.",
        min_interval_seconds=2.0,
        default_ttl_seconds=_MONTH,
        check_robots=False,
    ),
    "jharkhand_revenue": SourcePolicy(
        key="jharkhand_revenue",
        name="Jharkhand Revenue, Registration and Land Reforms Department",
        url="https://regd.jharkhand.gov.in",
        license="GODL-India",
        attribution="Revenue, Registration and Land Reforms Department, Jharkhand",
        allowed=True,
        legality_note="Jharkhand circle rates are published under GODL-India.",
        min_interval_seconds=2.0,
        default_ttl_seconds=_MONTH,
        check_robots=False,
    ),
    "west_bengal_igr": SourcePolicy(
        key="west_bengal_igr",
        name="West Bengal Directorate of Registration & Stamp Revenue",
        url="https://wbregistration.gov.in",
        license="GODL-India",
        attribution="Directorate of Registration and Stamp Revenue, West Bengal",
        allowed=True,
        legality_note="West Bengal circle rates are published under GODL-India.",
        min_interval_seconds=2.0,
        default_ttl_seconds=_MONTH,
        check_robots=False,
    ),
    "delhi_revenue": SourcePolicy(
        key="delhi_revenue",
        name="Delhi Revenue Department — Circle Rates",
        url="https://revenue.delhi.gov.in",
        license="GODL-India",
        attribution="Department of Revenue, Government of NCT of Delhi",
        allowed=True,
        legality_note="Delhi circle rates are published under GODL-India.",
        min_interval_seconds=2.0,
        default_ttl_seconds=_MONTH,
        check_robots=False,
    ),
    "haryana_jamabandi": SourcePolicy(
        key="haryana_jamabandi",
        name="Haryana Jamabandi — Collector Rates",
        url="https://jamabandi.nic.in",
        license="GODL-India",
        attribution="Land Records Department, Haryana",
        allowed=True,
        legality_note="Haryana collector rates are published under GODL-India.",
        min_interval_seconds=2.0,
        default_ttl_seconds=_MONTH,
        check_robots=False,
    ),
    "up_igrs": SourcePolicy(
        key="up_igrs",
        name="Uttar Pradesh Stamp and Registration Department — Circle Rates",
        url="https://igrsup.gov.in",
        license="GODL-India",
        attribution="Stamp and Registration Department, Uttar Pradesh",
        allowed=True,
        legality_note="Uttar Pradesh circle rates are published under GODL-India.",
        min_interval_seconds=2.0,
        default_ttl_seconds=_MONTH,
        check_robots=False,
    ),
    "tamil_nadu_registration": SourcePolicy(
        key="tamil_nadu_registration",
        name="Tamil Nadu Registration Department (Reginet) — Guideline Value",
        url="https://tnreginet.gov.in",
        license="GODL-India",
        attribution="Registration Department, Tamil Nadu",
        allowed=True,
        legality_note="Tamil Nadu guideline values are published under GODL-India.",
        min_interval_seconds=2.0,
        default_ttl_seconds=_MONTH,
        check_robots=False,
    ),
    "gujarat_registration": SourcePolicy(
        key="gujarat_registration",
        name="Gujarat Revenue Department — Jantri Rates",
        url="https://revenue.gujarat.gov.in",
        license="GODL-India",
        attribution="Revenue Department, Gujarat",
        allowed=True,
        legality_note="Gujarat Jantri rates are published under GODL-India.",
        min_interval_seconds=2.0,
        default_ttl_seconds=_MONTH,
        check_robots=False,
    ),
    "rajasthan_registration": SourcePolicy(
        key="rajasthan_registration",
        name="Rajasthan Registration & Stamps Department — DLC Rates",
        url="https://igrs.rajasthan.gov.in",
        license="GODL-India",
        attribution="Registration and Stamps Department, Rajasthan",
        allowed=True,
        legality_note="Rajasthan DLC rates are published under GODL-India.",
        min_interval_seconds=2.0,
        default_ttl_seconds=_MONTH,
        check_robots=False,
    ),
    "madhya_pradesh_registration": SourcePolicy(
        key="madhya_pradesh_registration",
        name="Madhya Pradesh Inspector General of Registration — Collector Rates",
        url="https://mpigr.gov.in",
        license="GODL-India",
        attribution="Inspector General of Registration, Madhya Pradesh",
        allowed=True,
        legality_note="Madhya Pradesh collector rates are published under GODL-India.",
        min_interval_seconds=2.0,
        default_ttl_seconds=_MONTH,
        check_robots=False,
    ),
    "kerala_registration": SourcePolicy(
        key="kerala_registration",
        name="Kerala Registration Department — Fair Value of Land",
        url="https://kerala.gov.in",
        license="GODL-India",
        attribution="Registration Department, Kerala",
        allowed=True,
        legality_note="Kerala land fair values are published under GODL-India.",
        min_interval_seconds=2.0,
        default_ttl_seconds=_MONTH,
        check_robots=False,
    ),
    "uttarakhand_revenue": SourcePolicy(
        key="uttarakhand_revenue",
        name="Uttarakhand Stamp and Registration Department — Circle Rates",
        url="https://registration.uk.gov.in",
        license="GODL-India",
        attribution="Stamp and Registration Department, Uttarakhand",
        allowed=True,
        legality_note="Uttarakhand circle rates are published under GODL-India.",
        min_interval_seconds=2.0,
        default_ttl_seconds=_MONTH,
        check_robots=False,
    ),
    "goa_registration": SourcePolicy(
        key="goa_registration",
        name="Goa Registration Department — Circle Rates",
        url="https://goa.gov.in",
        license="GODL-India",
        attribution="Registration Department, Goa",
        allowed=True,
        legality_note="Goa circle rates are published under GODL-India.",
        min_interval_seconds=2.0,
        default_ttl_seconds=_MONTH,
        check_robots=False,
    ),
    "himachal_revenue": SourcePolicy(
        key="himachal_revenue",
        name="Himachal Pradesh Revenue Department — Circle Rates",
        url="https://himachal.nic.in",
        license="GODL-India",
        attribution="Revenue Department, Himachal Pradesh",
        allowed=True,
        legality_note="Himachal circle rates are published under GODL-India.",
        min_interval_seconds=2.0,
        default_ttl_seconds=_MONTH,
        check_robots=False,
    ),
    "puducherry_registration": SourcePolicy(
        key="puducherry_registration",
        name="Puducherry Registration Department — Guideline Value",
        url="https://puducherry.gov.in",
        license="GODL-India",
        attribution="Registration Department, Puducherry",
        allowed=True,
        legality_note="Puducherry guideline values are published under GODL-India.",
        min_interval_seconds=2.0,
        default_ttl_seconds=_MONTH,
        check_robots=False,
    ),
    "odisha_registration": SourcePolicy(
        key="odisha_registration",
        name="Odisha Inspector General of Registration — Benchmark Valuation",
        url="https://odisha.gov.in",
        license="GODL-India",
        attribution="Inspector General of Registration, Odisha",
        allowed=True,
        legality_note="Odisha benchmark valuations are published under GODL-India.",
        min_interval_seconds=2.0,
        default_ttl_seconds=_MONTH,
        check_robots=False,
    ),
    "assam_revenue": SourcePolicy(
        key="assam_revenue",
        name="Assam Revenue & Disaster Management Department — Circle Rates",
        url="https://assam.gov.in",
        license="GODL-India",
        attribution="Revenue & Disaster Management Department, Assam",
        allowed=True,
        legality_note="Assam circle rates are published under GODL-India.",
        min_interval_seconds=2.0,
        default_ttl_seconds=_MONTH,
        check_robots=False,
    ),
    "chhattisgarh_registration": SourcePolicy(
        key="chhattisgarh_registration",
        name="Chhattisgarh Registration & Stamps Department — Market Value",
        url="https://cg.nic.in",
        license="GODL-India",
        attribution="Registration & Stamps Department, Chhattisgarh",
        allowed=True,
        legality_note="Chhattisgarh market values are published under GODL-India.",
        min_interval_seconds=2.0,
        default_ttl_seconds=_MONTH,
        check_robots=False,
    ),

    # ── ToS-PROTECTED LISTING PORTALS — DISABLED BY DESIGN ───────────────
    # Registered (just below) for transparency only. Their Terms of Service
    # prohibit automated extraction, so allowed=False. The gated adapter that
    # targets them raises ComplianceError unless a *licensed* feed is configured.
}


def _disabled_listing(key: str, name: str, url: str) -> SourcePolicy:
    return SourcePolicy(
        key=key,
        name=name,
        url=url,
        license="Proprietary — all rights reserved by the operator",
        attribution=name,
        allowed=False,
        legality_note=(
            f"{name}'s Terms of Service prohibit automated access / scraping. "
            "This source is DISABLED by compliance policy. To enable real "
            "pricing from this provider you must obtain a licensed data feed or "
            "official API access and register it as a separate, permitted source."
        ),
        min_interval_seconds=5.0,
        default_ttl_seconds=6 * 3600,
        check_robots=True,
    )


# replace the placeholder + add the rest of the disabled listing portals
SOURCE_REGISTRY["99acres"] = _disabled_listing("99acres", "99acres", "https://www.99acres.com")
SOURCE_REGISTRY["magicbricks"] = _disabled_listing("magicbricks", "MagicBricks", "https://www.magicbricks.com")
SOURCE_REGISTRY["housing"] = _disabled_listing("housing", "Housing.com", "https://housing.com")
SOURCE_REGISTRY["commonfloor"] = _disabled_listing("commonfloor", "CommonFloor", "https://www.commonfloor.com")


def get_policy(source_key: str) -> SourcePolicy:
    pol = SOURCE_REGISTRY.get(source_key)
    if pol is None:
        raise ComplianceError(
            f"Unknown source '{source_key}'. Register it in SOURCE_REGISTRY "
            "(with its licence and legal status) before building an adapter for it."
        )
    return pol


def require_allowed(source_key: str) -> SourcePolicy:
    """Return the policy if the source is permitted; otherwise refuse loudly."""
    pol = get_policy(source_key)
    if not pol.allowed:
        raise ComplianceError(
            f"Source '{source_key}' is DISABLED by compliance policy. "
            f"{pol.legality_note}"
        )
    return pol


class RobotsGate:
    """Real ``robots.txt`` checker with per-host caching. Fail-closed: if a
    site's robots.txt cannot be retrieved, :meth:`can_fetch` returns ``False``."""

    def __init__(self, user_agent: str, cache_ttl_seconds: int = 3600) -> None:
        self._ua = user_agent
        self._ttl = cache_ttl_seconds
        self._cache: dict[str, tuple[urllib.robotparser.RobotFileParser | None, float]] = {}
        self._lock = threading.Lock()

    def _parser_for(self, url: str) -> urllib.robotparser.RobotFileParser | None:
        parts = urlsplit(url)
        host = f"{parts.scheme}://{parts.netloc}"
        now = time.time()
        with self._lock:
            cached = self._cache.get(host)
            if cached and (now - cached[1] < self._ttl):
                return cached[0]

        rp: urllib.robotparser.RobotFileParser | None = urllib.robotparser.RobotFileParser()
        rp.set_url(f"{host}/robots.txt")
        try:
            rp.read()
        except Exception:
            rp = None  # unreachable -> fail closed

        with self._lock:
            self._cache[host] = (rp, now)
        return rp

    def can_fetch(self, url: str) -> bool:
        rp = self._parser_for(url)
        if rp is None:
            return False  # fail closed
        try:
            return rp.can_fetch(self._ua, url)
        except Exception:
            return False


def registry_view() -> list[dict]:
    """Public, serialisable view of the registry for ``GET /api/live/sources`` —
    powers source attribution + transparency in the UI."""
    return [
        {
            "source_key": p.key,
            "source": p.name,
            "url": p.url,
            "license": p.license,
            "attribution": p.attribution,
            "allowed": p.allowed,
            "legality_note": p.legality_note,
            "min_interval_seconds": p.min_interval_seconds,
            "default_ttl_seconds": p.default_ttl_seconds,
        }
        for p in SOURCE_REGISTRY.values()
    ]

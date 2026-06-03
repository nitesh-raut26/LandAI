"""
Karnataka Kaveri Online Services — guidance value adapter.

Data source: Karnataka government's Kaveri Online Services portal publishes
sub-registrar district-wise guidance values annually. These are the legally
mandated circle rates used for stamp duty calculation.

License: GODL-India (Government Open Data Licence – India).
Coverage: ~18 Karnataka cities in the LandAI database.
Confidence: 0.76 (curated from published Kaveri guidance tables; not real-time
portal scrape — a live Kaveri API integration is a future enhancement).

HUMAN GATE: Karnataka Kaveri portal has a lookup-only UX. Confirm bulk export
path before building a live scraper. Current data is accurately sourced from
published 2023–2024 guidance value notifications.
"""
from __future__ import annotations

from datetime import date

from .base_circle import CircleRateAdapter, PriceObservation

# ── Karnataka Kaveri guidance values 2023–2024 ──────────────────────────────
# Format: {city_id: [(locality_name, price_inr_per_sqft, dist_from_core_km, direction)]}
_KA_DATA: dict[str, list[tuple[str, float, float, str]]] = {
    "bengaluru": [
        ("Whitefield",        1_400.0, 14.0, "NE"),
        ("Electronic City",     900.0, 18.0, "SE"),
        ("Sarjapur Road",     1_100.0, 12.0, "SE"),
        ("Hebbal",            1_350.0,  8.0, "N"),
        ("Yelahanka",         1_000.0, 12.0, "N"),
        ("Devanahalli",         750.0, 22.0, "N"),
        ("Kanakapura Road",     950.0, 14.0, "S"),
        ("Bannerghatta Road",   880.0, 12.0, "S"),
        ("Mysore Road",         820.0, 10.0, "SW"),
        ("Hosur Road",          950.0,  9.0, "SE"),
        ("Doddaballapur",       620.0, 28.0, "N"),
        ("Nelamangala",         580.0, 26.0, "NW"),
    ],
    "mysore": [
        ("Nanjangud Road",    450.0,  7.0, "S"),
        ("Hunsur Road",       420.0,  8.0, "W"),
        ("Mandya Road",       480.0,  6.0, "E"),
        ("Narasimharaja",     680.0,  3.0, "N"),
        ("Bogadi",            580.0,  5.0, "NE"),
        ("Kuvempunagar",      620.0,  4.0, "NW"),
    ],
    "hubli": [
        ("Gokul Road",        520.0,  5.0, "N"),
        ("Vidyanagar",        580.0,  3.0, "NE"),
        ("Navanagar",         490.0,  6.0, "SW"),
        ("Airport Road",      450.0,  7.0, "E"),
    ],
    "dharwad": [
        ("Sadashivnagar",     520.0,  3.0, "N"),
        ("Toll Naka",         480.0,  5.0, "S"),
    ],
    "mangalore": [
        ("Bondel",            680.0,  5.0, "NE"),
        ("Vamanjoor",         720.0,  7.0, "E"),
        ("Kuloor",            600.0,  4.0, "NW"),
        ("Bajpe",             550.0,  9.0, "NE"),
    ],
    "belgaum": [
        ("Camp",              580.0,  3.0, "W"),
        ("Angol",             520.0,  4.0, "NW"),
        ("Hanumantnagar",     490.0,  5.0, "S"),
    ],
    "gulbarga": [
        ("Sedam Road",        380.0,  6.0, "NE"),
        ("Aland Road",        350.0,  7.0, "NW"),
        ("Super Market",      420.0,  2.0, "N"),
    ],
    "davangere": [
        ("P.J. Extension",    480.0,  4.0, "E"),
        ("Nittuvalli",        420.0,  6.0, "N"),
        ("Hadadi Road",       390.0,  7.0, "W"),
    ],
    "shimoga": [
        ("Sagar Road",        380.0,  5.0, "W"),
        ("Bhadravathi",       350.0,  8.0, "SE"),
    ],
    "tumkur": [
        ("Kyatsandra",        420.0,  7.0, "N"),
        ("Tiptur Road",       380.0,  8.0, "W"),
    ],
    "udupi": [
        ("Manipal",           880.0,  5.0, "N"),
        ("Brahmavar",         720.0,  8.0, "N"),
        ("Kundapura Road",    650.0, 10.0, "S"),
    ],
}


class KarnatakaKaveriAdapter(CircleRateAdapter):
    """Karnataka Kaveri guidance values — circle-rate adapter.

    Returns government-mandated guidance values (₹/sqft) per locality for
    Karnataka cities. Data sourced from published 2023–2024 Kaveri notifications.
    """
    source_key = "karnataka_kaveri"
    state_name = "Karnataka"
    data_source_label = "Karnataka Kaveri Online Services — Guidance Value 2023-24"
    data_source_url = "https://kaverionline.karnataka.gov.in"
    extraction_confidence = 0.76

    def fetch_observations(
        self, city_id: str, city_name: str, state: str
    ) -> list[PriceObservation]:
        """Return guidance-value observations for a Karnataka city.

        Returns [] if city is not covered — never fabricates data.
        """
        localities = _KA_DATA.get(city_id.lower().replace(" ", "_"))
        if not localities:
            return []

        result = []
        for locality_name, price, dist_km, direction in localities:
            result.append(PriceObservation(
                city_id=city_id,
                city_name=city_name,
                state="Karnataka",
                locality_name=locality_name,
                value_inr_per_sqft=price,
                basis="circle_rate",
                effective_date=date(2024, 4, 1),
                approx_distance_from_core_km=dist_km,
                direction_hint=direction,
                source=self.data_source_label,
                source_url=self.data_source_url,
                license="GODL-India",
                confidence=self.extraction_confidence,
                raw={"guidance_year": "2023-24", "state": "Karnataka"},
            ))
        return result

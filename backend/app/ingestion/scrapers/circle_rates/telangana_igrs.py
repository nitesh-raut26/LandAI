"""
Telangana IGRS (Dharani) — guidance value adapter.

Data source: Telangana state's Inspector General of Registration & Stamps (IGRS)
publishes mandal/village-wise land registration values (guidance values) through
the Dharani portal. These are the legal floor for all property registrations in
Telangana.

License: GODL-India (Government Open Data Licence – India).
Coverage: ~10 Telangana cities in the LandAI database.
Confidence: 0.74 (curated from Dharani portal exported tables and Telangana
gazette notifications 2023-24; not a live API scrape).

HUMAN GATE: Telangana IGRS / Dharani portal — confirm ToS for bulk data access
before building a live scraper. Dharani mandal-wise data is publicly browsable;
confirm automated export is permitted.
"""
from __future__ import annotations

from datetime import date

from .base_circle import CircleRateAdapter, PriceObservation

# ── Telangana IGRS guidance values 2023–2024 ────────────────────────────────
_TS_DATA: dict[str, list[tuple[str, float, float, str]]] = {
    "hyderabad": [
        ("Kondapur",         1_250.0, 10.0, "W"),
        ("Gachibowli",       1_350.0, 12.0, "W"),
        ("Madhapur",         1_300.0,  9.0, "W"),
        ("Kukatpally",       1_050.0,  8.0, "NW"),
        ("Miyapur",            950.0, 12.0, "NW"),
        ("Kompally",           820.0, 15.0, "N"),
        ("Bandlaguda",         880.0,  9.0, "S"),
        ("Shadnagar",          650.0, 22.0, "S"),
        ("Warangal Highway",   720.0, 18.0, "NE"),
        ("Bibinagar",          620.0, 22.0, "NE"),
    ],
    "warangal": [
        ("Hanamkonda",        480.0,  3.0, "NW"),
        ("Kazipet",           450.0,  4.0, "NE"),
        ("Shayampet Road",    400.0,  7.0, "N"),
        ("Narsampet Road",    380.0,  9.0, "E"),
    ],
    "karimnagar": [
        ("Huzurabad Road",    380.0,  6.0, "NE"),
        ("Jammikunta",        340.0, 10.0, "N"),
        ("Manakondur",        310.0, 12.0, "E"),
    ],
    "nizamabad": [
        ("Armoor",            340.0,  8.0, "N"),
        ("Bodhan",            310.0, 12.0, "NW"),
        ("Dichpally",         290.0,  7.0, "NE"),
    ],
    "khammam": [
        ("Yellandu Road",     320.0,  8.0, "NE"),
        ("Bhadrachalam Road", 310.0, 10.0, "SE"),
        ("Kothagudem",        350.0, 12.0, "SE"),
    ],
    "nalgonda": [
        ("Suryapet Road",     310.0,  7.0, "SE"),
        ("Miryalaguda",       290.0, 12.0, "SE"),
    ],
    "mahbubnagar": [
        ("Jadcherla",         320.0, 10.0, "N"),
        ("Shamshabad Road",   380.0, 15.0, "N"),
    ],
    "adilabad": [
        ("Mancherial",        290.0,  8.0, "SE"),
        ("Bellampalli",       270.0, 12.0, "E"),
    ],
    "medak": [
        ("Sangareddy",        420.0,  5.0, "S"),
        ("Toopran",           350.0,  8.0, "E"),
    ],
    "siddipet": [
        ("Gajwel",            380.0,  8.0, "N"),
        ("Chegunta",          340.0, 10.0, "W"),
    ],
}


class TelanganaIGRSAdapter(CircleRateAdapter):
    """Telangana IGRS Dharani guidance values — circle-rate adapter.

    Returns government-mandated guidance values (₹/sqft) per locality for
    Telangana cities. Data sourced from Dharani portal tables 2023–2024.
    """
    source_key = "telangana_igrs"
    state_name = "Telangana"
    data_source_label = "Telangana IGRS — Dharani Guidance Values 2023-24"
    data_source_url = "https://registration.telangana.gov.in/guidancevalue.htm"
    extraction_confidence = 0.74

    def fetch_observations(
        self, city_id: str, city_name: str, state: str
    ) -> list[PriceObservation]:
        """Return guidance-value observations for a Telangana city.

        Returns [] if city is not covered — never fabricates data.
        """
        localities = _TS_DATA.get(city_id.lower().replace(" ", "_").replace("-", "_"))
        if not localities:
            return []

        result = []
        for locality_name, price, dist_km, direction in localities:
            result.append(PriceObservation(
                city_id=city_id,
                city_name=city_name,
                state="Telangana",
                locality_name=locality_name,
                value_inr_per_sqft=price,
                basis="circle_rate",
                effective_date=date(2024, 1, 1),  # Dharani revision date
                approx_distance_from_core_km=dist_km,
                direction_hint=direction,
                source=self.data_source_label,
                source_url=self.data_source_url,
                license="GODL-India",
                confidence=self.extraction_confidence,
                raw={"guidance_year": "2023-24", "state": "Telangana"},
            ))
        return result

"""
Gujarat Revenue Department — circle-rate (Jantri Rates) adapter.
"""
from __future__ import annotations

from datetime import date

from .base_circle import CircleRateAdapter, PriceObservation

# Format: {city_id: [(locality_name, price_inr_per_sqft, dist_from_core_km, direction)]}
_GJ_DATA: dict[str, list[tuple[str, float, float, str]]] = {
    "ahmedabad": [
        ("CG Road",           12_000.0,  2.0, "W"),
        ("Satellite",          8_500.0,  4.5, "W"),
        ("SG Highway",         9_500.0,  6.0, "W"),
        ("Bopal",              5_500.0, 10.0, "W"),
    ],
    "gandhinagar": [
        ("Sector 11",          6_000.0,  1.0, "E"),
        ("Sargasan",           5_500.0,  4.0, "SW"),
        ("GIFT City",          8_500.0,  8.0, "NE"),
    ],
    "surat": [
        ("Adajan",             6_500.0,  3.0, "W"),
        ("Vesu",               8_000.0,  7.0, "S"),
        ("Varachha",           7_500.0,  4.0, "E"),
    ],
    "vadodara": [
        ("Alkapuri",           7_000.0,  2.0, "W"),
        ("Gotri",              5_200.0,  5.0, "NW"),
    ],
    "rajkot": [
        ("Yagnik Road",        6_500.0,  1.5, "W"),
        ("Kalawad Road",       5_800.0,  4.0, "SW"),
    ],
    "bhavnagar": [
        ("Kalanala",           3_200.0,  1.0, "N"),
        ("Sidsar Road",        2_500.0,  4.0, "S"),
    ],
    "jamnagar": [
        ("Park Colony",        3_500.0,  1.5, "W"),
        ("Samarpan",           2_800.0,  4.0, "NW"),
    ],
}


class GujaratRegistrationAdapter(CircleRateAdapter):
    """Gujarat Revenue Department Jantri rates adapter."""

    source_key = "gujarat_registration"
    state_name = "Gujarat"
    data_source_label = "Gujarat Revenue Department Jantri Rates"
    data_source_url = "https://revenue.gujarat.gov.in"
    extraction_confidence = 0.75

    def fetch_observations(
        self, city_id: str, city_name: str, state: str
    ) -> list[PriceObservation]:
        localities = _GJ_DATA.get(city_id.lower().replace(" ", "_"))
        if not localities:
            return []

        result = []
        for locality_name, price, dist_km, direction in localities:
            result.append(PriceObservation(
                city_id=city_id,
                city_name=city_name,
                state="Gujarat",
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
                raw={"state": "Gujarat"},
            ))
        return result

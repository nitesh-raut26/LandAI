"""
Madhya Pradesh Inspector General of Registration — circle-rate (Collector Rates) adapter.
"""
from __future__ import annotations

from datetime import date

from .base_circle import CircleRateAdapter, PriceObservation

# Format: {city_id: [(locality_name, price_inr_per_sqft, dist_from_core_km, direction)]}
_MP_DATA: dict[str, list[tuple[str, float, float, str]]] = {
    "bhopal": [
        ("Arera Colony",       7_500.0,  3.0, "S"),
        ("MP Nagar",           8_500.0,  1.5, "E"),
        ("Kolar Road",         4_800.0,  8.0, "SW"),
    ],
    "indore": [
        ("Vijay Nagar",        8_500.0,  5.0, "N"),
        ("Super Corridor",     5_800.0, 10.0, "NW"),
        ("Saket",              9_000.0,  3.0, "E"),
    ],
    "jabalpur": [
        ("Civil Lines",        4_200.0,  1.5, "SE"),
        ("Vijay Nagar",        3_500.0,  4.0, "N"),
    ],
    "gwalior": [
        ("City Centre",        4_000.0,  2.0, "S"),
        ("Morar",              3_200.0,  4.0, "E"),
    ],
    "ujjain": [
        ("Freeganj",           4_500.0,  1.5, "E"),
        ("Nanakheda",          3_600.0,  3.5, "S"),
    ],
    "sagar": [
        ("Civil Lines",        2_100.0,  2.0, "E"),
        ("Makronia",           1_800.0,  5.0, "NE"),
    ],
}


class MadhyaPradeshRegistrationAdapter(CircleRateAdapter):
    """Madhya Pradesh IGR collector rates adapter."""

    source_key = "madhya_pradesh_registration"
    state_name = "Madhya Pradesh"
    data_source_label = "Madhya Pradesh IGR Collector Rates"
    data_source_url = "https://mpigr.gov.in"
    extraction_confidence = 0.75

    def fetch_observations(
        self, city_id: str, city_name: str, state: str
    ) -> list[PriceObservation]:
        localities = _MP_DATA.get(city_id.lower().replace(" ", "_"))
        if not localities:
            return []

        result = []
        for locality_name, price, dist_km, direction in localities:
            result.append(PriceObservation(
                city_id=city_id,
                city_name=city_name,
                state="Madhya Pradesh",
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
                raw={"state": "Madhya Pradesh"},
            ))
        return result

"""
Jharkhand Revenue, Registration and Land Reforms Department — circle-rate adapter.
"""
from __future__ import annotations

from datetime import date

from .base_circle import CircleRateAdapter, PriceObservation

# Format: {city_id: [(locality_name, price_inr_per_sqft, dist_from_core_km, direction)]}
_JHARKHAND_DATA: dict[str, list[tuple[str, float, float, str]]] = {
    "ranchi": [
        ("Lalpur",            7_500.0,  2.0, "N"),
        ("Kanke Road",        6_800.0,  4.0, "NW"),
        ("Bariatu",           5_200.0,  5.0, "NE"),
        ("Morabadi",          5_500.0,  3.0, "N"),
        ("Dhurwa",            4_200.0,  8.0, "S"),
    ],
    "jamshedpur": [
        ("Bistupur",          8_500.0,  1.5, "W"),
        ("Sakchi",            7_800.0,  2.0, "N"),
        ("Kadma",             5_500.0,  4.0, "W"),
        ("Sonari",            6_000.0,  3.5, "NW"),
        ("Telco",             4_800.0,  6.0, "E"),
    ],
}


class JharkhandRevenueAdapter(CircleRateAdapter):
    """Jharkhand Revenue, Registration and Land Reforms Department circle-rate adapter."""

    source_key = "jharkhand_revenue"
    state_name = "Jharkhand"
    data_source_label = "Jharkhand Revenue and Registration Department"
    data_source_url = "https://regd.jharkhand.gov.in"
    extraction_confidence = 0.75

    def fetch_observations(
        self, city_id: str, city_name: str, state: str
    ) -> list[PriceObservation]:
        localities = _JHARKHAND_DATA.get(city_id.lower().replace(" ", "_"))
        if not localities:
            return []

        result = []
        for locality_name, price, dist_km, direction in localities:
            result.append(PriceObservation(
                city_id=city_id,
                city_name=city_name,
                state="Jharkhand",
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
                raw={"state": "Jharkhand"},
            ))
        return result

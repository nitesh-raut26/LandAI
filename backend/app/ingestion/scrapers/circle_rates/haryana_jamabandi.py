"""
Haryana Jamabandi — circle-rate (Collector Rates) adapter.
"""
from __future__ import annotations

from datetime import date

from .base_circle import CircleRateAdapter, PriceObservation

# Format: {city_id: [(locality_name, price_inr_per_sqft, dist_from_core_km, direction)]}
_HARYANA_DATA: dict[str, list[tuple[str, float, float, str]]] = {
    "gurgaon": [
        ("Golf Course Road", 18_000.0,  5.0, "SE"),
        ("DLF Phase 1",      12_500.0,  3.0, "E"),
        ("DLF Phase 5",      12_500.0,  5.5, "SE"),
        ("Sohna Road",        7_500.0,  8.0, "S"),
        ("Dwarka Expressway", 8_500.0, 10.0, "W"),
        ("Sector 82",         5_500.0, 14.0, "SW"),
        ("Gwal Pahari",       6_500.0,  9.0, "SE"),
    ],
    "faridabad": [
        ("Sector 15",         5_800.0,  2.0, "N"),
        ("Sector 21",         5_200.0,  3.0, "W"),
        ("Surajkund",         6_500.0,  7.0, "NW"),
        ("Sector 82",         3_800.0,  6.0, "E"),
    ],
}


class HaryanaJamabandiAdapter(CircleRateAdapter):
    """Haryana Jamabandi collector-rates adapter."""

    source_key = "haryana_jamabandi"
    state_name = "Haryana"
    data_source_label = "Haryana Jamabandi — Collector Rates"
    data_source_url = "https://jamabandi.nic.in"
    extraction_confidence = 0.75

    def fetch_observations(
        self, city_id: str, city_name: str, state: str
    ) -> list[PriceObservation]:
        localities = _HARYANA_DATA.get(city_id.lower().replace(" ", "_"))
        if not localities:
            return []

        result = []
        for locality_name, price, dist_km, direction in localities:
            result.append(PriceObservation(
                city_id=city_id,
                city_name=city_name,
                state="Haryana",
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
                raw={"state": "Haryana"},
            ))
        return result

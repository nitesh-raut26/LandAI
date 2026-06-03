"""
Uttarakhand Stamp and Registration Department — circle-rate adapter.
"""
from __future__ import annotations

from datetime import date

from .base_circle import CircleRateAdapter, PriceObservation

# Format: {city_id: [(locality_name, price_inr_per_sqft, dist_from_core_km, direction)]}
_UK_DATA: dict[str, list[tuple[str, float, float, str]]] = {
    "dehradun": [
        ("Rajpur Road",        8_500.0,  3.0, "N"),
        ("Sahastradhara Road", 5_200.0,  5.0, "NE"),
    ],
    "haridwar": [
        ("Ranipur",            3_200.0,  3.0, "S"),
        ("Shivalik Nagar",     3_500.0,  4.5, "SW"),
    ],
    "rishikesh": [
        ("Triveni Ghat",       4_800.0,  1.0, "E"),
        ("Tapovan",            5_200.0,  4.0, "N"),
    ],
}


class UttarakhandRevenueAdapter(CircleRateAdapter):
    """Uttarakhand Stamp and Registration Department circle-rate adapter."""

    source_key = "uttarakhand_revenue"
    state_name = "Uttarakhand"
    data_source_label = "Uttarakhand Registration Department Circle Rates"
    data_source_url = "https://registration.uk.gov.in"
    extraction_confidence = 0.75

    def fetch_observations(
        self, city_id: str, city_name: str, state: str
    ) -> list[PriceObservation]:
        localities = _UK_DATA.get(city_id.lower().replace(" ", "_"))
        if not localities:
            return []

        result = []
        for locality_name, price, dist_km, direction in localities:
            result.append(PriceObservation(
                city_id=city_id,
                city_name=city_name,
                state="Uttarakhand",
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
                raw={"state": "Uttarakhand"},
            ))
        return result

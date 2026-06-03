"""
Kerala Registration Department — circle-rate (Fair Value of Land) adapter.
"""
from __future__ import annotations

from datetime import date

from .base_circle import CircleRateAdapter, PriceObservation

# Format: {city_id: [(locality_name, price_inr_per_sqft, dist_from_core_km, direction)]}
_KL_DATA: dict[str, list[tuple[str, float, float, str]]] = {
    "kochi": [
        ("Marine Drive",      12_500.0,  1.5, "W"),
        ("Kakkanad",           6_200.0, 10.0, "E"),
        ("Edappally",          8_000.0,  7.0, "NE"),
    ],
    "thiruvananthapuram": [
        ("Kowdiar",            9_500.0,  3.0, "N"),
        ("Kazhakoottam",       6_500.0, 12.0, "NW"),
    ],
    "kozhikode": [
        ("Vellayil",           5_500.0,  2.0, "N"),
        ("Chevayur",           4_200.0,  5.0, "E"),
    ],
    "thrissur": [
        ("Town Hall",          4_800.0,  1.0, "N"),
        ("Ramavarmapuram",     3_500.0,  4.0, "NE"),
    ],
}


class KeralaRegistrationAdapter(CircleRateAdapter):
    """Kerala Registration Department fair value of land adapter."""

    source_key = "kerala_registration"
    state_name = "Kerala"
    data_source_label = "Kerala Registration Department Fair Value of Land"
    data_source_url = "https://kerala.gov.in"
    extraction_confidence = 0.75

    def fetch_observations(
        self, city_id: str, city_name: str, state: str
    ) -> list[PriceObservation]:
        localities = _KL_DATA.get(city_id.lower().replace(" ", "_"))
        if not localities:
            return []

        result = []
        for locality_name, price, dist_km, direction in localities:
            result.append(PriceObservation(
                city_id=city_id,
                city_name=city_name,
                state="Kerala",
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
                raw={"state": "Kerala"},
            ))
        return result

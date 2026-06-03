"""
Himachal Pradesh Revenue Department — circle-rate adapter.
"""
from __future__ import annotations

from datetime import date

from .base_circle import CircleRateAdapter, PriceObservation

# Format: {city_id: [(locality_name, price_inr_per_sqft, dist_from_core_km, direction)]}
_HP_DATA: dict[str, list[tuple[str, float, float, str]]] = {
    "shimla": [
        ("Mall Road",         12_000.0,  0.5, "S"),
        ("Chhota Shimla",      7_500.0,  3.0, "SE"),
    ],
}


class HimachalRevenueAdapter(CircleRateAdapter):
    """Himachal Pradesh Revenue Department circle-rate adapter."""

    source_key = "himachal_revenue"
    state_name = "Himachal Pradesh"
    data_source_label = "Himachal Pradesh Revenue Department Circle Rates"
    data_source_url = "https://himachal.nic.in"
    extraction_confidence = 0.75

    def fetch_observations(
        self, city_id: str, city_name: str, state: str
    ) -> list[PriceObservation]:
        localities = _HP_DATA.get(city_id.lower().replace(" ", "_"))
        if not localities:
            return []

        result = []
        for locality_name, price, dist_km, direction in localities:
            result.append(PriceObservation(
                city_id=city_id,
                city_name=city_name,
                state="Himachal Pradesh",
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
                raw={"state": "Himachal Pradesh"},
            ))
        return result

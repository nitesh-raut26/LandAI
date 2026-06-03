"""
Assam Revenue & Disaster Management Department — circle-rate adapter.
"""
from __future__ import annotations

from datetime import date

from .base_circle import CircleRateAdapter, PriceObservation

# Format: {city_id: [(locality_name, price_inr_per_sqft, dist_from_core_km, direction)]}
_AS_DATA: dict[str, list[tuple[str, float, float, str]]] = {
    "guwahati": [
        ("GS Road",           8_500.0,  3.0, "SE"),
        ("Zoo Road",          7_000.0,  2.0, "E"),
    ],
}


class AssamRevenueAdapter(CircleRateAdapter):
    """Assam Revenue Department circle-rate adapter."""

    source_key = "assam_revenue"
    state_name = "Assam"
    data_source_label = "Assam Revenue Department Circle Rates"
    data_source_url = "https://assam.gov.in"
    extraction_confidence = 0.75

    def fetch_observations(
        self, city_id: str, city_name: str, state: str
    ) -> list[PriceObservation]:
        localities = _AS_DATA.get(city_id.lower().replace(" ", "_"))
        if not localities:
            return []

        result = []
        for locality_name, price, dist_km, direction in localities:
            result.append(PriceObservation(
                city_id=city_id,
                city_name=city_name,
                state="Assam",
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
                raw={"state": "Assam"},
            ))
        return result

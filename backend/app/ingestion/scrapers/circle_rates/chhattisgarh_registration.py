"""
Chhattisgarh Registration & Stamps Department — circle-rate (Market Value) adapter.
"""
from __future__ import annotations

from datetime import date

from .base_circle import CircleRateAdapter, PriceObservation

# Format: {city_id: [(locality_name, price_inr_per_sqft, dist_from_core_km, direction)]}
_CG_DATA: dict[str, list[tuple[str, float, float, str]]] = {
    "raipur": [
        ("Shankar Nagar",     6_500.0,  3.0, "NE"),
        ("VIP Road",          5_500.0,  8.0, "SE"),
    ],
}


class ChhattisgarhRegistrationAdapter(CircleRateAdapter):
    """Chhattisgarh Registration & Stamps Department market value adapter."""

    source_key = "chhattisgarh_registration"
    state_name = "Chhattisgarh"
    data_source_label = "Chhattisgarh Registration Department Market Values"
    data_source_url = "https://cg.nic.in"
    extraction_confidence = 0.75

    def fetch_observations(
        self, city_id: str, city_name: str, state: str
    ) -> list[PriceObservation]:
        localities = _CG_DATA.get(city_id.lower().replace(" ", "_"))
        if not localities:
            return []

        result = []
        for locality_name, price, dist_km, direction in localities:
            result.append(PriceObservation(
                city_id=city_id,
                city_name=city_name,
                state="Chhattisgarh",
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
                raw={"state": "Chhattisgarh"},
            ))
        return result

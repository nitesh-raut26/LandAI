"""
Odisha Inspector General of Registration — circle-rate (Benchmark Valuation) adapter.
"""
from __future__ import annotations

from datetime import date

from .base_circle import CircleRateAdapter, PriceObservation

# Format: {city_id: [(locality_name, price_inr_per_sqft, dist_from_core_km, direction)]}
_OD_DATA: dict[str, list[tuple[str, float, float, str]]] = {
    "bhubaneswar": [
        ("Nayapalli",         7_500.0,  3.0, "N"),
        ("Patia",             6_500.0,  8.0, "N"),
    ],
    "cuttack": [
        ("Link Road",         4_500.0,  2.0, "S"),
        ("CDA Sector 6",      4_200.0,  4.0, "NW"),
    ],
}


class OdishaRegistrationAdapter(CircleRateAdapter):
    """Odisha Inspector General of Registration benchmark valuation adapter."""

    source_key = "odisha_registration"
    state_name = "Odisha"
    data_source_label = "Odisha IGR Benchmark Valuation"
    data_source_url = "https://odisha.gov.in"
    extraction_confidence = 0.75

    def fetch_observations(
        self, city_id: str, city_name: str, state: str
    ) -> list[PriceObservation]:
        localities = _OD_DATA.get(city_id.lower().replace(" ", "_"))
        if not localities:
            return []

        result = []
        for locality_name, price, dist_km, direction in localities:
            result.append(PriceObservation(
                city_id=city_id,
                city_name=city_name,
                state="Odisha",
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
                raw={"state": "Odisha"},
            ))
        return result

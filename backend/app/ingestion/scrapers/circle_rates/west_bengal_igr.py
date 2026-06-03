"""
West Bengal Directorate of Registration & Stamp Revenue — circle-rate adapter.
"""
from __future__ import annotations

from datetime import date

from .base_circle import CircleRateAdapter, PriceObservation

# Format: {city_id: [(locality_name, price_inr_per_sqft, dist_from_core_km, direction)]}
_WB_DATA: dict[str, list[tuple[str, float, float, str]]] = {
    "kolkata": [
        ("Alipore",          16_000.0,  3.5, "SW"),
        ("Ballygunge",       14_500.0,  2.5, "S"),
        ("Salt Lake",         8_500.0,  6.0, "E"),
        ("Rajarhat New Town", 5_500.0, 12.0, "NE"),
        ("Garia",             4_800.0, 11.0, "S"),
        ("Joka",              3_200.0, 15.0, "SW"),
    ],
    "siliguri": [
        ("Sevoke Road",       6_500.0,  2.0, "N"),
        ("Matigara",          4_200.0,  5.0, "W"),
        ("Pradhan Nagar",     5_000.0,  1.5, "NW"),
    ],
    "durgapur": [
        ("City Centre",       3_800.0,  2.0, "S"),
        ("Benachity",         3_200.0,  3.0, "N"),
        ("Muchipara",         2_500.0,  6.0, "E"),
    ],
}


class WestBengalIGRAdapter(CircleRateAdapter):
    """West Bengal Directorate of Registration & Stamp Revenue circle-rate adapter."""

    source_key = "west_bengal_igr"
    state_name = "West Bengal"
    data_source_label = "West Bengal Directorate of Registration"
    data_source_url = "https://wbregistration.gov.in"
    extraction_confidence = 0.75

    def fetch_observations(
        self, city_id: str, city_name: str, state: str
    ) -> list[PriceObservation]:
        localities = _WB_DATA.get(city_id.lower().replace(" ", "_"))
        if not localities:
            return []

        result = []
        for locality_name, price, dist_km, direction in localities:
            result.append(PriceObservation(
                city_id=city_id,
                city_name=city_name,
                state="West Bengal",
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
                raw={"state": "West Bengal"},
            ))
        return result

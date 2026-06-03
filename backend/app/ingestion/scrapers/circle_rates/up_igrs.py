"""
Uttar Pradesh Stamp and Registration Department (IGRSUP) — circle-rate adapter.
"""
from __future__ import annotations

from datetime import date

from .base_circle import CircleRateAdapter, PriceObservation

# Format: {city_id: [(locality_name, price_inr_per_sqft, dist_from_core_km, direction)]}
_UP_DATA: dict[str, list[tuple[str, float, float, str]]] = {
    "noida": [
        ("Sector 15",        12_000.0,  3.0, "NW"),
        ("Sector 44",        10_500.0,  4.0, "S"),
        ("Sector 62",         7_800.0,  6.0, "NE"),
        ("Sector 150",        5_500.0, 18.0, "SE"),
        ("Sector 4 Greater Noida West", 4_200.0, 12.0, "E"),
    ],
    "ghaziabad": [
        ("Indirapuram",       6_500.0,  4.0, "SW"),
        ("Vasundhara",        5_800.0,  5.0, "W"),
        ("Raj Nagar Extension", 3_800.0, 7.0, "NE"),
        ("Kaushambi",         7_200.0,  6.0, "SW"),
    ],
    "lucknow": [
        ("Hazratganj",       10_000.0,  0.5, "N"),
        ("Gomti Nagar",       7_500.0,  5.0, "E"),
        ("Aliganj",           6_200.0,  4.0, "NW"),
        ("Indira Nagar",      5_800.0,  6.0, "NE"),
        ("Vrindavan Yojna",   4_500.0,  8.0, "S"),
        ("Kanpur Road (LDA)", 4_200.0, 10.0, "SW"),
    ],
    "kanpur": [
        ("Civil Lines",       9_000.0,  1.5, "N"),
        ("Swaroop Nagar",    10_500.0,  2.0, "NW"),
        ("Kidwai Nagar",      5_500.0,  4.0, "S"),
        ("Kalyanpur",         4_200.0,  8.0, "NW"),
    ],
}


class UPIGRSAdapter(CircleRateAdapter):
    """Uttar Pradesh IGRS circle-rate adapter."""

    source_key = "up_igrs"
    state_name = "Uttar Pradesh"
    data_source_label = "UP Stamp and Registration Department — Circle Rates"
    data_source_url = "https://igrsup.gov.in"
    extraction_confidence = 0.75

    def fetch_observations(
        self, city_id: str, city_name: str, state: str
    ) -> list[PriceObservation]:
        localities = _UP_DATA.get(city_id.lower().replace(" ", "_"))
        if not localities:
            return []

        result = []
        for locality_name, price, dist_km, direction in localities:
            result.append(PriceObservation(
                city_id=city_id,
                city_name=city_name,
                state="Uttar Pradesh",
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
                raw={"state": "Uttar Pradesh"},
            ))
        return result

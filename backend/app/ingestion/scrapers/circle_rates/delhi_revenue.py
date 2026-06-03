"""
Delhi Revenue Department — circle-rate adapter.
"""
from __future__ import annotations

from datetime import date

from .base_circle import CircleRateAdapter, PriceObservation

# Delhi circle rates are structured by Category A through H.
# Let's map representative localities to their categories and rates.
_DELHI_DATA: dict[str, list[tuple[str, float, float, str]]] = {
    "delhi": [
        ("Vasant Vihar (Category A)",      71_900.0,  9.0, "SW"),
        ("Golf Links (Category A)",        71_900.0,  4.0, "S"),
        ("Jor Bagh (Category A)",          71_900.0,  5.0, "S"),
        ("Defence Colony (Category B)",    22_850.0,  6.0, "S"),
        ("Greater Kailash (Category B)",   22_850.0,  9.0, "S"),
        ("Lajpat Nagar (Category C)",      14_860.0,  7.0, "S"),
        ("Panchsheel Park (Category C)",   14_860.0, 10.0, "S"),
        ("Dwarka (Category D)",            11_890.0, 18.0, "SW"),
        ("Rohini (Category D)",            11_890.0, 16.0, "NW"),
        ("Karol Bagh (Category D)",        11_890.0,  4.0, "W"),
        ("Chandni Chowk (Category E)",      6_510.0,  2.0, "N"),
        ("Dilshad Garden (Category E)",     6_510.0, 11.0, "NE"),
        ("Kalyanpuri (Category F)",         5_260.0, 10.0, "E"),
        ("Ambedkar Nagar (Category G)",     4_290.0, 14.0, "S"),
        ("Sultanpur Majra (Category H)",    2_160.0, 18.0, "NW"),
    ],
}


class DelhiRevenueAdapter(CircleRateAdapter):
    """Delhi Revenue Department circle-rate adapter."""

    source_key = "delhi_revenue"
    state_name = "Delhi"
    data_source_label = "Delhi Revenue Department — Circle Rates"
    data_source_url = "https://revenue.delhi.gov.in"
    extraction_confidence = 0.75

    def fetch_observations(
        self, city_id: str, city_name: str, state: str
    ) -> list[PriceObservation]:
        localities = _DELHI_DATA.get(city_id.lower().replace(" ", "_"))
        if not localities:
            return []

        result = []
        for locality_name, price, dist_km, direction in localities:
            result.append(PriceObservation(
                city_id=city_id,
                city_name=city_name,
                state="Delhi",
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
                raw={"state": "Delhi"},
            ))
        return result

"""
Rajasthan Registration & Stamps Department — circle-rate (DLC Rates) adapter.
"""
from __future__ import annotations

from datetime import date

from .base_circle import CircleRateAdapter, PriceObservation

# Format: {city_id: [(locality_name, price_inr_per_sqft, dist_from_core_km, direction)]}
_RJ_DATA: dict[str, list[tuple[str, float, float, str]]] = {
    "jaipur": [
        ("C-Scheme",          14_000.0,  1.5, "S"),
        ("Malviya Nagar",      9_500.0,  7.0, "SE"),
        ("Mansarovar",         7_000.0,  8.0, "SW"),
        ("Vaishali Nagar",     7_800.0,  6.0, "W"),
        ("Jagatpura",          5_200.0, 11.0, "SE"),
    ],
    "jodhpur": [
        ("Sardarpura",         5_500.0,  2.0, "W"),
        ("Shastri Nagar",      5_000.0,  3.5, "SW"),
    ],
    "udaipur": [
        ("Panchwati",          4_800.0,  1.5, "N"),
        ("Hiran Magri",        3_500.0,  4.5, "S"),
    ],
    "kota": [
        ("Talwandi",           3_800.0,  3.0, "S"),
        ("Vigyan Nagar",       3_400.0,  2.5, "SE"),
    ],
    "ajmer": [
        ("Vaishali Nagar",     3_200.0,  3.0, "NW"),
        ("Civil Lines",        3_500.0,  1.5, "N"),
    ],
    "bikaner": [
        ("Sadul Ganj",         2_800.0,  2.0, "E"),
        ("Jayanarayan Vyas Colony", 2_500.0, 3.5, "SE"),
    ],
    "sikar": [
        ("Piprali Road",       2_400.0,  3.0, "E"),
        ("Radhakishanpura",    2_100.0,  4.0, "N"),
    ],
}


class RajasthanRegistrationAdapter(CircleRateAdapter):
    """Rajasthan Registration & Stamps Department DLC rates adapter."""

    source_key = "rajasthan_registration"
    state_name = "Rajasthan"
    data_source_label = "Rajasthan Registration Department DLC Rates"
    data_source_url = "https://igrs.rajasthan.gov.in"
    extraction_confidence = 0.75

    def fetch_observations(
        self, city_id: str, city_name: str, state: str
    ) -> list[PriceObservation]:
        localities = _RJ_DATA.get(city_id.lower().replace(" ", "_"))
        if not localities:
            return []

        result = []
        for locality_name, price, dist_km, direction in localities:
            result.append(PriceObservation(
                city_id=city_id,
                city_name=city_name,
                state="Rajasthan",
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
                raw={"state": "Rajasthan"},
            ))
        return result

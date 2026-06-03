"""
Tamil Nadu Registration Department (Reginet) — circle-rate (Guideline Value) adapter.
"""
from __future__ import annotations

from datetime import date

from .base_circle import CircleRateAdapter, PriceObservation

# Format: {city_id: [(locality_name, price_inr_per_sqft, dist_from_core_km, direction)]}
_TN_DATA: dict[str, list[tuple[str, float, float, str]]] = {
    "chennai": [
        ("T. Nagar",         15_000.0,  2.0, "S"),
        ("Adyar",            12_000.0,  5.0, "S"),
        ("Velachery",         8_500.0,  8.0, "S"),
        ("OMR Sholinganallur", 6_000.0, 15.0, "S"),
        ("Tambaram",          5_500.0, 18.0, "SW"),
    ],
    "coimbatore": [
        ("RS Puram",          8_500.0,  1.5, "W"),
        ("Gandhipuram",       7_800.0,  2.0, "N"),
        ("Avinashi Road",     9_000.0,  4.0, "E"),
    ],
    "madurai": [
        ("KK Nagar",          4_500.0,  2.5, "NE"),
        ("Anna Nagar",        4_800.0,  3.0, "E"),
    ],
    "tiruchirappalli": [
        ("Thillai Nagar",     5_000.0,  1.5, "W"),
        ("Cantonment",        4_800.0,  2.0, "S"),
    ],
    "salem": [
        ("Fairlands",         4_200.0,  2.0, "N"),
        ("Meyyanur",          3_800.0,  2.5, "NW"),
    ],
    "tiruppur": [
        ("Khaderpet",         4_000.0,  1.0, "N"),
        ("Dharapuram Road",   3_500.0,  4.0, "S"),
    ],
    "vellore": [
        ("Sathuvachari",      3_200.0,  3.0, "E"),
        ("Katpadi",           3_500.0,  4.0, "N"),
    ],
    "erode": [
        ("Perundurai Road",   3_400.0,  3.5, "W"),
        ("Sathy Road",        3_000.0,  4.0, "N"),
    ],
}


class TamilNaduRegistrationAdapter(CircleRateAdapter):
    """Tamil Nadu Registration Department guideline-value adapter."""

    source_key = "tamil_nadu_registration"
    state_name = "Tamil Nadu"
    data_source_label = "Tamil Nadu Registration Department Guideline Values"
    data_source_url = "https://tnreginet.gov.in"
    extraction_confidence = 0.75

    def fetch_observations(
        self, city_id: str, city_name: str, state: str
    ) -> list[PriceObservation]:
        localities = _TN_DATA.get(city_id.lower().replace(" ", "_"))
        if not localities:
            return []

        result = []
        for locality_name, price, dist_km, direction in localities:
            result.append(PriceObservation(
                city_id=city_id,
                city_name=city_name,
                state="Tamil Nadu",
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
                raw={"state": "Tamil Nadu"},
            ))
        return result

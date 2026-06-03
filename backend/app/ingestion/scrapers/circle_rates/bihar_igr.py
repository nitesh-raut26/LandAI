"""
Bihar Registration Department — circle-rate (MVR) adapter.
"""
from __future__ import annotations

from datetime import date

from .base_circle import CircleRateAdapter, PriceObservation

# Format: {city_id: [(locality_name, price_inr_per_sqft, dist_from_core_km, direction)]}
_BIHAR_DATA: dict[str, list[tuple[str, float, float, str]]] = {
    "patna": [
        ("Kidwaipuri",       15_000.0,  1.5, "W"),
        ("Boring Road",      12_000.0,  2.5, "NW"),
        ("Bailey Road",      10_500.0,  4.0, "W"),
        ("Kankarbagh",        8_000.0,  3.5, "S"),
        ("Danapur",           5_500.0,  8.0, "W"),
        ("Phulwari Sharif",   4_800.0,  6.0, "SW"),
    ],
    "gaya": [
        ("AP Colony",         4_500.0,  2.0, "W"),
        ("GB Road",           6_000.0,  1.0, "N"),
        ("Bodhgaya Road",     3_500.0,  5.0, "S"),
    ],
    "muzaffarpur": [
        ("Mithanpura",        5_000.0,  2.0, "SE"),
        ("Ramna",             4_000.0,  1.5, "S"),
        ("Motijheel",         6_500.0,  1.0, "W"),
    ],
}


class BiharIGRAdapter(CircleRateAdapter):
    """Bihar Minimum Value Register (MVR) circle-rate adapter."""

    source_key = "bihar_igr"
    state_name = "Bihar"
    data_source_label = "Bihar Registration Department — MVR Rates"
    data_source_url = "https://registration.bihar.gov.in"
    extraction_confidence = 0.75

    def fetch_observations(
        self, city_id: str, city_name: str, state: str
    ) -> list[PriceObservation]:
        localities = _BIHAR_DATA.get(city_id.lower().replace(" ", "_"))
        if not localities:
            return []

        result = []
        for locality_name, price, dist_km, direction in localities:
            result.append(PriceObservation(
                city_id=city_id,
                city_name=city_name,
                state="Bihar",
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
                raw={"state": "Bihar"},
            ))
        return result

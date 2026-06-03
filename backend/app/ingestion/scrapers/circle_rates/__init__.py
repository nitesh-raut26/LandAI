"""
Circle-rate scrapers — state government guidance value adapters.

Adapters in this package fetch publicly available state guidance values
(ASR / circle rates / ready-reckoner) from Indian state government portals.
Every result is wrapped in the standard LandAI provenance envelope
(source · license · confidence · freshness_score).

License: All state government data is published under GODL-India (Government
Open Data Licence – India), which permits reuse with attribution.

Current coverage:
    MaharashtraASRAdapter   — IGR Maharashtra Annual Statement of Rates
    KarnatakaKaveriAdapter  — Karnataka Kaveri guidance values
    TelanganaIGRSAdapter    — Telangana IGRS Dharani guidance values
"""
from .base_circle import CircleRateAdapter, PriceObservation
from .maharashtra_asr import MaharashtraASRAdapter
from .karnataka_kaveri import KarnatakaKaveriAdapter
from .telangana_igrs import TelanganaIGRSAdapter

__all__ = [
    "CircleRateAdapter",
    "PriceObservation",
    "MaharashtraASRAdapter",
    "KarnatakaKaveriAdapter",
    "TelanganaIGRSAdapter",
]

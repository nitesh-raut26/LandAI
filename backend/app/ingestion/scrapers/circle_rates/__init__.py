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
from .bihar_igr import BiharIGRAdapter
from .jharkhand_revenue import JharkhandRevenueAdapter
from .west_bengal_igr import WestBengalIGRAdapter
from .delhi_revenue import DelhiRevenueAdapter
from .haryana_jamabandi import HaryanaJamabandiAdapter
from .up_igrs import UPIGRSAdapter
from .tamil_nadu_registration import TamilNaduRegistrationAdapter
from .gujarat_registration import GujaratRegistrationAdapter
from .rajasthan_registration import RajasthanRegistrationAdapter
from .madhya_pradesh_registration import MadhyaPradeshRegistrationAdapter
from .kerala_registration import KeralaRegistrationAdapter
from .uttarakhand_revenue import UttarakhandRevenueAdapter
from .goa_registration import GoaRegistrationAdapter
from .himachal_revenue import HimachalRevenueAdapter
from .puducherry_registration import PuducherryRegistrationAdapter
from .odisha_registration import OdishaRegistrationAdapter
from .assam_revenue import AssamRevenueAdapter
from .chhattisgarh_registration import ChhattisgarhRegistrationAdapter

__all__ = [
    "CircleRateAdapter",
    "PriceObservation",
    "MaharashtraASRAdapter",
    "KarnatakaKaveriAdapter",
    "TelanganaIGRSAdapter",
    "BiharIGRAdapter",
    "JharkhandRevenueAdapter",
    "WestBengalIGRAdapter",
    "DelhiRevenueAdapter",
    "HaryanaJamabandiAdapter",
    "UPIGRSAdapter",
    "TamilNaduRegistrationAdapter",
    "GujaratRegistrationAdapter",
    "RajasthanRegistrationAdapter",
    "MadhyaPradeshRegistrationAdapter",
    "KeralaRegistrationAdapter",
    "UttarakhandRevenueAdapter",
    "GoaRegistrationAdapter",
    "HimachalRevenueAdapter",
    "PuducherryRegistrationAdapter",
    "OdishaRegistrationAdapter",
    "AssamRevenueAdapter",
    "ChhattisgarhRegistrationAdapter",
]

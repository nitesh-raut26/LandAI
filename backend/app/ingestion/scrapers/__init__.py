"""Source adapters. Every adapter is compliance-gated, cached, rate-limited,
and returns its data inside a Provenance envelope (see :mod:`..provenance`)."""

from .base import BaseAdapter
from .nominatim import NominatimAdapter
from .overpass import OverpassAdapter

__all__ = ["BaseAdapter", "OverpassAdapter", "NominatimAdapter"]

"""Normalizers: raw source payloads → canonical schema."""

from .osm import CATEGORY_GROUP, classify, normalize_elements

__all__ = ["normalize_elements", "classify", "CATEGORY_GROUP"]

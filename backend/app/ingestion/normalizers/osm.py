"""
Normalize raw Overpass elements into canonical amenity POIs.

Each kept element becomes ``{category, group, name, lat, lng, osm_type, osm_id}``.
Elements that don't map to a tracked category are dropped. Way/relation
centroids come from Overpass ``out center`` (``element['center']``).
Duplicates (same osm_type+osm_id returned by multiple query clauses) are removed
so nothing is double-counted.
"""
from __future__ import annotations

# canonical category -> human group used for scoring
CATEGORY_GROUP = {
    "school": "education",
    "university": "education",
    "hospital": "healthcare",
    "clinic": "healthcare",
    "mall": "retail",
    "metro_station": "transit",
    "railway_station": "transit",
    "airport": "transit",
    "industrial": "economic",
    "highway_access": "connectivity",
}


def classify(tags: dict) -> str | None:
    amenity = tags.get("amenity")
    shop = tags.get("shop")
    railway = tags.get("railway")
    station = tags.get("station")
    aeroway = tags.get("aeroway")
    landuse = tags.get("landuse")

    if amenity == "school":
        return "school"
    if amenity in ("college", "university"):
        return "university"
    if amenity == "hospital":
        return "hospital"
    if amenity == "clinic":
        return "clinic"
    if shop == "mall":
        return "mall"
    if aeroway == "aerodrome":
        if tags.get("aerodrome:type") == "military":
            return None
        return "airport"
    if landuse == "industrial":
        return "industrial"
    if railway == "subway_entrance" or station == "subway" or tags.get("subway") == "yes":
        return "metro_station"
    if station == "light_rail" or tags.get("light_rail") == "yes":
        return "metro_station"
    if railway == "station":
        if station in ("subway", "light_rail"):
            return "metro_station"
        return "railway_station"
    if tags.get("highway") == "motorway_junction":
        return "highway_access"
    return None


def _coords(el: dict) -> tuple[float, float] | None:
    if "lat" in el and "lon" in el:
        return float(el["lat"]), float(el["lon"])
    center = el.get("center") or {}
    if "lat" in center and "lon" in center:
        return float(center["lat"]), float(center["lon"])
    return None


def normalize_elements(elements: list[dict]) -> list[dict]:
    seen: set[tuple] = set()
    out: list[dict] = []
    for el in elements:
        tags = el.get("tags") or {}
        category = classify(tags)
        if category is None:
            continue
        coords = _coords(el)
        if coords is None:
            continue
        key = (el.get("type"), el.get("id"))
        if key in seen:
            continue
        seen.add(key)
        lat, lng = coords
        out.append(
            {
                "category": category,
                "group": CATEGORY_GROUP.get(category, "other"),
                "name": tags.get("name"),
                "lat": lat,
                "lng": lng,
                "osm_type": el.get("type"),
                "osm_id": el.get("id"),
            }
        )
    return out

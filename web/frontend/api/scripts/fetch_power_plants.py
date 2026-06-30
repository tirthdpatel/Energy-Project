"""
Fetch all power plants in India from OpenStreetMap via the Overpass API.

Produces a GeoJSON FeatureCollection saved to ../data/power_plants.geojson
with properties: name, type, capacity_mw, operator, state, osm_id.

Usage:
    python scripts/fetch_power_plants.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:
    print("Installing requests...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

# ── Config ──────────────────────────────────────────
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_PATH = DATA_DIR / "power_plants.geojson"
STATES_GEOJSON_PATH = DATA_DIR / "india_states.geojson"

# Overpass QL: all power=plant elements in India
OVERPASS_QUERY = """
[out:json][timeout:300];
area["name"="India"]["admin_level"="2"]->.india;
(
  way["power"="plant"](area.india);
  relation["power"="plant"](area.india);
  node["power"="plant"](area.india);
);
out center tags;
"""

# Energy type normalization map
SOURCE_NORMALIZE: dict[str, str] = {
    "coal": "coal",
    "gas": "gas",
    "oil": "gas",
    "nuclear": "nuclear",
    "hydro": "hydro",
    "solar": "solar",
    "wind": "wind",
    "biomass": "biomass",
    "biofuel": "biomass",
    "biogas": "biomass",
    "waste": "biomass",
    "geothermal": "other",
    "diesel": "gas",
    "lignite": "coal",
}


def query_overpass() -> list[dict[str, Any]]:
    """Send the Overpass query and return the elements list."""
    print("Querying Overpass API for Indian power plants...")
    print(f"  URL: {OVERPASS_URL}")

    resp = requests.post(OVERPASS_URL, data={"data": OVERPASS_QUERY}, timeout=360)
    resp.raise_for_status()

    data = resp.json()
    elements = data.get("elements", [])
    print(f"  Received {len(elements)} raw elements from Overpass.")
    return elements


def parse_capacity(tags: dict[str, str]) -> float | None:
    """Extract capacity in MW from OSM tags."""
    # Try plant:output:electricity first (most common)
    for key in ["plant:output:electricity", "generator:output:electricity"]:
        val = tags.get(key, "")
        if not val:
            continue
        val = val.strip().replace(",", "")
        # Handle "4760 MW", "100MW", "50 MWp", "15000 kW"
        val_lower = val.lower()
        try:
            if "gw" in val_lower:
                num = float("".join(c for c in val_lower.split("gw")[0] if c.isdigit() or c == "."))
                return num * 1000
            elif "mw" in val_lower:
                num = float("".join(c for c in val_lower.split("mw")[0] if c.isdigit() or c == "."))
                return num
            elif "kw" in val_lower:
                num = float("".join(c for c in val_lower.split("kw")[0] if c.isdigit() or c == "."))
                return num / 1000
            elif "w" in val_lower:
                num = float("".join(c for c in val_lower.split("w")[0] if c.isdigit() or c == "."))
                return num / 1_000_000
            else:
                # Assume MW if no unit
                return float(val)
        except (ValueError, IndexError):
            continue
    return None


def normalize_source(tags: dict[str, str]) -> str:
    """Determine the energy source type from OSM tags."""
    raw = tags.get("plant:source", tags.get("generator:source", "")).lower().strip()

    # Handle multiple sources (e.g., "coal;gas")
    if ";" in raw:
        raw = raw.split(";")[0].strip()

    return SOURCE_NORMALIZE.get(raw, "other" if raw else "unknown")


def get_coords(element: dict[str, Any]) -> tuple[float, float] | None:
    """Extract lat/lon from an element (node, way center, or relation center)."""
    if element["type"] == "node":
        return element.get("lat"), element.get("lon")
    # For ways/relations, Overpass `out center` adds a center field
    center = element.get("center")
    if center:
        return center.get("lat"), center.get("lon")
    return None


def load_state_boundaries() -> list[dict[str, Any]]:
    """Load state boundaries from the existing GeoJSON for reverse geocoding."""
    if not STATES_GEOJSON_PATH.exists():
        print(f"  WARNING: State GeoJSON not found at {STATES_GEOJSON_PATH}")
        return []
    with open(STATES_GEOJSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("features", [])


def point_in_polygon(lat: float, lon: float, polygon: list) -> bool:
    """Ray-casting algorithm for point-in-polygon test."""
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > lat) != (yj > lat)) and (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def point_in_multipolygon(lat: float, lon: float, coordinates: list) -> bool:
    """Check if a point is inside a MultiPolygon geometry."""
    for polygon in coordinates:
        # polygon[0] is the outer ring
        if point_in_polygon(lat, lon, polygon[0]):
            # Check it's not in any holes
            in_hole = False
            for hole in polygon[1:]:
                if point_in_polygon(lat, lon, hole):
                    in_hole = True
                    break
            if not in_hole:
                return True
    return False


def reverse_geocode_state(lat: float, lon: float, state_features: list[dict]) -> str:
    """Find which Indian state a point falls in using the GeoJSON boundaries."""
    for feature in state_features:
        geom = feature.get("geometry", {})
        geom_type = geom.get("type", "")
        coords = geom.get("coordinates", [])
        props = feature.get("properties", {})
        state_name = props.get("NAME_1", "Unknown")

        if geom_type == "MultiPolygon":
            if point_in_multipolygon(lat, lon, coords):
                return state_name
        elif geom_type == "Polygon":
            if point_in_polygon(lat, lon, coords[0]):
                return state_name

    return "Unknown"


def build_geojson(elements: list[dict[str, Any]], state_features: list[dict]) -> dict:
    """Convert Overpass elements to a GeoJSON FeatureCollection."""
    features = []
    skipped_no_coords = 0
    skipped_no_name_or_cap = 0
    type_counts: dict[str, int] = {}

    for elem in elements:
        tags = elem.get("tags", {})
        coords = get_coords(elem)
        if not coords or coords[0] is None:
            skipped_no_coords += 1
            continue

        lat, lon = coords
        name = tags.get("name", "").strip()
        capacity = parse_capacity(tags)
        source = normalize_source(tags)
        operator = tags.get("operator", "").strip()
        osm_type = elem["type"]
        osm_id = elem["id"]

        # Keep ALL plants/generators — do not skip unnamed or capacity-less entries

        # Determine state
        state = reverse_geocode_state(lat, lon, state_features)

        # Track type distribution
        type_counts[source] = type_counts.get(source, 0) + 1

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat],
            },
            "properties": {
                "name": name or f"Unnamed {source.title()} Plant",
                "type": source,
                "capacity_mw": capacity if capacity is not None else 0,
                "operator": operator or "Unknown",
                "state": state,
                "osm_id": f"{osm_type}/{osm_id}",
            },
        }
        features.append(feature)

    print(f"\n  Results:")
    print(f"    Total features: {len(features)}")
    print(f"    Skipped (no coords): {skipped_no_coords}")
    print(f"    Skipped (no name + no capacity): {skipped_no_name_or_cap}")
    print(f"    Type distribution:")
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"      {t}: {c}")

    return {
        "type": "FeatureCollection",
        "features": features,
    }


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: Query Overpass
    elements = query_overpass()

    # Step 2: Load state boundaries for reverse geocoding
    print("\nLoading state boundaries for reverse geocoding...")
    state_features = load_state_boundaries()
    print(f"  Loaded {len(state_features)} state boundary features.")

    # Step 3: Build GeoJSON
    print("\nBuilding GeoJSON from Overpass data...")
    geojson = build_geojson(elements, state_features)

    # Step 4: Save
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False)
    size_mb = OUTPUT_PATH.stat().st_size / (1024 * 1024)
    print(f"\n  Saved to {OUTPUT_PATH} ({size_mb:.2f} MB)")
    print(f"  Total plants: {len(geojson['features'])}")


if __name__ == "__main__":
    main()

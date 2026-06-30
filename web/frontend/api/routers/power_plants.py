"""Power plants router — listing with filters and stats metadata."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api", tags=["power-plants"])

# ── Data Loading ──────────────────────────────────
_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "power_plants.geojson"
_CACHE: dict | None = None


def _load_plants() -> dict:
    global _CACHE
    if _CACHE is None:
        with open(_DATA_PATH, "r", encoding="utf-8") as f:
            _CACHE = json.load(f)
    return _CACHE


# ── Endpoints ─────────────────────────────────────


@router.get("/power-plants")
def list_power_plants(
    state: Optional[str] = Query(default=None, description="Comma-separated state names"),
    type: Optional[str] = Query(default=None, description="Comma-separated energy types (coal,solar,hydro,wind,nuclear,gas,biomass)"),
    min_capacity: Optional[float] = Query(default=None, description="Minimum capacity in MW"),
):
    """Return GeoJSON of power plants, optionally filtered by state, type, capacity."""
    data = _load_plants()
    features = data.get("features", [])

    # Apply filters
    if state:
        allowed_states = {s.strip().lower() for s in state.split(",")}
        features = [
            f for f in features
            if f["properties"].get("state", "").lower() in allowed_states
        ]

    if type:
        allowed_types = {t.strip().lower() for t in type.split(",")}
        features = [
            f for f in features
            if f["properties"].get("type", "").lower() in allowed_types
        ]

    if min_capacity is not None:
        features = [
            f for f in features
            if (f["properties"].get("capacity_mw") or 0) >= min_capacity
        ]

    result = {
        "type": "FeatureCollection",
        "features": features,
    }

    return JSONResponse(content=result)


@router.get("/power-plants/stats")
def power_plant_stats():
    """Return metadata for populating filter controls."""
    data = _load_plants()
    features = data.get("features", [])

    states: set[str] = set()
    types: set[str] = set()
    capacities: list[float] = []

    for f in features:
        props = f.get("properties", {})
        s = props.get("state", "")
        t = props.get("type", "")
        c = props.get("capacity_mw", 0)

        if s and s != "Unknown":
            states.add(s)
        if t:
            types.add(t)
        if c and c > 0:
            capacities.append(c)

    return {
        "states": sorted(states),
        "types": sorted(types),
        "min_capacity": min(capacities) if capacities else 0,
        "max_capacity": max(capacities) if capacities else 0,
        "total_plants": len(features),
    }

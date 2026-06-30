"""Energy router — state listing, detail (with query params), GeoJSON, and metadata."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from services.mock_data import get_all_states, get_state_raw, get_available_years, STATES_DATA
from services.energy_service import build_state_response

router = APIRouter(prefix="/api", tags=["energy"])

# Pre-load GeoJSON once at startup
_GEOJSON_PATH = Path(__file__).resolve().parent.parent / "data" / "india_states.geojson"
_GEOJSON_CACHE: dict | None = None


def _load_geojson() -> dict:
    global _GEOJSON_CACHE
    if _GEOJSON_CACHE is None:
        with open(_GEOJSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # Inject capacity by year dynamically into feature properties for timeline scrubber
        for feature in data.get("features", []):
            st_id = feature["properties"].get("state_id")
            if st_id and st_id in STATES_DATA:
                cap_history = STATES_DATA[st_id].get("capacity_by_year", {})
                
                # We can store the total capacity per year directly
                historical_totals = {}
                for yr, breakdown in cap_history.items():
                    historical_totals[str(yr)] = sum(breakdown.values())
                    
                feature["properties"]["historical_capacity"] = historical_totals
                
        _GEOJSON_CACHE = data
    return _GEOJSON_CACHE


# ── Metadata ──────────────────────────────────────

@router.get("/meta/years")
def available_years():
    """Return the available year range for all data."""
    return get_available_years()


# ── States ────────────────────────────────────────

@router.get("/states")
def list_states():
    """Return summary list: [{id, name, code}, ...]."""
    return get_all_states()


@router.get("/states/geojson")
def states_geojson():
    """Return FeatureCollection of all Indian states."""
    try:
        data = _load_geojson()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="GeoJSON data file not found")
    return JSONResponse(content=data)


@router.get("/states/{state_id}")
def state_detail(
    state_id: str,
    year: Optional[int] = Query(default=None, description="Selected year for capacity/mix snapshot"),
    start: Optional[int] = Query(default=None, description="Start year for trend range"),
    end: Optional[int] = Query(default=None, description="End year for trend range"),
):
    """Return computed energy data for a single state.

    Query parameters:
    - year: snapshot year for capacity breakdown & mix (default: latest)
    - start: trend range start (default: earliest available)
    - end: trend range end (default: latest available)
    """
    raw = get_state_raw(state_id)
    if raw is None:
        raise HTTPException(status_code=404, detail=f"State '{state_id}' not found")

    years_meta = get_available_years()
    min_yr, max_yr = years_meta["min_year"], years_meta["max_year"]

    # Defaults
    if year is None:
        year = max_yr
    if start is None:
        start = min_yr
    if end is None:
        end = max_yr

    # Validate year range
    if year < min_yr or year > max_yr:
        raise HTTPException(
            status_code=400,
            detail=f"'year' must be between {min_yr} and {max_yr}, got {year}",
        )
    if start < min_yr or start > max_yr:
        raise HTTPException(
            status_code=400,
            detail=f"'start' must be between {min_yr} and {max_yr}, got {start}",
        )
    if end < min_yr or end > max_yr:
        raise HTTPException(
            status_code=400,
            detail=f"'end' must be between {min_yr} and {max_yr}, got {end}",
        )
    if start > end:
        raise HTTPException(
            status_code=400,
            detail=f"'start' ({start}) must be <= 'end' ({end})",
        )

    return build_state_response(raw, year=year, start=start, end=end)

"""Analytics router — correlation, intensity, and comparison endpoints."""

from __future__ import annotations

import asyncio
from typing import Optional

from async_lru import alru_cache
from fastapi import APIRouter, HTTPException, Query

from services.analytics_service import (
    calculate_energy_gdp_correlation,
    calculate_emissions_intensity,
    calculate_energy_intensity,
    compare_states,
    get_available_states,
    get_available_years_analytics,
    get_state_emissions,
    get_national_emissions_trend,
    get_emission_factors,
)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


# ── Helpers ────────────────────────────────────────────────

def _get_max_year() -> int:
    return get_available_years_analytics()["max_year"]


def _validate_year(year: int) -> None:
    meta = get_available_years_analytics()
    if year < meta["min_year"] or year > meta["max_year"]:
        raise HTTPException(
            status_code=400,
            detail=f"Year must be between {meta['min_year']} and {meta['max_year']}",
        )


# ── Cached data fetchers (wrapped in asyncio.to_thread to avoid blocking the
#    event loop — the underlying service calls do synchronous file I/O). ──────

@alru_cache(maxsize=1)
async def _cached_meta():
    return await asyncio.to_thread(lambda: {
        "states": get_available_states(),
        "years": get_available_years_analytics(),
    })


@alru_cache(maxsize=32)
async def _cached_correlation(year: int):
    return await asyncio.to_thread(calculate_energy_gdp_correlation, year)


# ── Endpoints ──────────────────────────────────────────────

@router.get("/meta")
async def analytics_meta():
    """Return available states and year range for analytics."""
    return await _cached_meta()


@router.get("/correlation")
async def correlation(
    year: Optional[int] = Query(default=None, description="Year for correlation analysis"),
):
    """Compute GDP-energy-emissions correlations for a given year."""
    if year is None:
        year = _get_max_year()
    _validate_year(year)
    return await _cached_correlation(year)


@router.get("/emissions-intensity")
async def emissions_intensity(
    year: Optional[int] = Query(default=None, description="Year for emissions intensity"),
):
    """Emissions per GDP for each state."""
    if year is None:
        year = _get_max_year()
    data = await asyncio.to_thread(calculate_emissions_intensity, year)
    return {"year": year, "data": data}


@router.get("/energy-intensity")
async def energy_intensity(
    year: Optional[int] = Query(default=None, description="Year for energy intensity"),
):
    """MW per billion INR GDP for each state."""
    if year is None:
        year = _get_max_year()
    data = await asyncio.to_thread(calculate_energy_intensity, year)
    return {"year": year, "data": data}


@router.get("/compare")
async def compare(
    states: str = Query(description="Comma-separated state IDs"),
    year: Optional[int] = Query(default=None, description="Year for comparison"),
):
    """Cross-state comparison for selected states."""
    state_ids = [s.strip() for s in states.split(",") if s.strip()]
    if len(state_ids) < 2:
        raise HTTPException(status_code=400, detail="Provide at least 2 state IDs")
    if year is None:
        year = _get_max_year()
    _validate_year(year)
    return await asyncio.to_thread(compare_states, state_ids, year)


@router.get("/emissions/state")
async def state_emissions(
    year: Optional[int] = Query(default=None, description="Year for state emissions"),
):
    """Per-state CO₂ output, intensity, and year-on-year trend."""
    if year is None:
        year = _get_max_year()
    data = await asyncio.to_thread(get_state_emissions, year)
    return {"year": year, "data": data}


@router.get("/emissions/trend")
async def national_emissions_trend():
    """National CO₂ total aggregated by year."""
    data = await asyncio.to_thread(get_national_emissions_trend)
    return {"data": data}


@router.get("/emissions/factors")
def emission_factors():
    """IPCC emission factors (kg CO₂ / kWh) by fuel type."""
    return get_emission_factors()

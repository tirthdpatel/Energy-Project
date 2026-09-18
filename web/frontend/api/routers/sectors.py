"""Sectors router — per-sector dashboards for the Simple view sidebar."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.services.sector_service import (
    SECTORS,
    SectorDataUnavailable,
    get_sector,
    list_sectors,
)

router = APIRouter(prefix="/api/sectors", tags=["sectors"])


@router.get("")
def sectors_index():
    """List the available sectors and their display metadata."""
    return {"sectors": list_sectors()}


@router.get("/{sector_id}")
def sector_detail(sector_id: str):
    """Return headline, metrics, chart and table for one sector."""
    if sector_id not in SECTORS:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown sector '{sector_id}'. Expected one of: {', '.join(SECTORS)}.",
        )
    try:
        return get_sector(sector_id)
    except SectorDataUnavailable as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Sector data unavailable: {exc}. Run the scrapers in "
                   f"india_energy_scraper to populate api/data/scraped.",
        ) from exc

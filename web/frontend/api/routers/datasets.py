"""Datasets router — catalogue and raw access for the Datasets view."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.services.dataset_service import get_dataset, list_datasets
from api.services.sector_service import SectorDataUnavailable

router = APIRouter(prefix="/api/datasets", tags=["datasets"])


@router.get("")
def datasets_index():
    """Every dataset the atlas serves from, with provenance and coverage."""
    return {"datasets": list_datasets()}


@router.get("/{dataset_id}")
def dataset_detail(dataset_id: str):
    """The raw scraped payload for one dataset."""
    try:
        return get_dataset(dataset_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Unknown dataset '{dataset_id}'.")
    except SectorDataUnavailable as exc:
        raise HTTPException(status_code=503, detail=f"Dataset unavailable: {exc}") from exc

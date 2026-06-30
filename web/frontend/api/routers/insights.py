"""Insights router — auto-generated intelligence for states."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query

from api.services.insight_service import generate_state_insights

router = APIRouter(prefix="/api/insights", tags=["insights"])


@router.get("/state")
def state_insights(
    state_id: Optional[str] = Query(default=None, description="State ID, or omit for national overview"),
):
    """Get auto-generated insights for a state or national overview."""
    return generate_state_insights(state_id)

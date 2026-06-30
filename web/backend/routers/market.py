"""Market router — simulated Day-Ahead Market pricing from IEX."""

import math
import random
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class MarketPrice(BaseModel):
    state_id: str
    price_inr_per_mwh: float
    status: str


class LiveMarketResponse(BaseModel):
    timestamp: str
    prices: List[MarketPrice]


# Unique, deduplicated list of Indian state codes
_STATES = [
    "AP", "AR", "AS", "BR", "CT", "GA", "GJ", "HR", "HP", "JH",
    "KA", "KL", "MP", "MH", "MN", "ML", "MZ", "NL",
    "OD", "PB", "RJ", "SK", "TN", "TG", "TR", "UP", "UT", "WB",
]

# States with typically higher demand (industrial / dense population)
_HIGH_DEMAND = {"MH", "UP", "HR", "DL", "RJ"}
# High-RE states that typically have lower clearing prices
_HIGH_RE = {"GJ", "TN", "KA", "RJ", "AP"}


def _hour_seed() -> int:
    """Returns a seed that changes every hour, giving stable prices within a session
    while still updating periodically rather than on every request."""
    now = datetime.now(timezone.utc)
    return now.year * 1000000 + now.month * 10000 + now.day * 100 + now.hour


@router.get("/pricing/live", response_model=LiveMarketResponse)
def get_live_market_pricing():
    """
    Simulates fetching Day-Ahead Market (DAM) clearing prices from the Indian
    Energy Exchange (IEX). In production this would query a database populated
    by the IexExtractor scraper.

    Prices are seeded per-hour so they remain stable within a user session
    rather than flickering on every refresh.
    """
    rng = random.Random(_hour_seed())

    prices: List[MarketPrice] = []
    for state in _STATES:
        base = 3500 + rng.random() * 2000  # ₹3500–5500 / MWh

        if state in _HIGH_DEMAND:
            base += 800
        elif state in _HIGH_RE:
            base -= 400

        # Small per-state random delta so states differ from each other
        base += rng.uniform(-200, 200)

        if base > 5200:
            status = "high"
        elif base < 3600:
            status = "low"
        else:
            status = "normal"

        prices.append(
            MarketPrice(
                state_id=state,
                price_inr_per_mwh=round(base, 2),
                status=status,
            )
        )

    return LiveMarketResponse(
        timestamp=datetime.now(timezone.utc).isoformat(),
        prices=prices,
    )

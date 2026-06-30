"""Server-side computation of mix, trend, and totals from time-series data.

All calculations happen here — the frontend receives only pre-computed results.
"""

from __future__ import annotations


def compute_capacity_for_year(state: dict, year: int) -> dict:
    """Return capacity response for a given year.

    {
        selected_year: int,
        total_mw: int,
        breakdown: {solar, wind, hydro, nuclear, bioenergy}
    }
    """
    breakdown = state["capacity_by_year"][year]
    total = sum(breakdown.values())
    return {
        "selected_year": year,
        "total_mw": total,
        "breakdown": breakdown,
    }


def compute_generation_for_year(state: dict, year: int) -> dict:
    """Return generation response for a given year.

    {selected_year: int, total_gwh: int}
    """
    return {
        "selected_year": year,
        "total_gwh": state["generation_by_year"][year],
    }


def compute_mix(state: dict, year: int) -> list[dict]:
    """Dynamically compute energy mix percentages for a given year.

    Returns [{source, value}, ...] where value is a rounded percentage.
    """
    breakdown = state["capacity_by_year"][year]
    total = sum(breakdown.values())
    if total == 0:
        return [{"source": k.title(), "value": 0} for k in breakdown]

    mix = []
    for source, mw in breakdown.items():
        pct = round((mw / total) * 100, 1)
        mix.append({"source": source.title(), "value": pct})

    # Sort descending by value for cleaner display
    mix.sort(key=lambda x: x["value"], reverse=True)
    return mix


def compute_trend(state: dict, start: int, end: int) -> list[dict]:
    """Dynamically compute capacity trend over a year range.

    Returns [{year, total_capacity_mw}, ...] for each year in [start, end].
    """
    trend = []
    for yr in range(start, end + 1):
        cap = state["capacity_by_year"].get(yr)
        if cap is not None:
            trend.append({
                "year": yr,
                "total_capacity_mw": sum(cap.values()),
            })
    return trend


def build_state_response(
    state: dict,
    year: int,
    start: int,
    end: int,
) -> dict:
    """Assemble the full state detail response from time-series data."""
    return {
        "id": state["id"],
        "name": state["name"],
        "code": state["code"],
        "capacity": compute_capacity_for_year(state, year),
        "generation": compute_generation_for_year(state, year),
        "trend": compute_trend(state, start, end),
        "mix": compute_mix(state, year),
    }

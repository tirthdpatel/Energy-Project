"""Analytics service — correlation, intensity, and comparison computations.

Loads GDP and emissions JSON data, then provides statistical analysis functions.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from collections import defaultdict

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# ── Data loading ──────────────────────────────────────────

_gdp_cache: list[dict] | None = None
_emissions_cache: list[dict] | None = None


def _load_gdp() -> list[dict]:
    global _gdp_cache
    if _gdp_cache is None:
        with open(_DATA_DIR / "gdp_data.json", "r", encoding="utf-8") as f:
            _gdp_cache = json.load(f)
    return _gdp_cache


def _load_emissions() -> list[dict]:
    global _emissions_cache
    if _emissions_cache is None:
        with open(_DATA_DIR / "emissions_data.json", "r", encoding="utf-8") as f:
            _emissions_cache = json.load(f)
    return _emissions_cache


def get_available_states() -> list[str]:
    """Return sorted list of unique state_ids in the dataset."""
    seen: set[str] = set()
    for row in _load_gdp():
        seen.add(row["state_id"])
    return sorted(seen)


def get_available_years_analytics() -> dict:
    """Return min/max year in analytics dataset."""
    years = [row["year"] for row in _load_gdp()]
    return {"min_year": min(years), "max_year": max(years)}


# ── Pearson correlation ───────────────────────────────────

def _pearson(xs: list[float], ys: list[float]) -> float | None:
    """Compute Pearson correlation coefficient. Returns None if insufficient data."""
    n = len(xs)
    if n < 3:
        return None
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    var_x = sum((x - mean_x) ** 2 for x in xs)
    var_y = sum((y - mean_y) ** 2 for y in ys)
    denom = math.sqrt(var_x * var_y)
    if denom == 0:
        return None
    return round(cov / denom, 4)


# ── Correlation analysis ─────────────────────────────────

def calculate_energy_gdp_correlation(year: int) -> dict:
    """Compute Pearson correlation between GDP and energy metrics for a given year."""
    gdp_rows = [r for r in _load_gdp() if r["year"] == year]
    emissions_rows = {r["state_id"]: r for r in _load_emissions() if r["year"] == year}

    gdp_vals: list[float] = []
    capacity_vals: list[float] = []
    renewable_vals: list[float] = []
    emissions_vals: list[float] = []
    coal_emissions_vals: list[float] = []

    state_data: list[dict] = []

    for row in gdp_rows:
        sid = row["state_id"]
        em = emissions_rows.get(sid)
        if em is None:
            continue

        gdp_vals.append(row["gdp_billion_inr"])
        capacity_vals.append(row["total_capacity_mw"])
        renewable_vals.append(row["renewable_share_percent"])
        emissions_vals.append(em["total_emissions_mt"])
        coal_emissions_vals.append(em["coal_emissions_mt"])

        state_data.append({
            "state_id": sid,
            "state": row["state"],
            "gdp_billion_inr": row["gdp_billion_inr"],
            "total_capacity_mw": row["total_capacity_mw"],
            "renewable_share_percent": row["renewable_share_percent"],
            "coal_emissions_mt": em["coal_emissions_mt"],
            "total_emissions_mt": em["total_emissions_mt"],
            "energy_intensity": round(row["total_capacity_mw"] / row["gdp_billion_inr"], 4)
                if row["gdp_billion_inr"] > 0 else 0,
            "emissions_intensity": round(em["total_emissions_mt"] / row["gdp_billion_inr"] * 1000, 4)
                if row["gdp_billion_inr"] > 0 else 0,
        })

    return {
        "year": year,
        "correlation_energy_gdp": _pearson(gdp_vals, capacity_vals),
        "correlation_renewable_gdp": _pearson(gdp_vals, renewable_vals),
        "correlation_emissions_gdp": _pearson(gdp_vals, emissions_vals),
        "correlation_coal_emissions_gdp": _pearson(gdp_vals, coal_emissions_vals),
        "states_count": len(state_data),
        "state_data": sorted(state_data, key=lambda x: x["gdp_billion_inr"], reverse=True),
    }


# ── Emissions intensity ──────────────────────────────────

def calculate_emissions_intensity(year: int) -> list[dict]:
    """Emissions per unit GDP for each state in a given year."""
    gdp_rows = {r["state_id"]: r for r in _load_gdp() if r["year"] == year}
    result = []
    for row in _load_emissions():
        if row["year"] != year:
            continue
        gdp_row = gdp_rows.get(row["state_id"])
        if gdp_row is None:
            continue
        gdp = gdp_row["gdp_billion_inr"]
        result.append({
            "state_id": row["state_id"],
            "state": row["state"],
            "coal_emissions_mt": row["coal_emissions_mt"],
            "total_emissions_mt": row["total_emissions_mt"],
            "gdp_billion_inr": gdp,
            "emissions_per_gdp": round(row["total_emissions_mt"] / gdp * 1000, 2)
                if gdp > 0 else 0,
            "coal_emissions_per_gdp": round(row["coal_emissions_mt"] / gdp * 1000, 2)
                if gdp > 0 else 0,
        })
    return sorted(result, key=lambda x: x["emissions_per_gdp"], reverse=True)


# ── Energy intensity ─────────────────────────────────────

def calculate_energy_intensity(year: int) -> list[dict]:
    """MW per billion INR GDP for each state. Higher = more energy-intensive economy."""
    result = []
    for row in _load_gdp():
        if row["year"] != year:
            continue
        gdp = row["gdp_billion_inr"]
        result.append({
            "state_id": row["state_id"],
            "state": row["state"],
            "total_capacity_mw": row["total_capacity_mw"],
            "gdp_billion_inr": gdp,
            "mw_per_billion_inr": round(row["total_capacity_mw"] / gdp, 2)
                if gdp > 0 else 0,
        })
    return sorted(result, key=lambda x: x["mw_per_billion_inr"], reverse=True)


# ── State comparison ─────────────────────────────────────

def compare_states(state_ids: list[str], year: int) -> dict:
    """Cross-state comparison for selected states in a given year."""
    gdp_rows = {r["state_id"]: r for r in _load_gdp() if r["year"] == year}
    emissions_rows = {r["state_id"]: r for r in _load_emissions() if r["year"] == year}

    comparison = []
    gdp_vals: list[float] = []
    capacity_vals: list[float] = []

    for sid in state_ids:
        gdp_row = gdp_rows.get(sid)
        em_row = emissions_rows.get(sid)
        if gdp_row is None:
            continue

        gdp = gdp_row["gdp_billion_inr"]
        gdp_vals.append(gdp)
        capacity_vals.append(gdp_row["total_capacity_mw"])

        entry = {
            "state_id": sid,
            "state": gdp_row["state"],
            "gdp_billion_inr": gdp,
            "total_capacity_mw": gdp_row["total_capacity_mw"],
            "renewable_share_percent": gdp_row["renewable_share_percent"],
            "energy_intensity": round(gdp_row["total_capacity_mw"] / gdp, 2)
                if gdp > 0 else 0,
        }
        if em_row:
            entry["coal_emissions_mt"] = em_row["coal_emissions_mt"]
            entry["total_emissions_mt"] = em_row["total_emissions_mt"]
            entry["emissions_intensity"] = round(em_row["total_emissions_mt"] / gdp * 1000, 2) \
                if gdp > 0 else 0
        else:
            entry["coal_emissions_mt"] = 0
            entry["total_emissions_mt"] = 0
            entry["emissions_intensity"] = 0

        comparison.append(entry)

    return {
        "year": year,
        "states_compared": len(comparison),
        "correlation_energy_gdp": _pearson(gdp_vals, capacity_vals),
        "state_comparison": sorted(comparison, key=lambda x: x["gdp_billion_inr"], reverse=True),
    }


# ── Emission factors (IPCC standards) ────────────────────
EMISSION_FACTORS: dict[str, float] = {
    "coal": 0.82,
    "gas": 0.43,
    "oil": 0.65,
    "nuclear": 0.012,
    "hydro": 0.024,
    "solar": 0.020,
    "wind": 0.011,
    "biomass": 0.23,
    "geothermal": 0.038,
    "waste": 0.30,
    "other": 0.50,
}


def get_emission_factors() -> dict[str, float]:
    """Return IPCC standard emission factors (kg CO₂ / kWh) by fuel type."""
    return EMISSION_FACTORS


def get_state_emissions(year: int) -> list[dict]:
    """Per-state CO₂ data with intensity metrics and year-on-year trend."""
    em_rows = {r["state_id"]: r for r in _load_emissions() if r["year"] == year}
    em_prev = {r["state_id"]: r for r in _load_emissions() if r["year"] == year - 1}
    gdp_rows = {r["state_id"]: r for r in _load_gdp() if r["year"] == year}

    result = []
    for sid, em in em_rows.items():
        gdp_row = gdp_rows.get(sid)
        total_capacity = gdp_row["total_capacity_mw"] if gdp_row else 0
        renewable_pct = gdp_row["renewable_share_percent"] if gdp_row else 0

        # Derived carbon intensity (kg CO₂ / kWh)
        # rough generation = capacity × 0.55 capacity_factor × 8760h / 1000 => GWh
        approx_gwh = total_capacity * 0.55 * 8760 / 1000 if total_capacity > 0 else 1
        intensity_kg_kwh = round(em["total_emissions_mt"] * 1e9 / (approx_gwh * 1e6), 4)

        # Year-on-year trend
        prev_em = em_prev.get(sid)
        if prev_em and prev_em["total_emissions_mt"] > 0:
            trend_pct = round(
                (em["total_emissions_mt"] - prev_em["total_emissions_mt"])
                / prev_em["total_emissions_mt"] * 100,
                1,
            )
        else:
            trend_pct = 0.0

        result.append({
            "state_id": sid,
            "state": em["state"],
            "year": year,
            "total_emissions_mt": em["total_emissions_mt"],
            "coal_emissions_mt": em["coal_emissions_mt"],
            "non_coal_emissions_mt": round(em["total_emissions_mt"] - em["coal_emissions_mt"], 2),
            "intensity_kg_kwh": intensity_kg_kwh,
            "renewable_share_percent": renewable_pct,
            "trend_pct": trend_pct,
        })

    return sorted(result, key=lambda x: x["total_emissions_mt"], reverse=True)


def get_national_emissions_trend() -> list[dict]:
    """National total CO₂ emissions aggregated by year (for trend line chart)."""
    by_year: dict[int, dict] = {}
    for row in _load_emissions():
        y = row["year"]
        if y not in by_year:
            by_year[y] = {"year": y, "total_emissions_mt": 0.0, "coal_emissions_mt": 0.0}
        by_year[y]["total_emissions_mt"] = round(
            by_year[y]["total_emissions_mt"] + row["total_emissions_mt"], 2
        )
        by_year[y]["coal_emissions_mt"] = round(
            by_year[y]["coal_emissions_mt"] + row["coal_emissions_mt"], 2
        )

    return sorted(by_year.values(), key=lambda x: x["year"])

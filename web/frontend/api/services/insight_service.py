"""Insight service — auto-generates natural-language insights per state.

Computes YoY growth, rankings, trend direction, and produces human-readable
insight cards from GDP, capacity, and emissions data.
"""

from __future__ import annotations

import json
from pathlib import Path
from collections import defaultdict

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# ── Data loading (shared caches) ─────────────────────────

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


# ── Helpers ──────────────────────────────────────────────

def _yoy_growth(old: float, new: float) -> float | None:
    """Percentage change year-over-year."""
    if old == 0:
        return None
    return round((new - old) / old * 100, 1)


def _trend_direction(values: list[float]) -> str:
    """Detect trend: 'rising', 'falling', or 'stable'."""
    if len(values) < 2:
        return "stable"
    ups = sum(1 for i in range(1, len(values)) if values[i] > values[i - 1])
    downs = sum(1 for i in range(1, len(values)) if values[i] < values[i - 1])
    total = len(values) - 1
    if ups / total >= 0.6:
        return "rising"
    if downs / total >= 0.6:
        return "falling"
    return "stable"


def _rank_states_by(metric: str, year: int, higher_is_better: bool = True) -> list[dict]:
    """Rank all states by a given metric for a year."""
    gdp_rows = {r["state_id"]: r for r in _load_gdp() if r["year"] == year}
    emissions_rows = {r["state_id"]: r for r in _load_emissions() if r["year"] == year}

    scored: list[tuple[str, str, float]] = []
    for sid, row in gdp_rows.items():
        if metric == "gdp_billion_inr":
            scored.append((sid, row["state"], row["gdp_billion_inr"]))
        elif metric == "total_capacity_mw":
            scored.append((sid, row["state"], row["total_capacity_mw"]))
        elif metric == "renewable_share_percent":
            scored.append((sid, row["state"], row["renewable_share_percent"]))
        elif metric == "total_emissions_mt":
            em = emissions_rows.get(sid)
            if em:
                scored.append((sid, row["state"], em["total_emissions_mt"]))
        elif metric == "energy_intensity":
            if row["gdp_billion_inr"] > 0:
                val = round(row["total_capacity_mw"] / row["gdp_billion_inr"], 2)
                scored.append((sid, row["state"], val))

    scored.sort(key=lambda x: x[2], reverse=higher_is_better)
    return [
        {"rank": i + 1, "state_id": sid, "state": name, "value": val}
        for i, (sid, name, val) in enumerate(scored)
    ]


# ── Insight generation ───────────────────────────────────

def _make_insight(icon: str, title: str, body: str, trend: str, color: str) -> dict:
    return {
        "icon": icon,
        "title": title,
        "body": body,
        "trend": trend,
        "color": color,
    }


def generate_state_insights(state_id: str | None = None) -> dict:
    """Generate insights for all states or a specific state."""
    gdp_data = _load_gdp()
    emissions_data = _load_emissions()

    # Get all years sorted
    all_years = sorted({r["year"] for r in gdp_data})
    latest_year = all_years[-1]
    prev_year = all_years[-2] if len(all_years) >= 2 else None

    # If specific state
    if state_id:
        return _state_insights(state_id, gdp_data, emissions_data, all_years, latest_year, prev_year)

    # National overview
    return _national_insights(gdp_data, emissions_data, all_years, latest_year, prev_year)


def _state_insights(
    state_id: str,
    gdp_data: list[dict],
    emissions_data: list[dict],
    all_years: list[int],
    latest_year: int,
    prev_year: int | None,
) -> dict:
    state_gdp = [r for r in gdp_data if r["state_id"] == state_id]
    state_em = [r for r in emissions_data if r["state_id"] == state_id]

    if not state_gdp:
        return {"error": f"State '{state_id}' not found", "insights": [], "rankings": {}, "trend_data": []}

    state_gdp.sort(key=lambda r: r["year"])
    state_em.sort(key=lambda r: r["year"])

    state_name = state_gdp[0]["state"]
    latest = state_gdp[-1]
    prev = state_gdp[-2] if len(state_gdp) >= 2 else None

    latest_em = next((r for r in state_em if r["year"] == latest_year), None)
    prev_em = next((r for r in state_em if r["year"] == prev_year), None) if prev_year else None

    # Trend data
    trend_data = []
    for g in state_gdp:
        em = next((e for e in state_em if e["year"] == g["year"]), None)
        trend_data.append({
            "year": g["year"],
            "gdp_billion_inr": g["gdp_billion_inr"],
            "total_capacity_mw": g["total_capacity_mw"],
            "renewable_share_percent": g["renewable_share_percent"],
            "total_emissions_mt": em["total_emissions_mt"] if em else 0,
        })

    # Insights
    insights: list[dict] = []

    # 1. Capacity growth
    cap_values = [r["total_capacity_mw"] for r in state_gdp]
    cap_trend = _trend_direction(cap_values)
    if prev:
        cap_yoy = _yoy_growth(prev["total_capacity_mw"], latest["total_capacity_mw"])
        if cap_yoy is not None:
            direction = "grew" if cap_yoy > 0 else "declined"
            insights.append(_make_insight(
                "⚡", "Energy Capacity",
                f"{state_name}'s installed capacity {direction} by {abs(cap_yoy)}% to {latest['total_capacity_mw']:,} MW in {latest_year}.",
                cap_trend,
                "cyan" if cap_yoy > 0 else "red",
            ))

    # 2. Renewable share
    ren_values = [r["renewable_share_percent"] for r in state_gdp]
    ren_trend = _trend_direction(ren_values)
    ren_pct = latest["renewable_share_percent"]
    tier = "leader" if ren_pct >= 90 else "strong performer" if ren_pct >= 75 else "growing" if ren_pct >= 60 else "lagging"
    insights.append(_make_insight(
        "🌿", "Renewable Share",
        f"At {ren_pct}%, {state_name} is a {tier} in renewable energy adoption.",
        ren_trend,
        "green" if ren_pct >= 75 else "amber" if ren_pct >= 60 else "red",
    ))

    # 3. GDP growth
    gdp_values = [r["gdp_billion_inr"] for r in state_gdp]
    gdp_trend = _trend_direction(gdp_values)
    if prev:
        gdp_yoy = _yoy_growth(prev["gdp_billion_inr"], latest["gdp_billion_inr"])
        if gdp_yoy is not None:
            insights.append(_make_insight(
                "📈", "Economic Growth",
                f"GDP grew {gdp_yoy}% to ₹{latest['gdp_billion_inr']:,} billion in {latest_year}.",
                gdp_trend,
                "green" if gdp_yoy > 0 else "red",
            ))

    # 4. Emissions
    if latest_em and prev_em:
        em_yoy = _yoy_growth(prev_em["total_emissions_mt"], latest_em["total_emissions_mt"])
        em_values = [r.get("total_emissions_mt", 0) for r in state_em]
        em_trend = _trend_direction(em_values)
        if em_yoy is not None:
            direction = "increased" if em_yoy > 0 else "decreased"
            insights.append(_make_insight(
                "🏭", "Carbon Emissions",
                f"Total emissions {direction} by {abs(em_yoy)}% to {latest_em['total_emissions_mt']} MT in {latest_year}.",
                em_trend,
                "green" if em_yoy < 0 else "red",
            ))

    # Rankings
    rankings = {}
    for metric, label, higher in [
        ("total_capacity_mw", "Energy Capacity", True),
        ("renewable_share_percent", "Renewable Share", True),
        ("gdp_billion_inr", "GDP", True),
        ("total_emissions_mt", "Lowest Emissions", False),
    ]:
        ranked = _rank_states_by(metric, latest_year, higher_is_better=higher)
        for r in ranked:
            if r["state_id"] == state_id:
                rankings[label] = r["rank"]
                break

    return {
        "state_id": state_id,
        "state": state_name,
        "year": latest_year,
        "insights": insights,
        "rankings": rankings,
        "total_states": len({r["state_id"] for r in gdp_data}),
        "trend_data": trend_data,
    }


def _national_insights(
    gdp_data: list[dict],
    emissions_data: list[dict],
    all_years: list[int],
    latest_year: int,
    prev_year: int | None,
) -> dict:
    latest_rows = [r for r in gdp_data if r["year"] == latest_year]
    prev_rows = {r["state_id"]: r for r in gdp_data if r["year"] == prev_year} if prev_year else {}
    latest_em = {r["state_id"]: r for r in emissions_data if r["year"] == latest_year}

    total_cap = sum(r["total_capacity_mw"] for r in latest_rows)
    total_gdp = sum(r["gdp_billion_inr"] for r in latest_rows)
    avg_renewable = round(sum(r["renewable_share_percent"] for r in latest_rows) / len(latest_rows), 1) if latest_rows else 0
    total_emissions = sum(r.get("total_emissions_mt", 0) for r in latest_em.values())

    insights: list[dict] = []

    # 1. Total capacity
    if prev_rows:
        prev_cap = sum(r["total_capacity_mw"] for r in prev_rows.values())
        cap_yoy = _yoy_growth(prev_cap, total_cap)
        if cap_yoy is not None:
            insights.append(_make_insight(
                "⚡", "National Capacity",
                f"India's installed capacity reached {total_cap:,} MW in {latest_year}, up {cap_yoy}% YoY.",
                "rising" if cap_yoy > 0 else "falling",
                "cyan",
            ))

    # 2. Renewable average
    insights.append(_make_insight(
        "🌿", "Renewable Adoption",
        f"Average renewable share across states is {avg_renewable}% in {latest_year}.",
        "rising",
        "green",
    ))

    # 3. Top state
    top = max(latest_rows, key=lambda r: r["total_capacity_mw"])
    insights.append(_make_insight(
        "🏆", "Top State",
        f"{top['state']} leads with {top['total_capacity_mw']:,} MW installed capacity.",
        "stable",
        "amber",
    ))

    # 4. Emissions
    insights.append(_make_insight(
        "🏭", "National Emissions",
        f"Total emissions across tracked states: {total_emissions:,.1f} MT in {latest_year}.",
        "falling",
        "red",
    ))

    # Rankings
    rankings_data = {
        "capacity": _rank_states_by("total_capacity_mw", latest_year)[:10],
        "renewable": _rank_states_by("renewable_share_percent", latest_year)[:10],
        "gdp": _rank_states_by("gdp_billion_inr", latest_year)[:10],
    }

    # Trend data (aggregated by year)
    yearly: dict[int, dict] = defaultdict(lambda: {"gdp": 0, "capacity": 0, "emissions": 0, "count": 0, "ren_sum": 0})
    for r in gdp_data:
        y = yearly[r["year"]]
        y["gdp"] += r["gdp_billion_inr"]
        y["capacity"] += r["total_capacity_mw"]
        y["ren_sum"] += r["renewable_share_percent"]
        y["count"] += 1
    for r in emissions_data:
        yearly[r["year"]]["emissions"] += r.get("total_emissions_mt", 0)

    trend_data = [
        {
            "year": yr,
            "gdp_billion_inr": d["gdp"],
            "total_capacity_mw": d["capacity"],
            "renewable_share_percent": round(d["ren_sum"] / d["count"], 1) if d["count"] else 0,
            "total_emissions_mt": round(d["emissions"], 1),
        }
        for yr, d in sorted(yearly.items())
    ]

    return {
        "state_id": None,
        "state": "India (All States)",
        "year": latest_year,
        "insights": insights,
        "rankings": rankings_data,
        "total_states": len(latest_rows),
        "trend_data": trend_data,
    }

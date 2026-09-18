"""Sector dashboards built from the scraped datasets under api/data/scraped.

Each sector in the Simple view (Overview, Solar, Wind, Coal & Thermal, National
Grid) is assembled here from real source data rather than hard-coded figures:

  * CEA installed capacity (all-India monthly, and the RES sub-split)
  * CEA actual generation by mode, in billion units (BU)
  * CEA peak demand met, by state and month
  * CEA transmission line inventory
  * NIWE/NSRDB solar irradiance and wind resource summaries by state
  * NPCIL reactor fleet listing
  * Coal India production and off-take

Everything is parsed once and memoised, so a request only pays dictionary
lookups. Values are returned pre-computed; the frontend does no arithmetic.
"""

from __future__ import annotations

import json
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Optional

_SCRAPED = Path(__file__).resolve().parent.parent / "data" / "scraped"

# The scrape is stored under a dated folder per source. Resolve the most recent
# snapshot rather than pinning a date, so a re-run of the scrapers is picked up
# without touching this module.
_MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

SECTORS = ("overview", "solar", "wind", "coal", "grid")


class SectorDataUnavailable(RuntimeError):
    """Raised when a required scraped dataset is missing from disk."""


def _latest_snapshot(source: str) -> Optional[Path]:
    root = _SCRAPED / source
    if not root.is_dir():
        return None
    dated = sorted((p for p in root.iterdir() if p.is_dir()), reverse=True)
    return dated[0] if dated else None


@lru_cache(maxsize=None)
def _load(source: str, filename: str) -> Any:
    """Load one scraped JSON file from the newest snapshot of a source."""
    snapshot = _latest_snapshot(source)
    if snapshot is None:
        raise SectorDataUnavailable(f"no scraped snapshot for source '{source}'")
    path = snapshot / filename
    if not path.is_file():
        raise SectorDataUnavailable(f"missing {source}/{path.name}")
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _num(value: Any) -> float:
    """Parse a scraped numeric cell, tolerating blanks, commas and stray text."""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = str(value).replace(",", "").strip()
    if not cleaned:
        return 0.0
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def _month_key(label: str) -> tuple[int, int]:
    """Sort key for a 'Mon-YYYY' label, e.g. 'Dec-2025' -> (2025, 12)."""
    try:
        mon, year = str(label).strip().split("-")
        return (int(year), _MONTHS.get(mon[:3].lower(), 0))
    except (ValueError, AttributeError):
        return (0, 0)


def _dedupe_months(rows: list[dict], id_key: str) -> list[dict]:
    """Collapse revised monthly returns down to one row per month.

    From Dec-2024 the CEA republishes each month with a revised set of figures
    while keeping the superseded row in the feed. Both carry the same month
    label, so charting the raw list double-plots every recent month. The row
    with the highest record id is the later revision and wins.
    """
    latest_by_month: dict[str, dict] = {}
    for row in rows:
        month = row.get("month")
        held = latest_by_month.get(month)
        if held is None or _num(row.get(id_key)) >= _num(held.get(id_key)):
            latest_by_month[month] = row
    return sorted(latest_by_month.values(), key=lambda r: _month_key(r["month"]))


def _pct_change(current: float, previous: float) -> float:
    if not previous:
        return 0.0
    return round((current - previous) / previous * 100, 1)


def _trend(value: float) -> str:
    if value > 0:
        return "up"
    if value < 0:
        return "down"
    return "flat"


# ── source readers ────────────────────────────────────────────────

def _capacity_series() -> list[dict]:
    """All-India installed capacity by month (MW), oldest first."""
    rows = _load("cea", "installed_capacity_allindia.json")
    parsed = [
        {
            "month": r.get("month"),
            "id": r.get("id"),
            "coal": _num(r.get("coal")),
            "gas": _num(r.get("gas")),
            "diesel": _num(r.get("diesel")),
            "thermal": _num(r.get("thermal_total")),
            "nuclear": _num(r.get("nuclear")),
            "hydro": _num(r.get("hydro")),
            "res": _num(r.get("res")),
            "total": _num(r.get("grand_total")),
        }
        for r in rows
    ]
    return _dedupe_months(parsed, "id")


def _res_series() -> list[dict]:
    """Renewable capacity split by month (MW), oldest first."""
    rows = _load("cea", "installed_capacity_res.json")
    parsed = [
        {
            "month": r.get("Month"),
            "id": r.get("ID"),
            "solar": _num(r.get("solar_power")),
            "wind": _num(r.get("wind_power")),
            "small_hydro": _num(r.get("small_hydro_power")),
            "biomass": _num(r.get("bmpower_congen")),
            "waste": _num(r.get("wastetoenergy")),
        }
        for r in rows
    ]
    return _dedupe_months(parsed, "id")


def _generation_by_mode() -> list[dict]:
    """Monthly actual generation (BU) folded into renewable vs fossil."""
    by_fy = _load("cea", "power_generation.json")
    buckets: dict[str, dict[str, float]] = {}
    for rows in by_fy.values():
        for r in rows:
            month = r.get("Month")
            mode = str(r.get("mode", "")).strip().upper()
            # Only all-India rows; imports are excluded from the domestic mix.
            if str(r.get("Region_State", "")).strip().lower() != "all india":
                continue
            if "IMP" in mode:
                continue
            slot = buckets.setdefault(
                month,
                {"renewable": 0.0, "fossil": 0.0, "nuclear": 0.0, "_modes": set()},
            )
            value = _num(r.get("bus"))
            if mode in ("THERMAL",):
                slot["fossil"] += value
                slot["_modes"].add("THERMAL")
            elif mode in ("RENEWABLE", "HYDRO"):
                slot["renewable"] += value
                slot["_modes"].add(mode)
            elif mode == "NUCLEAR":
                slot["nuclear"] += value
    # Only months with a thermal return are usable; a month filed without one
    # would otherwise chart as a collapse in fossil output. Note that this CEA
    # feed reports HYDRO and NUCLEAR separately but rarely breaks out a
    # RENEWABLE mode, so "renewable" here is predominantly large hydro — it is
    # not a substitute for the installed-capacity RES series.
    series = [
        {
            "month": month,
            "renewable": round(vals["renewable"], 2),
            "fossil": round(vals["fossil"], 2),
            "nuclear": round(vals["nuclear"], 2),
        }
        for month, vals in buckets.items()
        if "THERMAL" in vals["_modes"]
    ]
    return sorted(series, key=lambda r: _month_key(r["month"]))


def _all_india_peak() -> list[dict]:
    """All-India peak demand and peak met by month (MW), oldest first."""
    by_fy = _load("cea", "psp_peak.json")
    seen: dict[str, dict] = {}
    for rows in by_fy.values():
        for r in rows:
            if str(r.get("State", "")).strip().lower() != "all india":
                continue
            month = r.get("Month")
            demand = _num(r.get("peak_demand"))
            met = _num(r.get("peak_met"))
            if not demand:
                continue
            seen[month] = {
                "month": month,
                "peak_demand_mw": round(demand),
                "peak_met_mw": round(met),
                "deficit_pct": round((demand - met) / demand * 100, 2) if demand else 0.0,
            }
    return sorted(seen.values(), key=lambda r: _month_key(r["month"]))


def _solar_resource_by_state() -> list[dict]:
    """Annual solar resource per state, from the Solargis prospect payload.

    The scraper also writes solar_summary_table.json, but that flattening step
    yields null irradiance columns, so the per-state payload is read directly.
    Figures are annual totals; the per-day values the industry quotes are the
    annual divided by 365.
    """
    raw = _load("solar_atlas", "solar_irradiation_india.json")
    out: list[dict] = []
    for state, payload in raw.items():
        annual = (
            payload.get("solar_data", {}).get("annual", {}).get("data", {})
        )
        ghi = _num(annual.get("GHI"))
        if not ghi:
            continue
        out.append({
            "state": state,
            "ghi_annual": round(ghi, 1),
            "ghi_daily": round(ghi / 365, 2),
            "dni_daily": round(_num(annual.get("DNI")) / 365, 2),
            "pvout": round(_num(annual.get("PVOUT_csi")), 1),
            "temp": round(_num(annual.get("TEMP")), 1),
        })
    return sorted(out, key=lambda r: r["ghi_annual"], reverse=True)


def _coal_production_by_subsidiary() -> list[dict]:
    """Coal India production and off-take per subsidiary, in million tonnes.

    The published table is laid out with subsidiaries as columns and COAL /
    OFFTAKE as rows, so it is pivoted here into one record per subsidiary.
    """
    tables = _load("coal_india", "physical_tables.json").get("tables", [])
    for table in tables:
        headers = [str(h).strip() for h in table.get("headers", [])]
        if not headers or headers[0].upper() != "DETAILS":
            continue
        # Columns after DETAILS and UNIT are the subsidiary names.
        names = headers[2:]
        rows_by_label = {
            str(r[0]).strip().upper(): r[2:]
            for r in table.get("data", []) if r
        }
        production = rows_by_label.get("COAL", [])
        offtake = rows_by_label.get("OFFTAKE", [])
        if not production:
            continue
        out = []
        for idx, name in enumerate(names):
            prod = _num(production[idx]) if idx < len(production) else 0.0
            off = _num(offtake[idx]) if idx < len(offtake) else 0.0
            if not prod and not off:
                continue
            out.append({
                "company": name,
                "production_mt": round(prod, 1),
                "offtake_mt": round(off, 1),
                "offtake_ratio": round(off / prod * 100, 1) if prod else 0.0,
            })
        # Report the subsidiaries largest-first, with the CIL total last.
        subsidiaries = [r for r in out if r["company"].upper() != "CIL"]
        total = [r for r in out if r["company"].upper() == "CIL"]
        subsidiaries.sort(key=lambda r: r["production_mt"], reverse=True)
        return subsidiaries + total
    return []


def _tail(series: list[dict], count: int) -> list[dict]:
    return series[-count:] if len(series) > count else series


def _metric(label: str, value: str, unit: str = "", change: float = 0.0,
            sub: str = "") -> dict:
    return {
        "label": label,
        "value": value,
        "unit": unit,
        "change_pct": change,
        "trend": _trend(change),
        "sub": sub,
    }


def _yoy(series: list[dict], field: str) -> tuple[float, float]:
    """Latest value and its year-on-year change for a monthly series."""
    if not series:
        return 0.0, 0.0
    latest = series[-1].get(field, 0.0)
    prior = series[-13].get(field, 0.0) if len(series) >= 13 else series[0].get(field, 0.0)
    return latest, _pct_change(latest, prior)


# ── sector builders ───────────────────────────────────────────────

def _overview() -> dict:
    cap = _capacity_series()
    gen = _generation_by_mode()
    peak = _all_india_peak()

    latest = cap[-1]
    total_gw = latest["total"] / 1000
    _, total_change = _yoy(cap, "total")
    res_gw = latest["res"] / 1000
    _, res_change = _yoy(cap, "res")
    res_share = round(latest["res"] / latest["total"] * 100, 1) if latest["total"] else 0.0

    peak_latest = peak[-1] if peak else {"peak_demand_mw": 0, "month": "—"}
    peak_gw = peak_latest["peak_demand_mw"] / 1000
    peak_change = 0.0
    if len(peak) >= 13:
        peak_change = _pct_change(
            peak_latest["peak_demand_mw"], peak[-13]["peak_demand_mw"]
        )

    fossil_gw = (latest["coal"] + latest["gas"] + latest["diesel"]) / 1000
    _, fossil_change = _yoy(cap, "coal")

    return {
        "headline": (
            f"India has {total_gw:,.0f} GW of installed generation capacity, "
            f"{res_share:.0f}% of it renewable."
        ),
        "subtitle": (
            "Installed capacity, actual generation and peak demand for the "
            "national grid, compiled from Central Electricity Authority returns."
        ),
        "as_of": latest["month"],
        "metrics": [
            _metric("Total Capacity", f"{total_gw:,.1f}", "GW", total_change,
                    f"All sources as of {latest['month']}"),
            _metric("Renewable Capacity", f"{res_gw:,.1f}", "GW", res_change,
                    f"{res_share:.1f}% of the national mix"),
            _metric("Fossil Capacity", f"{fossil_gw:,.1f}", "GW", fossil_change,
                    "Coal, gas and diesel combined"),
            _metric("Peak Demand", f"{peak_gw:,.1f}", "GW", peak_change,
                    f"Highest demand met in {peak_latest['month']}"),
        ],
        "chart": {
            "title": "Renewable vs. Fossil Capacity",
            "subtitle": "Installed all-India capacity by month, in gigawatts",
            "unit": " GW",
            "x_key": "month",
            "series": [
                {"key": "renewable_gw", "label": "Renewable", "color": "#20d3ee"},
                {"key": "fossil_gw", "label": "Fossil Fuel", "color": "#475569"},
            ],
            "data": [
                {
                    "month": r["month"],
                    "renewable_gw": round(r["res"] / 1000, 2),
                    "fossil_gw": round(
                        (r["coal"] + r["gas"] + r["diesel"]) / 1000, 2
                    ),
                }
                for r in _tail(cap, 36)
            ],
        },
        "table": {
            "title": "Capacity Mix",
            "columns": [
                {"key": "source", "label": "Source"},
                {"key": "capacity_gw", "label": "Capacity (GW)", "numeric": True},
                {"key": "share_pct", "label": "Share (%)", "numeric": True},
            ],
            "rows": [
                {
                    "source": name,
                    "capacity_gw": round(latest[field] / 1000, 2),
                    "share_pct": round(latest[field] / latest["total"] * 100, 1)
                    if latest["total"] else 0.0,
                }
                for name, field in (
                    ("Coal", "coal"), ("Renewables", "res"), ("Hydro", "hydro"),
                    ("Gas", "gas"), ("Nuclear", "nuclear"), ("Diesel", "diesel"),
                )
            ],
        },
        "source": "Central Electricity Authority (CEA) — installed capacity, "
                  "generation and peak demand returns",
    }


def _renewable_sector(kind: str) -> dict:
    """Shared builder for the solar and wind sectors."""
    res = _res_series()
    latest = res[-1]
    value_mw, change = _yoy(res, kind)
    value_gw = value_mw / 1000

    res_total = sum(
        latest[k] for k in ("solar", "wind", "small_hydro", "biomass", "waste")
    )
    share = round(value_mw / res_total * 100, 1) if res_total else 0.0

    # Five years back, to show the build-out rather than a single month.
    base = res[-61] if len(res) >= 61 else res[0]
    growth_multiple = (value_mw / base[kind]) if base.get(kind) else 0.0

    if kind == "solar":
        ranked = _solar_resource_by_state()
        rows = [
            {
                "state": r["state"],
                "resource": r["ghi_daily"],
                "secondary": r["dni_daily"],
                "yield": r["pvout"],
                "temp": r["temp"],
            }
            for r in ranked[:15]
        ]
        table = {
            "title": "Solar Resource by State",
            "subtitle": "Ranked by global horizontal irradiance",
            "columns": [
                {"key": "state", "label": "State"},
                {"key": "resource", "label": "GHI (kWh/m²/day)", "numeric": True},
                {"key": "secondary", "label": "DNI (kWh/m²/day)", "numeric": True},
                {"key": "yield", "label": "PV Yield (kWh/kWp/yr)", "numeric": True},
                {"key": "temp", "label": "Avg Temp (°C)", "numeric": True},
            ],
            "rows": rows,
        }
        headline = (
            f"India's solar fleet has reached {value_gw:,.1f} GW, "
            f"{share:.0f}% of all renewable capacity."
        )
        subtitle = ("Grid-connected solar build-out and the underlying irradiance "
                    "resource that drives it.")
        colour = "#facc15"
        series_label = "Solar Capacity"
        source = ("CEA renewable capacity returns; irradiance from the Global Solar "
                  "Atlas state summary")
    else:
        atlas = _load("wind_atlas", "wind_summary_table.json")
        ranked = sorted(
            atlas, key=lambda r: _num(r.get("wind_speed_50m_ms")), reverse=True
        )
        rows = [
            {
                "state": r.get("state"),
                "resource": round(_num(r.get("wind_speed_50m_ms")), 2),
                "secondary": round(_num(r.get("wind_speed_50m_max_ms")), 2),
                "temp": round(_num(r.get("wind_speed_10m_ms")), 2),
            }
            for r in ranked[:15]
        ]
        table = {
            "title": "Wind Resource by State",
            "subtitle": "Ranked by mean wind speed at 50 m hub height",
            "columns": [
                {"key": "state", "label": "State"},
                {"key": "resource", "label": "Mean @50m (m/s)", "numeric": True},
                {"key": "secondary", "label": "Peak @50m (m/s)", "numeric": True},
                {"key": "temp", "label": "Mean @10m (m/s)", "numeric": True},
            ],
            "rows": rows,
        }
        headline = (
            f"India's wind fleet stands at {value_gw:,.1f} GW, "
            f"{share:.0f}% of all renewable capacity."
        )
        subtitle = ("Grid-connected wind build-out alongside the measured wind "
                    "resource at hub height.")
        colour = "#38bdf8"
        series_label = "Wind Capacity"
        source = ("CEA renewable capacity returns; wind resource from the Global "
                  "Wind Atlas state summary")

    chart_data = [
        {"month": r["month"], "capacity_gw": round(r[kind] / 1000, 2)}
        for r in _tail(res, 36)
    ]

    return {
        "headline": headline,
        "subtitle": subtitle,
        "as_of": latest["month"],
        "metrics": [
            _metric(f"{series_label}", f"{value_gw:,.1f}", "GW", change,
                    f"Installed as of {latest['month']}"),
            _metric("Share of Renewables", f"{share:,.1f}", "%", 0.0,
                    "Of total RES capacity"),
            _metric("5-Year Growth", f"{growth_multiple:,.1f}", "×", 0.0,
                    f"Versus {base['month']}"),
            _metric("States Surveyed", f"{len(table['rows'])}", "", 0.0,
                    "Top resource-ranked states shown"),
        ],
        "chart": {
            "title": f"{series_label} Build-out",
            "subtitle": "Cumulative grid-connected capacity by month",
            "unit": " GW",
            "x_key": "month",
            "series": [
                {"key": "capacity_gw", "label": series_label, "color": colour},
            ],
            "data": chart_data,
        },
        "table": table,
        "source": source,
    }


def _coal() -> dict:
    cap = _capacity_series()
    gen = _generation_by_mode()
    latest = cap[-1]

    coal_gw = latest["coal"] / 1000
    _, coal_change = _yoy(cap, "coal")
    thermal_gw = latest["thermal"] / 1000
    _, thermal_change = _yoy(cap, "thermal")
    thermal_share = (
        round(latest["thermal"] / latest["total"] * 100, 1) if latest["total"] else 0.0
    )

    fossil_gen, fossil_gen_change = _yoy(gen, "fossil")

    try:
        production_rows = _coal_production_by_subsidiary()
    except SectorDataUnavailable:
        production_rows = []

    if production_rows:
        table = {
            "title": "Coal India Production & Off-take",
            "subtitle": "Year-to-date by subsidiary, in million tonnes",
            "columns": [
                {"key": "company", "label": "Subsidiary"},
                {"key": "production_mt", "label": "Production (MT)", "numeric": True},
                {"key": "offtake_mt", "label": "Off-take (MT)", "numeric": True},
                {"key": "offtake_ratio", "label": "Off-take / Production (%)", "numeric": True},
            ],
            "rows": production_rows,
        }
    else:
        table = {
            "title": "Thermal Capacity Mix",
            "subtitle": "Installed thermal capacity by fuel",
            "columns": [
                {"key": "source", "label": "Fuel"},
                {"key": "capacity_gw", "label": "Capacity (GW)", "numeric": True},
            ],
            "rows": [
                {"source": n, "capacity_gw": round(latest[f] / 1000, 2)}
                for n, f in (("Coal", "coal"), ("Gas", "gas"), ("Diesel", "diesel"))
            ],
        }

    return {
        "headline": (
            f"Coal still anchors the grid at {coal_gw:,.1f} GW, "
            f"{thermal_share:.0f}% of capacity is thermal."
        ),
        "subtitle": ("Thermal capacity, actual fossil generation and Coal India's "
                     "production performance."),
        "as_of": latest["month"],
        "metrics": [
            _metric("Coal Capacity", f"{coal_gw:,.1f}", "GW", coal_change,
                    f"Installed as of {latest['month']}"),
            _metric("Thermal Total", f"{thermal_gw:,.1f}", "GW", thermal_change,
                    "Coal, gas and diesel"),
            _metric("Thermal Share", f"{thermal_share:,.1f}", "%", 0.0,
                    "Of total installed capacity"),
            _metric("Fossil Generation", f"{fossil_gen:,.1f}", "BU",
                    fossil_gen_change, "Most recent month reported"),
        ],
        "chart": {
            "title": "Thermal Capacity by Fuel",
            "subtitle": "Installed coal and gas capacity by month",
            "unit": " GW",
            "x_key": "month",
            "series": [
                {"key": "coal_gw", "label": "Coal", "color": "#f97316"},
                {"key": "gas_gw", "label": "Gas", "color": "#a78bfa"},
            ],
            "data": [
                {
                    "month": r["month"],
                    "coal_gw": round(r["coal"] / 1000, 2),
                    "gas_gw": round(r["gas"] / 1000, 2),
                }
                for r in _tail(cap, 36)
            ],
        },
        "table": table,
        "source": "CEA installed capacity and generation returns; Coal India "
                  "provisional production reports",
    }


def _grid() -> dict:
    peak = _all_india_peak()
    cap = _capacity_series()
    latest_peak = peak[-1]

    peak_gw = latest_peak["peak_demand_mw"] / 1000
    peak_change = 0.0
    if len(peak) >= 13:
        peak_change = _pct_change(
            latest_peak["peak_demand_mw"], peak[-13]["peak_demand_mw"]
        )
    deficit = latest_peak["deficit_pct"]
    met_gw = latest_peak["peak_met_mw"] / 1000

    # Transmission inventory, aggregated by voltage class.
    lines = _load("cea", "transmission_lines.json")
    by_voltage: dict[str, dict] = {}
    for row in lines:
        kv = str(row.get("voltage_level", "")).strip()
        if not kv:
            continue
        slot = by_voltage.setdefault(kv, {"voltage": f"{kv} kV", "circuits": 0,
                                          "length_ckm": 0.0, "_kv": _num(kv)})
        slot["circuits"] += 1
        slot["length_ckm"] += _num(row.get("line_length"))
    voltage_rows = sorted(by_voltage.values(), key=lambda r: r["_kv"], reverse=True)
    for r in voltage_rows:
        r["length_ckm"] = round(r["length_ckm"])
        r.pop("_kv", None)
    total_ckm = sum(r["length_ckm"] for r in voltage_rows)

    return {
        "headline": (
            f"Peak demand reached {peak_gw:,.1f} GW with a "
            f"{deficit:.2f}% shortfall against supply."
        ),
        "subtitle": ("Peak demand met, supply shortfall and the transmission "
                     "backbone carrying it."),
        "as_of": latest_peak["month"],
        "metrics": [
            _metric("Peak Demand", f"{peak_gw:,.1f}", "GW", peak_change,
                    f"Recorded in {latest_peak['month']}"),
            _metric("Peak Met", f"{met_gw:,.1f}", "GW", 0.0,
                    "Supply actually delivered"),
            _metric("Supply Deficit", f"{deficit:,.2f}", "%", 0.0,
                    "Unmet share of peak demand"),
            _metric("Transmission Lines", f"{total_ckm:,.0f}", "ckm", 0.0,
                    f"Across {len(voltage_rows)} voltage classes"),
        ],
        "chart": {
            "title": "Peak Demand vs Peak Met",
            "subtitle": "All-India monthly peak, in gigawatts",
            "unit": " GW",
            "x_key": "month",
            "series": [
                {"key": "demand_gw", "label": "Peak Demand", "color": "#20d3ee"},
                {"key": "met_gw", "label": "Peak Met", "color": "#475569"},
            ],
            "data": [
                {
                    "month": r["month"],
                    "demand_gw": round(r["peak_demand_mw"] / 1000, 2),
                    "met_gw": round(r["peak_met_mw"] / 1000, 2),
                }
                for r in _tail(peak, 24)
            ],
        },
        "table": {
            "title": "Transmission Network by Voltage",
            "subtitle": "Commissioned circuit length on record",
            "columns": [
                {"key": "voltage", "label": "Voltage"},
                {"key": "circuits", "label": "Lines", "numeric": True},
                {"key": "length_ckm", "label": "Length (ckm)", "numeric": True},
            ],
            "rows": voltage_rows,
        },
        "source": "CEA peak power supply position and transmission line inventory",
    }


_BUILDERS = {
    "overview": _overview,
    "solar": lambda: _renewable_sector("solar"),
    "wind": lambda: _renewable_sector("wind"),
    "coal": _coal,
    "grid": _grid,
}

_META = {
    "overview": {"label": "Overview", "icon": "dashboard"},
    "solar": {"label": "Solar Energy", "icon": "wb_sunny"},
    "wind": {"label": "Wind Power", "icon": "air"},
    "coal": {"label": "Coal & Thermal", "icon": "factory"},
    "grid": {"label": "National Grid", "icon": "grid_view"},
}


def list_sectors() -> list[dict]:
    """Sector ids and display metadata for the sidebar."""
    return [{"id": s, **_META[s]} for s in SECTORS]


@lru_cache(maxsize=len(SECTORS))
def get_sector(sector_id: str) -> dict:
    """Build the dashboard payload for one sector."""
    builder = _BUILDERS[sector_id]
    payload = builder()
    payload["id"] = sector_id
    payload["label"] = _META[sector_id]["label"]
    payload["icon"] = _META[sector_id]["icon"]
    return payload

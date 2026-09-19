"""Catalogue of the datasets behind the atlas, for the Datasets view.

Lists every scraped source the API serves from — where it came from, how many
records it holds, what period it covers and when the snapshot was taken — and
exposes each one as raw JSON so it can be inspected or reused directly.

The live-generation and market-price feeds are listed too, flagged as
simulated: they are generated per request from installed capacity rather than
read from a source, and the catalogue says so instead of implying otherwise.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Optional

from api.services.sector_service import (
    SectorDataUnavailable,
    _latest_snapshot,
    _load,
    _month_key,
)

# id -> (source folder, file, display name, publisher, source url)
_SCRAPED: dict[str, tuple[str, str, str, str, str]] = {
    "installed_capacity_allindia": (
        "cea", "installed_capacity_allindia.json",
        "Installed capacity — all India, by fuel",
        "Central Electricity Authority", "https://cea.nic.in/api/installed_capacity_allindia.php",
    ),
    "installed_capacity_res": (
        "cea", "installed_capacity_res.json",
        "Installed capacity — renewables split",
        "Central Electricity Authority", "https://cea.nic.in/api/instcap_allindia_res.php",
    ),
    "installed_capacity_statewise": (
        "cea", "installed_capacity_statewise.json",
        "Installed capacity — by state",
        "Central Electricity Authority", "https://cea.nic.in/api/installed_capacity_statewise.php",
    ),
    "installed_capacity_regionwise": (
        "cea", "installed_capacity_regionwise.json",
        "Installed capacity — by region",
        "Central Electricity Authority", "https://cea.nic.in/api/installed_capacity.php",
    ),
    "installed_capacity_composition": (
        "cea", "installed_capacity_composition.json",
        "Installed capacity — ownership composition",
        "Central Electricity Authority", "https://cea.nic.in/api/installed_capacity_composition.php",
    ),
    "power_generation": (
        "cea", "power_generation.json",
        "Generation by mode",
        "Central Electricity Authority", "https://cea.nic.in/api/power_generation.php",
    ),
    "renewable_energy": (
        "cea", "renewable_energy.json",
        "Renewable generation",
        "Central Electricity Authority", "https://cea.nic.in/api/renewable_energy.php",
    ),
    "psp_peak": (
        "cea", "psp_peak.json",
        "Peak demand and peak met",
        "Central Electricity Authority", "https://cea.nic.in/api/psp_peak.php",
    ),
    "psp_energy": (
        "cea", "psp_energy.json",
        "Energy requirement and supply",
        "Central Electricity Authority", "https://cea.nic.in/api/psp_energy.php",
    ),
    "transmission_lines": (
        "cea", "transmission_lines.json",
        "Commissioned transmission lines",
        "Central Electricity Authority", "https://cea.nic.in/api/transmission_lines.php",
    ),
    "transformation_capacity": (
        "cea", "transformation_capacity.json",
        "Substation transformation capacity",
        "Central Electricity Authority", "https://cea.nic.in/api/transformation_substations.php",
    ),
    "per_capita_consumption": (
        "cea", "per_capita_consumption.json",
        "Per capita electricity consumption",
        "Central Electricity Authority", "https://cea.nic.in/api/percapitalConsumtion.php",
    ),
    "solar_resource": (
        "solar_atlas", "solar_irradiation_india.json",
        "Solar resource by state (GHI, DNI, PV yield)",
        "Global Solar Atlas (Solargis)", "https://globalsolaratlas.info",
    ),
    "wind_resource": (
        "wind_atlas", "wind_summary_table.json",
        "Wind resource by state (hub-height speeds)",
        "Global Wind Atlas", "https://globalwindatlas.info",
    ),
    "coal_india_production": (
        "coal_india", "physical_tables.json",
        "Coal India production and off-take",
        "Coal India Limited", "https://www.coalindia.in/performance/physical/",
    ),
}

_SIMULATED = [
    {
        "id": "live_generation",
        "name": "Live generation by state",
        "publisher": "Simulated",
        "kind": "simulated",
        "note": "Generated per request from 2026 installed capacity with randomised "
                "utilisation factors. Not a live grid feed.",
    },
    {
        "id": "market_pricing",
        "name": "Day-ahead market prices",
        "publisher": "Simulated",
        "kind": "simulated",
        "note": "Hourly-seeded simulation of IEX clearing prices. Not market data.",
    },
]


def _records(payload: Any) -> list[dict]:
    """Flatten a payload to its record rows, whatever its shape."""
    if isinstance(payload, list):
        return [r for r in payload if isinstance(r, dict)]
    if isinstance(payload, dict):
        # Scraped HTML pages: count table rows, not the tables themselves.
        tables = payload.get("tables")
        if isinstance(tables, list):
            return [
                {"row": row} for t in tables if isinstance(t, dict)
                for row in t.get("data", [])
            ]
        # Payloads keyed by financial year hold a list per key.
        lists = [v for v in payload.values() if isinstance(v, list)]
        if lists:
            return [r for v in lists for r in v if isinstance(r, dict)]
        # Keyed by state (the Solargis payload): one record per key.
        if all(isinstance(v, dict) for v in payload.values()):
            return list(payload.values())
    return []


def _coverage(rows: list[dict]) -> Optional[dict]:
    """First and last month across rows carrying a 'Mon-YYYY' month field."""
    months = [
        str(r.get("month") or r.get("Month") or "").strip()
        for r in rows if isinstance(r, dict)
    ]
    # Several CEA feeds pad rows with epoch placeholders (Jan-1900, Jan-1970);
    # reporting those as coverage would claim a century of data that is not
    # there, so anything before 2000 is treated as a placeholder.
    months = [m for m in months if _month_key(m)[0] >= 2000]
    if not months:
        return None
    ordered = sorted(set(months), key=_month_key)
    return {"from": ordered[0], "to": ordered[-1]}


@lru_cache(maxsize=1)
def list_datasets() -> list[dict]:
    """Catalogue entries; computed once per process, as snapshots only change on deploy."""
    out: list[dict] = []
    for dataset_id, (source, filename, name, publisher, url) in _SCRAPED.items():
        snapshot = _latest_snapshot(source)
        entry: dict[str, Any] = {
            "id": dataset_id,
            "name": name,
            "publisher": publisher,
            "source_url": url,
            "kind": "scraped",
            "snapshot": snapshot.name if snapshot else None,
        }
        try:
            payload = _load(source, filename)
            rows = _records(payload)
            entry["records"] = len(rows)
            entry["coverage"] = _coverage(rows)
            entry["available"] = True
        except SectorDataUnavailable:
            entry.update(records=0, coverage=None, available=False)
        out.append(entry)
    return out + _SIMULATED


def get_dataset(dataset_id: str) -> Any:
    """Raw payload for one scraped dataset. Raises KeyError for unknown ids."""
    source, filename, *_ = _SCRAPED[dataset_id]
    return _load(source, filename)

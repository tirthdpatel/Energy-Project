"""CEA extractor — refreshes the Central Electricity Authority JSON feeds.

These are the datasets behind the Simple view's sector dashboards
(/api/sectors): installed capacity, renewable capacity, generation by mode,
peak demand and the transmission inventory.

The endpoint map below is the one recorded in the existing snapshot at
api/data/scraped/cea/<date>/cea_api_data.json. Each endpoint returns plain
JSON, so there is no HTML or PDF parsing to do — the work is validating the
response and writing it out in the layout the API already reads.

Guarding against bad refreshes matters more than speed here: cea.nic.in is
frequently unreachable from outside India and sometimes answers with an HTML
error page carrying a 200 status. A response that does not look like the
dataset it claims to be is rejected, and a run that cannot validate every
endpoint leaves the previous snapshot untouched rather than half-replacing it.

Usage:
    python -m scrapers.cea_extractor                 # write a new snapshot
    python -m scrapers.cea_extractor --check         # validate the last one
    python -m scrapers.cea_extractor --out DIR       # override destination
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional

try:
    import httpx
except ImportError:  # pragma: no cover - dependency is declared in requirements
    httpx = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

API_BASE = "https://cea.nic.in/api"

# filename stem -> (url, description, a column that every record must carry)
ENDPOINTS: dict[str, tuple[str, str, str]] = {
    "installed_capacity_allindia": (
        f"{API_BASE}/installed_capacity_allindia.php",
        "All India Installed Capacity (sector-wise)",
        "grand_total",
    ),
    "installed_capacity_res": (
        f"{API_BASE}/instcap_allindia_res.php",
        "All India Installed Capacity — renewables split",
        "solar_power",
    ),
    "installed_capacity_regionwise": (
        f"{API_BASE}/installed_capacity.php",
        "Installed Capacity by region",
        "",
    ),
    "installed_capacity_statewise": (
        f"{API_BASE}/installed_capacity_statewise.php",
        "Installed Capacity by state",
        "",
    ),
    "installed_capacity_composition": (
        f"{API_BASE}/installed_capacity_composition.php",
        "Installed Capacity composition",
        "",
    ),
    "power_generation": (
        f"{API_BASE}/power_generation.php",
        "Actual generation by mode, in billion units",
        "",
    ),
    "renewable_energy": (
        f"{API_BASE}/renewable_energy.php",
        "Renewable generation",
        "",
    ),
    "psp_energy": (
        f"{API_BASE}/psp_energy.php",
        "Power supply position — energy",
        "",
    ),
    "psp_peak": (
        f"{API_BASE}/psp_peak.php",
        "Power supply position — peak demand and peak met",
        "",
    ),
    "transmission_lines": (
        f"{API_BASE}/transmission_lines.php",
        "Commissioned transmission lines",
        "line_length",
    ),
    "transformation_capacity": (
        f"{API_BASE}/transformation_substations.php",
        "Transformation capacity at substations",
        "",
    ),
    "per_capita_consumption": (
        f"{API_BASE}/percapitalConsumtion.php",
        "Per capita electricity consumption",
        "",
    ),
}

# Where the web API reads its data from.
DEFAULT_OUT = (
    Path(__file__).resolve().parents[2]
    / "web" / "frontend" / "api" / "data" / "scraped" / "cea"
)

REQUEST_TIMEOUT = 60.0
MAX_ATTEMPTS = 3


class CeaRefreshError(RuntimeError):
    """Raised when a refresh cannot be completed safely."""


def _records(payload: Any) -> list[dict]:
    """Flatten a CEA payload to a flat record list.

    Most endpoints return a list. A few (power_generation, psp_peak) return an
    object keyed by financial year, each holding its own list.
    """
    if isinstance(payload, list):
        return [r for r in payload if isinstance(r, dict)]
    if isinstance(payload, dict):
        out: list[dict] = []
        for value in payload.values():
            if isinstance(value, list):
                out.extend(r for r in value if isinstance(r, dict))
        return out
    return []


def validate(name: str, payload: Any, required_field: str = "") -> int:
    """Check a payload looks like the dataset it claims to be.

    Returns the record count. Raises CeaRefreshError when the response is not
    usable, so a bad fetch can never overwrite a good snapshot.
    """
    if payload is None:
        raise CeaRefreshError(f"{name}: response was not JSON")
    if not isinstance(payload, (list, dict)):
        raise CeaRefreshError(f"{name}: expected a list or object, got {type(payload).__name__}")

    rows = _records(payload)
    if not rows:
        raise CeaRefreshError(f"{name}: payload carried no records")

    if required_field and required_field not in rows[0]:
        raise CeaRefreshError(
            f"{name}: records are missing the expected '{required_field}' column "
            f"(saw: {', '.join(list(rows[0])[:8])})"
        )
    return len(rows)


def fetch(url: str, client: "httpx.Client") -> Any:
    """GET one endpoint, retrying transient failures."""
    last: Optional[Exception] = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = client.get(url)
            response.raise_for_status()
            try:
                return response.json()
            except ValueError as exc:
                # A 200 carrying an HTML error page is the common failure here.
                raise CeaRefreshError(
                    f"{url}: response was not JSON (content-type "
                    f"{response.headers.get('content-type', 'unknown')})"
                ) from exc
        except Exception as exc:  # network, status, or decode
            last = exc
            logger.warning("attempt %d/%d failed for %s: %s",
                           attempt, MAX_ATTEMPTS, url, exc)
    raise CeaRefreshError(f"{url}: giving up after {MAX_ATTEMPTS} attempts ({last})")


def write_snapshot(results: dict[str, Any], out_root: Path,
                   snapshot_date: Optional[str] = None) -> Path:
    """Write validated payloads as a dated snapshot, matching the existing layout."""
    stamp = snapshot_date or date.today().isoformat()
    target = out_root / stamp
    target.mkdir(parents=True, exist_ok=True)

    combined: dict[str, Any] = {}
    for name, payload in results.items():
        url, description, _ = ENDPOINTS[name]
        with open(target / f"{name}.json", "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False)
        combined[name] = {
            "url": url,
            "description": description,
            "record_count": len(_records(payload)),
            "data": payload,
        }

    with open(target / "cea_api_data.json", "w", encoding="utf-8") as fh:
        json.dump(
            {
                "fetched_at": datetime.now().isoformat(),
                "api_base": API_BASE,
                "endpoints": combined,
            },
            fh,
            ensure_ascii=False,
        )
    return target


def refresh(out_root: Path = DEFAULT_OUT,
            snapshot_date: Optional[str] = None) -> Path:
    """Fetch and validate every endpoint, then write the snapshot.

    Nothing is written unless all endpoints validate, so a partial outage
    cannot leave the site serving a half-updated dataset.
    """
    if httpx is None:
        raise CeaRefreshError("httpx is not installed — pip install -r requirements.txt")

    results: dict[str, Any] = {}
    headers = {
        "User-Agent": "india-energy-atlas/1.0 (+https://github.com/tirthdpatel/Energy-Project)",
        "Accept": "application/json",
    }
    with httpx.Client(timeout=REQUEST_TIMEOUT, headers=headers,
                      follow_redirects=True) as client:
        for name, (url, _, required) in ENDPOINTS.items():
            logger.info("fetching %s", name)
            payload = fetch(url, client)
            count = validate(name, payload, required)
            logger.info("  %s: %d records", name, count)
            results[name] = payload

    target = write_snapshot(results, out_root, snapshot_date)
    logger.info("wrote snapshot to %s", target)
    return target


def check(out_root: Path = DEFAULT_OUT) -> int:
    """Validate the newest snapshot already on disk. Returns an exit code."""
    snapshots = sorted((p for p in out_root.iterdir() if p.is_dir()), reverse=True) \
        if out_root.is_dir() else []
    if not snapshots:
        logger.error("no snapshot found under %s", out_root)
        return 1

    latest = snapshots[0]
    logger.info("checking %s", latest)
    failures = 0
    for name, (_, _, required) in ENDPOINTS.items():
        path = latest / f"{name}.json"
        if not path.is_file():
            logger.error("  %-34s MISSING", name)
            failures += 1
            continue
        try:
            with open(path, "r", encoding="utf-8") as fh:
                count = validate(name, json.load(fh), required)
            logger.info("  %-34s ok (%d records)", name, count)
        except (CeaRefreshError, ValueError) as exc:
            logger.error("  %-34s %s", name, exc)
            failures += 1
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="validate the newest snapshot on disk instead of fetching")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT,
                        help=f"snapshot root (default: {DEFAULT_OUT})")
    parser.add_argument("--date", dest="snapshot_date", default=None,
                        help="snapshot folder name (default: today)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    if args.check:
        return check(args.out)
    try:
        refresh(args.out, args.snapshot_date)
    except CeaRefreshError as exc:
        logger.error("refresh failed: %s", exc)
        logger.error("the previous snapshot has been left untouched")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""
India Energy Atlas — Full Stress Test, Data Extraction & Parity Audit
=====================================================================
Generates:
  - stress_results.json   (raw metrics per concurrency level)
  - stress_report.md       (human-readable report)
  - local_site_data_dump.json
  - state_year_matrix.csv
  - power_plants_all.csv
  - analytics_correlation_by_year.csv
  - data_parity_audit.json
  - data_parity_audit.md
"""

import asyncio, aiohttp, json, csv, time, statistics, os, sys
from datetime import datetime
from pathlib import Path

BASE = "http://127.0.0.1:8000"
OUT = Path(__file__).parent / "audit_output"
OUT.mkdir(exist_ok=True)

# ─── ENDPOINTS TO STRESS ──────────────────────────────────
ENDPOINTS = [
    "/api/states",
    "/api/states/geojson",
    "/api/states/maharashtra",
    "/api/states/gujarat?year=2024",
    "/api/states/tamil_nadu?year=2023&start=2019&end=2025",
    "/api/power-plants",
    "/api/power-plants/stats",
    "/api/power-plants?type=solar",
    "/api/power-plants?type=coal&min_capacity=500",
    "/api/analytics/meta",
    "/api/analytics/correlation?year=2024",
    "/api/analytics/compare?states=maharashtra,gujarat&year=2024",
    "/api/insights/state?state_id=rajasthan",
    "/api/generation/live",
    "/api/market/pricing/live",
    "/api/meta/years",
    "/",
]

CONCURRENCY_LEVELS = [50, 100, 250, 500, 1000]

# ─── STRESS TEST ──────────────────────────────────────────

async def hit(session, url, results_list):
    t0 = time.perf_counter()
    status = 0
    error = None
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as resp:
            status = resp.status
            await resp.read()
    except aiohttp.ClientConnectorError:
        error = "ConnectError"
    except asyncio.TimeoutError:
        error = "Timeout"
    except Exception as e:
        error = type(e).__name__
    elapsed = time.perf_counter() - t0
    results_list.append({"url": url, "status": status, "elapsed": elapsed, "error": error})


async def run_stress_level(concurrency: int):
    """Fire `concurrency` requests across all endpoints simultaneously."""
    results = []
    connector = aiohttp.TCPConnector(limit=concurrency, force_close=True)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for i in range(concurrency):
            url = f"{BASE}{ENDPOINTS[i % len(ENDPOINTS)]}"
            tasks.append(hit(session, url, results))
        await asyncio.gather(*tasks, return_exceptions=True)
    return results


async def stress_test():
    print("=" * 60)
    print("  STRESS TEST — India Energy Atlas")
    print("=" * 60)
    all_results = {}
    for c in CONCURRENCY_LEVELS:
        print(f"\n→ Concurrency {c} ...", end=" ", flush=True)
        res = await run_stress_level(c)
        times = [r["elapsed"] for r in res if r["error"] is None]
        errors = [r for r in res if r["error"] is not None]
        http_errors = [r for r in res if r["status"] >= 400 and r["error"] is None]
        summary = {
            "concurrency": c,
            "total_requests": len(res),
            "successful": len(times),
            "errors": len(errors),
            "http_errors": len(http_errors),
            "error_types": {},
        }
        for e in errors:
            t = e["error"]
            summary["error_types"][t] = summary["error_types"].get(t, 0) + 1
        if times:
            times.sort()
            summary["rps"] = round(len(times) / max(sum(times) / len(times), 0.001), 2)
            summary["min_s"] = round(min(times), 4)
            summary["max_s"] = round(max(times), 4)
            summary["mean_s"] = round(statistics.mean(times), 4)
            summary["median_s"] = round(statistics.median(times), 4)
            summary["p95_s"] = round(times[int(len(times) * 0.95)], 4)
            summary["p99_s"] = round(times[int(len(times) * 0.99)], 4) if len(times) > 1 else summary["max_s"]
        else:
            summary["rps"] = 0
        all_results[str(c)] = summary
        print(f"OK  RPS={summary.get('rps',0)}  errors={summary['errors']}  http_err={summary['http_errors']}")

    # Write JSON
    (OUT / "stress_results.json").write_text(json.dumps(all_results, indent=2))
    print(f"\n✓ stress_results.json saved")

    # Write Markdown report
    write_stress_report(all_results)
    return all_results


def write_stress_report(results):
    lines = [
        "# India Energy Atlas — Stress Test Report",
        f"\n**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Base URL:** {BASE}",
        f"**Endpoints tested:** {len(ENDPOINTS)}",
        f"**Concurrency levels:** {CONCURRENCY_LEVELS}\n",
        "## Summary Table\n",
        "| Concurrency | RPS | Mean (s) | Median (s) | P95 (s) | P99 (s) | Max (s) | Errors | HTTP 4xx/5xx |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for k, v in results.items():
        lines.append(
            f"| {v['concurrency']} | {v.get('rps',0)} | {v.get('mean_s','—')} | "
            f"{v.get('median_s','—')} | {v.get('p95_s','—')} | {v.get('p99_s','—')} | "
            f"{v.get('max_s','—')} | {v['errors']} | {v['http_errors']} |"
        )

    # Determine breaking point
    for k, v in results.items():
        if v["errors"] > 0 or v.get("p95_s", 0) > 5:
            lines.append(f"\n> [!WARNING]\n> Breaking behavior observed at **{v['concurrency']} concurrent users** "
                         f"(P95={v.get('p95_s','—')}s, errors={v['errors']}).")
            break

    lines.append("\n## Error Breakdown\n")
    for k, v in results.items():
        if v["error_types"]:
            lines.append(f"**Concurrency {v['concurrency']}:** {v['error_types']}")

    lines.append("\n## Observations\n")
    peak_rps = max((v.get("rps", 0), v["concurrency"]) for v in results.values())
    lines.append(f"- Peak throughput: **{peak_rps[0]} RPS** at concurrency {peak_rps[1]}")
    lines.append(f"- `/api/generation/live` and `/api/market/pricing/live` produce randomized simulation data.")
    lines.append(f"- Tested {len(ENDPOINTS)} endpoints covering states, power plants, analytics, generation, and market.")

    (OUT / "stress_report.md").write_text("\n".join(lines), encoding="utf-8")
    print("✓ stress_report.md saved")


# ─── DATA EXTRACTION ─────────────────────────────────────

async def fetch_json(session, path):
    try:
        async with session.get(f"{BASE}{path}", timeout=aiohttp.ClientTimeout(total=30)) as r:
            if r.status == 200:
                return await r.json()
            return {"_error": r.status, "_path": path}
    except Exception as e:
        return {"_error": str(e), "_path": path}


async def extract_all_data():
    print("\n" + "=" * 60)
    print("  DATA EXTRACTION")
    print("=" * 60)

    dump = {}
    async with aiohttp.ClientSession() as session:
        # States list
        states = await fetch_json(session, "/api/states")
        dump["states"] = states
        print(f"  States: {len(states) if isinstance(states, list) else '?'}")

        # Years metadata
        years_meta = await fetch_json(session, "/api/meta/years")
        dump["years_meta"] = years_meta
        min_yr = years_meta.get("min_year", 2019)
        max_yr = years_meta.get("max_year", 2026)

        # Per-state per-year detail
        state_details = []
        if isinstance(states, list):
            for st in states:
                sid = st["id"]
                for yr in range(min_yr, max_yr + 1):
                    d = await fetch_json(session, f"/api/states/{sid}?year={yr}")
                    d["_query_year"] = yr
                    d["_state_id"] = sid
                    state_details.append(d)
            print(f"  State-year details: {len(state_details)}")
        dump["state_details"] = state_details

        # Power plants
        pp = await fetch_json(session, "/api/power-plants")
        pp_features = pp.get("features", []) if isinstance(pp, dict) else []
        dump["power_plants_count"] = len(pp_features)
        dump["power_plants_features"] = pp_features
        print(f"  Power plants: {len(pp_features)}")

        pp_stats = await fetch_json(session, "/api/power-plants/stats")
        dump["power_plants_stats"] = pp_stats

        # Analytics
        analytics_meta = await fetch_json(session, "/api/analytics/meta")
        dump["analytics_meta"] = analytics_meta

        correlations = []
        for yr in range(min_yr, max_yr + 1):
            c = await fetch_json(session, f"/api/analytics/correlation?year={yr}")
            c["_query_year"] = yr
            correlations.append(c)
        dump["analytics_correlations"] = correlations
        print(f"  Correlation queries: {len(correlations)}")

        # Comparison (pick first 3 states for a sample)
        if isinstance(states, list) and len(states) >= 3:
            sample_ids = [s["id"] for s in states[:3]]
            comparison = await fetch_json(session, f"/api/analytics/compare?states={','.join(sample_ids)}&year={max_yr}")
            dump["analytics_comparison_sample"] = comparison

        # Live endpoints
        dump["live_generation"] = await fetch_json(session, "/api/generation/live")
        dump["live_market"] = await fetch_json(session, "/api/market/pricing/live")

        # Insights sample
        if isinstance(states, list) and len(states) > 0:
            dump["insights_sample"] = await fetch_json(session, f"/api/insights/state?state_id={states[0]['id']}")

    # Write full dump
    (OUT / "local_site_data_dump.json").write_text(json.dumps(dump, indent=2, default=str), encoding="utf-8")
    print("✓ local_site_data_dump.json saved")

    # ── CSV exports ──
    # 1. state_year_matrix.csv
    with open(OUT / "state_year_matrix.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["state_id", "state_name", "year", "total_capacity_mw",
                     "solar", "wind", "hydro", "nuclear", "bioenergy", "generation_gwh"])
        for d in state_details:
            if "_error" in d:
                continue
            cap = d.get("capacity", {})
            bk = cap.get("breakdown", {})
            gen = d.get("generation", {})
            w.writerow([
                d.get("id", d.get("_state_id", "")),
                d.get("name", ""),
                d.get("_query_year", ""),
                cap.get("total_mw", ""),
                bk.get("solar", ""), bk.get("wind", ""), bk.get("hydro", ""),
                bk.get("nuclear", ""), bk.get("bioenergy", ""),
                gen.get("total_gwh", ""),
            ])
    print("✓ state_year_matrix.csv saved")

    # 2. power_plants_all.csv
    with open(OUT / "power_plants_all.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["name", "type", "capacity_mw", "operator", "state", "osm_id", "lng", "lat"])
        for feat in pp_features:
            props = feat.get("properties", {})
            coords = feat.get("geometry", {}).get("coordinates", [None, None])
            w.writerow([
                props.get("name", ""),
                props.get("type", ""),
                props.get("capacity_mw", ""),
                props.get("operator", ""),
                props.get("state", ""),
                props.get("osm_id", ""),
                coords[0] if coords else "",
                coords[1] if len(coords) > 1 else "",
            ])
    print("✓ power_plants_all.csv saved")

    # 3. analytics_correlation_by_year.csv
    with open(OUT / "analytics_correlation_by_year.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["year", "status", "top_state", "correlation_count"])
        for c in correlations:
            yr = c.get("_query_year", "")
            if "_error" in c:
                w.writerow([yr, f"error_{c['_error']}", "", ""])
            else:
                rankings = c.get("state_rankings", [])
                top = rankings[0]["state_name"] if rankings else ""
                w.writerow([yr, "ok", top, len(rankings)])
    print("✓ analytics_correlation_by_year.csv saved")

    return dump


# ─── DATA PARITY AUDIT ──────────────────────────────────

async def data_parity_audit(dump):
    print("\n" + "=" * 60)
    print("  DATA PARITY AUDIT")
    print("=" * 60)

    audit = {
        "timestamp": datetime.now().isoformat(),
        "local_stats": {},
        "live_checks": {},
        "observations": [],
    }

    # Local stats
    states = dump.get("states", [])
    state_details = dump.get("state_details", [])
    pp_count = dump.get("power_plants_count", 0)

    audit["local_stats"]["state_count"] = len(states) if isinstance(states, list) else 0
    audit["local_stats"]["state_year_points"] = len(state_details)
    audit["local_stats"]["power_plant_count"] = pp_count

    # Check for correlation 400 errors
    corr_errors = [c for c in dump.get("analytics_correlations", []) if "_error" in c]
    audit["local_stats"]["correlation_errors"] = [
        {"year": c["_query_year"], "error": c["_error"]} for c in corr_errors
    ]
    if corr_errors:
        audit["observations"].append(
            f"Analytics correlation returned errors for years: "
            f"{[c['_query_year'] for c in corr_errors]}. Backend may not support those years."
        )

    # Live generation / market check
    live_gen = dump.get("live_generation", {})
    live_mkt = dump.get("live_market", {})
    audit["live_checks"]["generation_timestamp"] = live_gen.get("timestamp", "N/A")
    audit["live_checks"]["market_timestamp"] = live_mkt.get("timestamp", "N/A")
    audit["live_checks"]["generation_national_mw"] = live_gen.get("national_total_mw", 0)
    audit["live_checks"]["generation_states_count"] = len(live_gen.get("states", {}))

    if live_gen.get("timestamp") == "Live":
        audit["observations"].append(
            "/api/generation/live uses a fixed 'Live' timestamp — this is simulation-style output."
        )

    # Wikipedia parity check (attempt)
    wiki_parity = []
    try:
        async with aiohttp.ClientSession() as session:
            # Use a simple heuristic — compare our total capacity with known approximate values
            # We'll check a few major states against commonly known figures
            known_approx = {
                "rajasthan": {"wiki_approx_gw": 30, "source": "Wikipedia ~2024-25"},
                "gujarat": {"wiki_approx_gw": 25, "source": "Wikipedia ~2024-25"},
                "tamil_nadu": {"wiki_approx_gw": 20, "source": "Wikipedia ~2024-25"},
                "karnataka": {"wiki_approx_gw": 18, "source": "Wikipedia ~2024-25"},
                "maharashtra": {"wiki_approx_gw": 25, "source": "Wikipedia ~2024-25"},
                "andhra_pradesh": {"wiki_approx_gw": 16, "source": "Wikipedia ~2024-25"},
                "madhya_pradesh": {"wiki_approx_gw": 15, "source": "Wikipedia ~2024-25"},
                "uttar_pradesh": {"wiki_approx_gw": 15, "source": "Wikipedia ~2024-25"},
                "telangana": {"wiki_approx_gw": 12, "source": "Wikipedia ~2024-25"},
            }
            for d in state_details:
                sid = d.get("_state_id", d.get("id", ""))
                yr = d.get("_query_year", 0)
                if yr == 2025 and sid in known_approx:
                    local_mw = d.get("capacity", {}).get("total_mw", 0)
                    local_gw = round(local_mw / 1000, 2)
                    wiki_gw = known_approx[sid]["wiki_approx_gw"]
                    gap_pct = round(abs(local_gw - wiki_gw) / max(wiki_gw, 1) * 100, 2)
                    wiki_parity.append({
                        "state": sid,
                        "local_gw": local_gw,
                        "wiki_approx_gw": wiki_gw,
                        "gap_pct": gap_pct,
                    })
    except Exception as e:
        audit["observations"].append(f"Wikipedia parity check error: {e}")

    audit["live_checks"]["wiki_parity_states"] = len(wiki_parity)
    audit["live_checks"]["wiki_parity"] = wiki_parity
    if wiki_parity:
        mean_gap = round(statistics.mean([p["gap_pct"] for p in wiki_parity]), 2)
        high_gap = [p for p in wiki_parity if p["gap_pct"] > 10]
        audit["live_checks"]["wiki_mean_gap_pct"] = mean_gap
        audit["live_checks"]["wiki_high_gap_states"] = len(high_gap)
        audit["observations"].append(
            f"Capacity vs Wikipedia approx: {len(wiki_parity)} states checked, "
            f"mean abs gap {mean_gap}%, {len(high_gap)} states above 10% gap."
        )

    # Power plant count vs known
    audit["live_checks"]["local_plant_count"] = pp_count
    audit["observations"].append(f"Local power plant count: {pp_count}")

    # Freshness
    audit["observations"].append(
        f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}. "
        f"Data freshness depends on last scraper run."
    )

    # Write JSON
    (OUT / "data_parity_audit.json").write_text(json.dumps(audit, indent=2, default=str), encoding="utf-8")
    print("✓ data_parity_audit.json saved")

    # Write MD
    write_parity_md(audit, wiki_parity)
    return audit


def write_parity_md(audit, wiki_parity):
    lines = [
        "# India Energy Atlas — Data Parity Audit",
        f"\n**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Base URL:** {BASE}\n",
        "## Local Data Summary\n",
        f"| Metric | Value |",
        f"|---|---|",
        f"| States | {audit['local_stats']['state_count']} |",
        f"| State-year data points | {audit['local_stats']['state_year_points']} |",
        f"| Power plants | {audit['local_stats']['power_plant_count']} |",
        f"| Correlation errors | {len(audit['local_stats']['correlation_errors'])} |",
        "",
    ]

    if audit["local_stats"]["correlation_errors"]:
        lines.append("### Correlation Year Errors\n")
        for e in audit["local_stats"]["correlation_errors"]:
            lines.append(f"- Year **{e['year']}**: HTTP {e['error']}")
        lines.append("")

    lines.append("## Live Endpoint Checks\n")
    lines.append(f"| Endpoint | Status |")
    lines.append(f"|---|---|")
    lines.append(f"| /api/generation/live | timestamp=`{audit['live_checks']['generation_timestamp']}`, "
                 f"national={audit['live_checks']['generation_national_mw']} MW |")
    lines.append(f"| /api/market/pricing/live | timestamp=`{audit['live_checks']['market_timestamp']}` |")
    lines.append("")

    if wiki_parity:
        lines.append("## Wikipedia Capacity Parity (2025 snapshot)\n")
        lines.append("| State | Local (GW) | Wiki Approx (GW) | Gap (%) |")
        lines.append("|---|---|---|---|")
        for p in sorted(wiki_parity, key=lambda x: -x["gap_pct"]):
            flag = " ⚠️" if p["gap_pct"] > 10 else ""
            lines.append(f"| {p['state']} | {p['local_gw']} | {p['wiki_approx_gw']} | {p['gap_pct']}%{flag} |")
        lines.append(f"\n**Mean gap:** {audit['live_checks'].get('wiki_mean_gap_pct', '—')}%")
        lines.append(f"**States above 10% gap:** {audit['live_checks'].get('wiki_high_gap_states', 0)}")
        lines.append("")

    lines.append("## Observations\n")
    for obs in audit.get("observations", []):
        lines.append(f"- {obs}")

    (OUT / "data_parity_audit.md").write_text("\n".join(lines), encoding="utf-8")
    print("✓ data_parity_audit.md saved")


# ─── MAIN ─────────────────────────────────────────────────

async def main():
    t0 = time.time()

    # 1. Stress test
    stress_results = await stress_test()

    # 2. Data extraction
    dump = await extract_all_data()

    # 3. Parity audit
    audit = await data_parity_audit(dump)

    elapsed = round(time.time() - t0, 1)
    print(f"\n{'=' * 60}")
    print(f"  ALL DONE in {elapsed}s")
    print(f"  Output directory: {OUT}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(main())

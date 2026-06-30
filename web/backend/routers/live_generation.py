"""Live generation router — simulated near-real-time generation by state."""

import random
from datetime import datetime, timezone

from fastapi import APIRouter
from services.mock_data import STATES_DATA

router = APIRouter()


@router.get("/live")
def get_live_generation():
    """
    Returns simulated near-real-time generation data for all tracked states.

    In a production pipeline this would read from a Grid-India daily report
    payload written by the IexExtractor / GridIndiaExtractor scrapers.
    Generation is simulated based on 2026 installed capacity with realistic
    utilisation factors per source type.
    """
    live_data: dict = {}
    total_national_live = 0

    for state_id, state_info in STATES_DATA.items():
        cap_2026 = sum(state_info.get("capacity_by_year", {}).get(2026, {}).values())

        if cap_2026 == 0:
            continue

        # Simulate current utilisation factor (40–85% of total capacity)
        utilisation = random.uniform(0.40, 0.85)
        current_gen_mw = int(cap_2026 * utilisation)
        total_national_live += current_gen_mw

        breakdown = state_info["capacity_by_year"][2026]
        gen_mix: dict[str, int] = {}
        for source, mw in breakdown.items():
            if mw <= 0:
                continue
            # Source-specific utilisation factors reflecting real-world patterns
            if source == "solar":
                source_util = random.uniform(0.10, 0.90)  # daytime only
            elif source == "wind":
                source_util = random.uniform(0.20, 0.70)  # variable
            else:
                source_util = random.uniform(0.60, 0.95)  # steady baseline

            val = int(mw * source_util)
            if val > 0:
                gen_mix[source] = val

        # Normalise so individual source MWs sum to the state's simulated total
        mix_sum = sum(gen_mix.values())
        if mix_sum > 0:
            gen_mix = {k: int((v / mix_sum) * current_gen_mw) for k, v in gen_mix.items()}

        live_data[state_id] = {
            "state_id": state_id,
            "state_name": state_info["name"],
            "current_generation_mw": current_gen_mw,
            "utilisation_pct": round(utilisation * 100, 1),
            "mix": gen_mix,
        }

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "national_total_mw": total_national_live,
        "states": live_data,
    }

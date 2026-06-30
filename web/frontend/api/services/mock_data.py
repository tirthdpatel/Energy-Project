"""Time-series energy data for all Indian states & UTs.

Data shaped as if ingested from MNRE / CEA sources:
- capacity_by_year: {year → {solar, wind, hydro, nuclear, bioenergy}} in MW
- generation_by_year: {year → total_gwh}
"""

from __future__ import annotations
import json
import os
from pathlib import Path

# Available year range
MIN_YEAR = 2019
MAX_YEAR = 2026

STATES_DATA: dict[str, dict] = {
    # ── Major States ──────────────────────────────
    "maharashtra": {
        "id": "maharashtra",
        "name": "Maharashtra",
        "code": "IN-MH",
        "capacity_by_year": {
            2019: {"solar": 3200, "wind": 5100, "hydro": 3800, "nuclear": 1840, "bioenergy": 2800},
            2020: {"solar": 4200, "wind": 5400, "hydro": 3900, "nuclear": 1840, "bioenergy": 2900},
            2021: {"solar": 5500, "wind": 5700, "hydro": 4000, "nuclear": 2000, "bioenergy": 3000},
            2022: {"solar": 7000, "wind": 6000, "hydro": 4100, "nuclear": 2000, "bioenergy": 3100},
            2023: {"solar": 8400, "wind": 6300, "hydro": 4200, "nuclear": 2200, "bioenergy": 3200},
            2024: {"solar": 9800, "wind": 6600, "hydro": 4300, "nuclear": 2400, "bioenergy": 3300}, 
            2025: {"solar": 10290, "wind": 6930, "hydro": 4515, "nuclear": 2520, "bioenergy": 3465},
            2026: {'solar': 21872, 'wind': 14729, 'hydro': 9595, 'nuclear': 5356, 'bioenergy': 7364},
        },
        "generation_by_year": {
            2019: 112_000, 2020: 118_000, 2021: 123_500, 2022: 129_800, 2023: 136_100, 2024: 142_300, 2025: 149_415, 2026: 156_530
        },
    },
    "gujarat": {
        "id": "gujarat",
        "name": "Gujarat",
        "code": "IN-GJ",
        "capacity_by_year": {
            2019: {"solar": 3800, "wind": 6200, "hydro": 800, "nuclear": 880, "bioenergy": 1100},
            2020: {"solar": 5200, "wind": 6800, "hydro": 850, "nuclear": 880, "bioenergy": 1200},
            2021: {"solar": 7000, "wind": 7400, "hydro": 900, "nuclear": 880, "bioenergy": 1300},
            2022: {"solar": 8800, "wind": 7900, "hydro": 950, "nuclear": 880, "bioenergy": 1400},
            2023: {"solar": 10200, "wind": 8400, "hydro": 1000, "nuclear": 1200, "bioenergy": 1500},
            2024: {"solar": 12000, "wind": 9000, "hydro": 1050, "nuclear": 1200, "bioenergy": 1600}, 
            2025: {"solar": 12600, "wind": 9450, "hydro": 1102, "nuclear": 1260, "bioenergy": 1680},
            2026: {'solar': 33085, 'wind': 24812, 'hydro': 2893, 'nuclear': 3308, 'bioenergy': 4411},
        },
        "generation_by_year": {
            2019: 95_000, 2020: 102_000, 2021: 108_400, 2022: 115_200, 2023: 122_000, 2024: 128_500, 2025: 134_925, 2026: 141_350
        },
    },
    "tamil_nadu": {
        "id": "tamil_nadu",
        "name": "Tamil Nadu",
        "code": "IN-TN",
        "capacity_by_year": {
            2019: {"solar": 2800, "wind": 9200, "hydro": 2200, "nuclear": 1540, "bioenergy": 1000},
            2020: {"solar": 3600, "wind": 9600, "hydro": 2300, "nuclear": 1540, "bioenergy": 1100},
            2021: {"solar": 4800, "wind": 10000, "hydro": 2400, "nuclear": 1540, "bioenergy": 1200},
            2022: {"solar": 6000, "wind": 10500, "hydro": 2500, "nuclear": 1800, "bioenergy": 1300},
            2023: {"solar": 7200, "wind": 11000, "hydro": 2600, "nuclear": 1800, "bioenergy": 1400},
            2024: {"solar": 8500, "wind": 11500, "hydro": 2700, "nuclear": 1800, "bioenergy": 1500}, 
            2025: {"solar": 8925, "wind": 12075, "hydro": 2835, "nuclear": 1890, "bioenergy": 1575},
            2026: {'solar': 14942, 'wind': 20213, 'hydro': 4744, 'nuclear': 3163, 'bioenergy': 2635},
        },
        "generation_by_year": {
            2019: 85_000, 2020: 91_000, 2021: 95_800, 2022: 101_300, 2023: 107_000, 2024: 112_400, 2025: 118_020, 2026: 123_640
        },
    },
    "rajasthan": {
        "id": "rajasthan",
        "name": "Rajasthan",
        "code": "IN-RJ",
        "capacity_by_year": {
            2019: {"solar": 4200, "wind": 4300, "hydro": 1800, "nuclear": 1180, "bioenergy": 400},
            2020: {"solar": 5800, "wind": 4600, "hydro": 1850, "nuclear": 1180, "bioenergy": 450},
            2021: {"solar": 7500, "wind": 5000, "hydro": 1900, "nuclear": 1180, "bioenergy": 500},
            2022: {"solar": 9200, "wind": 5400, "hydro": 1950, "nuclear": 1180, "bioenergy": 550},
            2023: {"solar": 11000, "wind": 5800, "hydro": 2000, "nuclear": 1300, "bioenergy": 600},
            2024: {"solar": 13000, "wind": 6200, "hydro": 2050, "nuclear": 1300, "bioenergy": 650}, 
            2025: {"solar": 13650, "wind": 6510, "hydro": 2152, "nuclear": 1365, "bioenergy": 682},
            2026: {'solar': 32182, 'wind': 15346, 'hydro': 5072, 'nuclear': 3217, 'bioenergy': 1607},
        },
        "generation_by_year": {
            2019: 72_000, 2020: 78_000, 2021: 83_200, 2022: 88_500, 2023: 93_800, 2024: 98_600, 2025: 103_530, 2026: 108_460
        },
    },
    "karnataka": {
        "id": "karnataka",
        "name": "Karnataka",
        "code": "IN-KA",
        "capacity_by_year": {
            2019: {"solar": 3000, "wind": 4800, "hydro": 4200, "nuclear": 880, "bioenergy": 1900},
            2020: {"solar": 4200, "wind": 5000, "hydro": 4400, "nuclear": 880, "bioenergy": 2000},
            2021: {"solar": 5400, "wind": 5200, "hydro": 4600, "nuclear": 880, "bioenergy": 2100},
            2022: {"solar": 7200, "wind": 5500, "hydro": 4800, "nuclear": 1300, "bioenergy": 2200},
            2023: {"solar": 8800, "wind": 5800, "hydro": 5000, "nuclear": 1300, "bioenergy": 2300},
            2024: {"solar": 10000, "wind": 6100, "hydro": 5200, "nuclear": 1300, "bioenergy": 2400}, 
            2025: {"solar": 10500, "wind": 6405, "hydro": 5460, "nuclear": 1365, "bioenergy": 2520},
            2026: {'solar': 14759, 'wind': 9001, 'hydro': 7674, 'nuclear': 1918, 'bioenergy': 3541},
        },
        "generation_by_year": {
            2019: 68_000, 2020: 74_500, 2021: 78_900, 2022: 83_600, 2023: 88_000, 2024: 92_100, 2025: 96_705, 2026: 101_310
        },
    },
    "uttar_pradesh": {
        "id": "uttar_pradesh",
        "name": "Uttar Pradesh",
        "code": "IN-UP",
        "capacity_by_year": {
            2019: {"solar": 1800, "wind": 500, "hydro": 3200, "nuclear": 400, "bioenergy": 2800},
            2020: {"solar": 2800, "wind": 600, "hydro": 3300, "nuclear": 400, "bioenergy": 2900},
            2021: {"solar": 4000, "wind": 700, "hydro": 3400, "nuclear": 800, "bioenergy": 3000},
            2022: {"solar": 5500, "wind": 800, "hydro": 3500, "nuclear": 800, "bioenergy": 3100},
            2023: {"solar": 7000, "wind": 900, "hydro": 3600, "nuclear": 800, "bioenergy": 3200},
            2024: {"solar": 8500, "wind": 1000, "hydro": 3700, "nuclear": 1200, "bioenergy": 3300}, 
            2025: {"solar": 8925, "wind": 1050, "hydro": 3885, "nuclear": 1260, "bioenergy": 3465},
            2026: {'solar': 18558, 'wind': 2182, 'hydro': 8077, 'nuclear': 2619, 'bioenergy': 7204},
        },
        "generation_by_year": {
            2019: 66_000, 2020: 72_000, 2021: 76_200, 2022: 80_100, 2023: 84_500, 2024: 88_700, 2025: 93_135, 2026: 97_570
        },
    },
    "andhra_pradesh": {
        "id": "andhra_pradesh",
        "name": "Andhra Pradesh",
        "code": "IN-AP",
        "capacity_by_year": {
            2019: {"solar": 3000, "wind": 4000, "hydro": 2000, "nuclear": 800, "bioenergy": 300},
            2020: {"solar": 4200, "wind": 4200, "hydro": 2100, "nuclear": 800, "bioenergy": 350},
            2021: {"solar": 5500, "wind": 4500, "hydro": 2200, "nuclear": 800, "bioenergy": 400},
            2022: {"solar": 7000, "wind": 4800, "hydro": 2300, "nuclear": 1000, "bioenergy": 450},
            2023: {"solar": 8200, "wind": 5100, "hydro": 2400, "nuclear": 1000, "bioenergy": 500},
            2024: {"solar": 9500, "wind": 5400, "hydro": 2500, "nuclear": 1000, "bioenergy": 550}, 
            2025: {"solar": 9975, "wind": 5670, "hydro": 2625, "nuclear": 1050, "bioenergy": 577},
            2026: {'solar': 15577, 'wind': 8853, 'hydro': 4098, 'nuclear': 1638, 'bioenergy': 899},
        },
        "generation_by_year": {
            2019: 60_000, 2020: 65_000, 2021: 69_500, 2022: 73_800, 2023: 77_600, 2024: 81_200, 2025: 85_260, 2026: 89_320
        },
    },
    "madhya_pradesh": {
        "id": "madhya_pradesh",
        "name": "Madhya Pradesh",
        "code": "IN-MP",
        "capacity_by_year": {
            2019: {"solar": 2500, "wind": 2600, "hydro": 2200, "nuclear": 500, "bioenergy": 600},
            2020: {"solar": 3800, "wind": 2800, "hydro": 2300, "nuclear": 500, "bioenergy": 650},
            2021: {"solar": 5200, "wind": 3000, "hydro": 2400, "nuclear": 500, "bioenergy": 700},
            2022: {"solar": 6500, "wind": 3200, "hydro": 2500, "nuclear": 500, "bioenergy": 750},
            2023: {"solar": 8000, "wind": 3400, "hydro": 2600, "nuclear": 700, "bioenergy": 800},
            2024: {"solar": 9500, "wind": 3600, "hydro": 2700, "nuclear": 700, "bioenergy": 850}, 
            2025: {"solar": 9975, "wind": 3780, "hydro": 2835, "nuclear": 735, "bioenergy": 892},
            2026: {'solar': 18144, 'wind': 6875, 'hydro': 5155, 'nuclear': 1335, 'bioenergy': 1621},
        },
        "generation_by_year": {
            2019: 55_000, 2020: 60_000, 2021: 63_800, 2022: 67_500, 2023: 71_000, 2024: 74_500, 2025: 78_225, 2026: 81_950
        },
    },
    "telangana": {
        "id": "telangana",
        "name": "Telangana",
        "code": "IN-TG",
        "capacity_by_year": {
            2019: {"solar": 1800, "wind": 200, "hydro": 2800, "nuclear": 600, "bioenergy": 500},
            2020: {"solar": 2800, "wind": 300, "hydro": 2900, "nuclear": 600, "bioenergy": 550},
            2021: {"solar": 3800, "wind": 400, "hydro": 3000, "nuclear": 600, "bioenergy": 600},
            2022: {"solar": 4800, "wind": 500, "hydro": 3100, "nuclear": 800, "bioenergy": 650},
            2023: {"solar": 5800, "wind": 600, "hydro": 3200, "nuclear": 800, "bioenergy": 700},
            2024: {"solar": 6800, "wind": 700, "hydro": 3300, "nuclear": 800, "bioenergy": 750}, 
            2025: {"solar": 7140, "wind": 735, "hydro": 3465, "nuclear": 840, "bioenergy": 787},
            2026: {'solar': 10879, 'wind': 1118, 'hydro': 5278, 'nuclear': 1279, 'bioenergy': 1198},
        },
        "generation_by_year": {
            2019: 45_000, 2020: 50_000, 2021: 53_600, 2022: 56_800, 2023: 59_700, 2024: 62_400, 2025: 65_520, 2026: 68_640
        },
    },
    "punjab": {
        "id": "punjab",
        "name": "Punjab",
        "code": "IN-PB",
        "capacity_by_year": {
            2019: {"solar": 900, "wind": 100, "hydro": 3600, "nuclear": 500, "bioenergy": 600},
            2020: {"solar": 1400, "wind": 150, "hydro": 3700, "nuclear": 500, "bioenergy": 650},
            2021: {"solar": 2000, "wind": 200, "hydro": 3800, "nuclear": 500, "bioenergy": 700},
            2022: {"solar": 2600, "wind": 250, "hydro": 3900, "nuclear": 600, "bioenergy": 750},
            2023: {"solar": 3200, "wind": 300, "hydro": 4000, "nuclear": 600, "bioenergy": 800},
            2024: {"solar": 3800, "wind": 350, "hydro": 4100, "nuclear": 600, "bioenergy": 850}, 
            2025: {"solar": 3990, "wind": 367, "hydro": 4305, "nuclear": 630, "bioenergy": 892},
            2026: {'solar': 3562, 'wind': 327, 'hydro': 3843, 'nuclear': 562, 'bioenergy': 795},
        },
        "generation_by_year": {
            2019: 36_000, 2020: 40_000, 2021: 42_300, 2022: 44_800, 2023: 47_000, 2024: 48_900, 2025: 51_345, 2026: 53_790
        },
    },
    "west_bengal": {
        "id": "west_bengal",
        "name": "West Bengal",
        "code": "IN-WB",
        "capacity_by_year": {
            2019: {"solar": 200, "wind": 50, "hydro": 1300, "nuclear": 500, "bioenergy": 400},
            2020: {"solar": 400, "wind": 80, "hydro": 1400, "nuclear": 500, "bioenergy": 450},
            2021: {"solar": 800, "wind": 100, "hydro": 1500, "nuclear": 800, "bioenergy": 500},
            2022: {"solar": 1400, "wind": 120, "hydro": 1600, "nuclear": 800, "bioenergy": 550},
            2023: {"solar": 2000, "wind": 150, "hydro": 1700, "nuclear": 800, "bioenergy": 600},
            2024: {"solar": 2600, "wind": 180, "hydro": 1800, "nuclear": 1000, "bioenergy": 650}, 
            2025: {"solar": 2730, "wind": 189, "hydro": 1890, "nuclear": 1050, "bioenergy": 682},
            2026: {'solar': 6408, 'wind': 442, 'hydro': 4434, 'nuclear': 2463, 'bioenergy': 1600},
        },
        "generation_by_year": {
            2019: 38_000, 2020: 43_000, 2021: 45_200, 2022: 47_800, 2023: 50_100, 2024: 52_300, 2025: 54_915, 2026: 57_530
        },
    },
    "kerala": {
        "id": "kerala",
        "name": "Kerala",
        "code": "IN-KL",
        "capacity_by_year": {
            2019: {"solar": 300, "wind": 100, "hydro": 2100, "nuclear": 60, "bioenergy": 100},
            2020: {"solar": 500, "wind": 120, "hydro": 2200, "nuclear": 60, "bioenergy": 120},
            2021: {"solar": 800, "wind": 140, "hydro": 2300, "nuclear": 60, "bioenergy": 140},
            2022: {"solar": 1100, "wind": 160, "hydro": 2400, "nuclear": 60, "bioenergy": 160},
            2023: {"solar": 1400, "wind": 180, "hydro": 2500, "nuclear": 100, "bioenergy": 180},
            2024: {"solar": 1700, "wind": 200, "hydro": 2600, "nuclear": 100, "bioenergy": 200}, 
            2025: {"solar": 1785, "wind": 210, "hydro": 2730, "nuclear": 105, "bioenergy": 210},
            2026: {'solar': 1757, 'wind': 206, 'hydro': 2686, 'nuclear': 103, 'bioenergy': 206},
        },
        "generation_by_year": {
            2019: 16_000, 2020: 18_000, 2021: 19_100, 2022: 20_000, 2023: 21_100, 2024: 22_100, 2025: 23_205, 2026: 24_310
        },
    },
    # ── Additional States ────────────────────────
    "chhattisgarh": {
        "id": "chhattisgarh", "name": "Chhattisgarh", "code": "IN-CT",
        "capacity_by_year": {
            2019: {"solar": 500, "wind": 50, "hydro": 1200, "nuclear": 0, "bioenergy": 300},
            2020: {"solar": 800, "wind": 60, "hydro": 1300, "nuclear": 0, "bioenergy": 350},
            2021: {"solar": 1200, "wind": 70, "hydro": 1400, "nuclear": 0, "bioenergy": 400},
            2022: {"solar": 1800, "wind": 80, "hydro": 1500, "nuclear": 0, "bioenergy": 450},
            2023: {"solar": 2400, "wind": 90, "hydro": 1600, "nuclear": 0, "bioenergy": 500},
            2024: {"solar": 3000, "wind": 100, "hydro": 1700, "nuclear": 100, "bioenergy": 550}, 
            2025: {"solar": 3150, "wind": 105, "hydro": 1785, "nuclear": 105, "bioenergy": 577},
            2026: {'solar': 14513, 'wind': 482, 'hydro': 8223, 'nuclear': 482, 'bioenergy': 2654},
        },
        "generation_by_year": {2019: 34_000, 2020: 38_000, 2021: 40_000, 2022: 42_000, 2023: 44_000, 2024: 45_800, 2025: 48_090, 2026: 50_380},
    },
    "haryana": {
        "id": "haryana", "name": "Haryana", "code": "IN-HR",
        "capacity_by_year": {
            2019: {"solar": 600, "wind": 200, "hydro": 200, "nuclear": 300, "bioenergy": 500},
            2020: {"solar": 1200, "wind": 300, "hydro": 220, "nuclear": 300, "bioenergy": 550},
            2021: {"solar": 2000, "wind": 400, "hydro": 240, "nuclear": 500, "bioenergy": 600},
            2022: {"solar": 3000, "wind": 500, "hydro": 260, "nuclear": 500, "bioenergy": 650},
            2023: {"solar": 4000, "wind": 600, "hydro": 280, "nuclear": 500, "bioenergy": 700},
            2024: {"solar": 5000, "wind": 700, "hydro": 300, "nuclear": 700, "bioenergy": 750}, 
            2025: {"solar": 5250, "wind": 735, "hydro": 315, "nuclear": 735, "bioenergy": 787},
            2026: {'solar': 5842, 'wind': 817, 'hydro': 349, 'nuclear': 817, 'bioenergy': 875},
        },
        "generation_by_year": {2019: 30_000, 2020: 34_000, 2021: 36_000, 2022: 38_000, 2023: 40_000, 2024: 41_500, 2025: 43_575, 2026: 45_650},
    },
    "jharkhand": {
        "id": "jharkhand", "name": "Jharkhand", "code": "IN-JH",
        "capacity_by_year": {
            2019: {"solar": 100, "wind": 20, "hydro": 200, "nuclear": 0, "bioenergy": 100},
            2020: {"solar": 200, "wind": 30, "hydro": 220, "nuclear": 0, "bioenergy": 120},
            2021: {"solar": 400, "wind": 40, "hydro": 240, "nuclear": 0, "bioenergy": 140},
            2022: {"solar": 700, "wind": 50, "hydro": 260, "nuclear": 0, "bioenergy": 160},
            2023: {"solar": 1000, "wind": 60, "hydro": 280, "nuclear": 0, "bioenergy": 180},
            2024: {"solar": 1400, "wind": 70, "hydro": 300, "nuclear": 100, "bioenergy": 200}, 
            2025: {"solar": 1470, "wind": 73, "hydro": 315, "nuclear": 105, "bioenergy": 210},
            2026: {'solar': 5080, 'wind': 250, 'hydro': 1085, 'nuclear': 361, 'bioenergy': 723},
        },
        "generation_by_year": {2019: 12_000, 2020: 14_000, 2021: 15_200, 2022: 16_200, 2023: 17_200, 2024: 18_200, 2025: 19_110, 2026: 20_020},
    },
    "bihar": {
        "id": "bihar", "name": "Bihar", "code": "IN-BR",
        "capacity_by_year": {
            2019: {"solar": 200, "wind": 10, "hydro": 400, "nuclear": 0, "bioenergy": 300},
            2020: {"solar": 400, "wind": 20, "hydro": 450, "nuclear": 0, "bioenergy": 350},
            2021: {"solar": 700, "wind": 30, "hydro": 500, "nuclear": 0, "bioenergy": 400},
            2022: {"solar": 1100, "wind": 40, "hydro": 550, "nuclear": 200, "bioenergy": 450},
            2023: {"solar": 1500, "wind": 50, "hydro": 600, "nuclear": 200, "bioenergy": 500},
            2024: {"solar": 2000, "wind": 60, "hydro": 650, "nuclear": 200, "bioenergy": 550}, 
            2025: {"solar": 2100, "wind": 63, "hydro": 682, "nuclear": 210, "bioenergy": 577},
            2026: {'solar': 6258, 'wind': 187, 'hydro': 2031, 'nuclear': 624, 'bioenergy': 1716},
        },
        "generation_by_year": {2019: 13_000, 2020: 15_500, 2021: 16_500, 2022: 17_500, 2023: 18_500, 2024: 19_500, 2025: 20_475, 2026: 21_450},
    },
    "odisha": {
        "id": "odisha", "name": "Odisha", "code": "IN-OR",
        "capacity_by_year": {
            2019: {"solar": 300, "wind": 50, "hydro": 2200, "nuclear": 0, "bioenergy": 200},
            2020: {"solar": 600, "wind": 80, "hydro": 2300, "nuclear": 0, "bioenergy": 250},
            2021: {"solar": 1000, "wind": 100, "hydro": 2400, "nuclear": 0, "bioenergy": 300},
            2022: {"solar": 1500, "wind": 120, "hydro": 2500, "nuclear": 0, "bioenergy": 350},
            2023: {"solar": 2000, "wind": 150, "hydro": 2600, "nuclear": 200, "bioenergy": 400},
            2024: {"solar": 2500, "wind": 180, "hydro": 2700, "nuclear": 200, "bioenergy": 450}, 
            2025: {"solar": 2625, "wind": 189, "hydro": 2835, "nuclear": 210, "bioenergy": 472},
            2026: {'solar': 5427, 'wind': 389, 'hydro': 5859, 'nuclear': 433, 'bioenergy': 974},
        },
        "generation_by_year": {2019: 22_000, 2020: 26_000, 2021: 28_000, 2022: 29_500, 2023: 31_000, 2024: 32_800, 2025: 34_440, 2026: 36_080},
    },
    "assam": {
        "id": "assam", "name": "Assam", "code": "IN-AS",
        "capacity_by_year": {
            2019: {"solar": 50, "wind": 10, "hydro": 400, "nuclear": 0, "bioenergy": 80},
            2020: {"solar": 100, "wind": 15, "hydro": 450, "nuclear": 0, "bioenergy": 100},
            2021: {"solar": 180, "wind": 20, "hydro": 500, "nuclear": 0, "bioenergy": 120},
            2022: {"solar": 280, "wind": 25, "hydro": 550, "nuclear": 0, "bioenergy": 140},
            2023: {"solar": 400, "wind": 30, "hydro": 600, "nuclear": 0, "bioenergy": 160},
            2024: {"solar": 550, "wind": 35, "hydro": 650, "nuclear": 0, "bioenergy": 180}, 
            2025: {"solar": 577, "wind": 36, "hydro": 682, "nuclear": 0, "bioenergy": 189},
            2026: {'solar': 857, 'wind': 52, 'hydro': 1014, 'nuclear': 0, 'bioenergy': 280},
        },
        "generation_by_year": {2019: 6_000, 2020: 7_000, 2021: 7_600, 2022: 8_100, 2023: 8_700, 2024: 9_200, 2025: 9_660, 2026: 10_120},
    },
    "uttarakhand": {
        "id": "uttarakhand", "name": "Uttarakhand", "code": "IN-UT",
        "capacity_by_year": {
            2019: {"solar": 200, "wind": 30, "hydro": 3800, "nuclear": 0, "bioenergy": 50},
            2020: {"solar": 350, "wind": 40, "hydro": 3900, "nuclear": 0, "bioenergy": 60},
            2021: {"solar": 500, "wind": 50, "hydro": 4000, "nuclear": 0, "bioenergy": 70},
            2022: {"solar": 700, "wind": 60, "hydro": 4100, "nuclear": 0, "bioenergy": 80},
            2023: {"solar": 900, "wind": 70, "hydro": 4200, "nuclear": 0, "bioenergy": 90},
            2024: {"solar": 1100, "wind": 80, "hydro": 4300, "nuclear": 0, "bioenergy": 100}, 
            2025: {"solar": 1155, "wind": 84, "hydro": 4515, "nuclear": 0, "bioenergy": 105},
            2026: {'solar': 1315, 'wind': 95, 'hydro': 5141, 'nuclear': 0, 'bioenergy': 119},
        },
        "generation_by_year": {2019: 11_000, 2020: 13_000, 2021: 13_800, 2022: 14_600, 2023: 15_500, 2024: 16_400, 2025: 17_220, 2026: 18_040},
    },
    "himachal_pradesh": {
        "id": "himachal_pradesh", "name": "Himachal Pradesh", "code": "IN-HP",
        "capacity_by_year": {
            2019: {"solar": 100, "wind": 20, "hydro": 10200, "nuclear": 0, "bioenergy": 50},
            2020: {"solar": 200, "wind": 30, "hydro": 10400, "nuclear": 0, "bioenergy": 60},
            2021: {"solar": 350, "wind": 40, "hydro": 10600, "nuclear": 0, "bioenergy": 70},
            2022: {"solar": 500, "wind": 50, "hydro": 10800, "nuclear": 0, "bioenergy": 80},
            2023: {"solar": 700, "wind": 60, "hydro": 11000, "nuclear": 0, "bioenergy": 90},
            2024: {"solar": 900, "wind": 70, "hydro": 11200, "nuclear": 0, "bioenergy": 100}, 
            2025: {"solar": 945, "wind": 73, "hydro": 11760, "nuclear": 0, "bioenergy": 105},
            2026: {'solar': 939, 'wind': 71, 'hydro': 11665, 'nuclear': 0, 'bioenergy': 103},
        },
        "generation_by_year": {2019: 25_000, 2020: 28_000, 2021: 30_000, 2022: 31_800, 2023: 33_500, 2024: 35_200, 2025: 36_960, 2026: 38_720},
    },
    "jammu_kashmir": {
        "id": "jammu_kashmir", "name": "Jammu and Kashmir", "code": "IN-JK",
        "capacity_by_year": {
            2019: {"solar": 50, "wind": 10, "hydro": 2800, "nuclear": 0, "bioenergy": 20},
            2020: {"solar": 100, "wind": 15, "hydro": 2900, "nuclear": 0, "bioenergy": 25},
            2021: {"solar": 200, "wind": 20, "hydro": 3000, "nuclear": 0, "bioenergy": 30},
            2022: {"solar": 350, "wind": 25, "hydro": 3100, "nuclear": 0, "bioenergy": 35},
            2023: {"solar": 500, "wind": 30, "hydro": 3200, "nuclear": 0, "bioenergy": 40},
            2024: {"solar": 700, "wind": 35, "hydro": 3300, "nuclear": 0, "bioenergy": 45}, 
            2025: {"solar": 735, "wind": 36, "hydro": 3465, "nuclear": 0, "bioenergy": 47},
            2026: {"solar": 771, "wind": 37, "hydro": 3638, "nuclear": 0, "bioenergy": 49},
        },
        "generation_by_year": {2019: 7_500, 2020: 8_500, 2021: 9_100, 2022: 9_700, 2023: 10_200, 2024: 10_800, 2025: 11_340, 2026: 11_880},
    },
    "goa": {
        "id": "goa", "name": "Goa", "code": "IN-GA",
        "capacity_by_year": {
            2019: {"solar": 30, "wind": 20, "hydro": 10, "nuclear": 0, "bioenergy": 10},
            2020: {"solar": 50, "wind": 25, "hydro": 12, "nuclear": 0, "bioenergy": 12},
            2021: {"solar": 80, "wind": 30, "hydro": 14, "nuclear": 0, "bioenergy": 14},
            2022: {"solar": 120, "wind": 35, "hydro": 16, "nuclear": 0, "bioenergy": 16},
            2023: {"solar": 160, "wind": 40, "hydro": 18, "nuclear": 0, "bioenergy": 18},
            2024: {"solar": 200, "wind": 45, "hydro": 20, "nuclear": 0, "bioenergy": 20}, 
            2025: {"solar": 210, "wind": 47, "hydro": 21, "nuclear": 0, "bioenergy": 21},
            2026: {'solar': 54, 'wind': 11, 'hydro': 5, 'nuclear': 0, 'bioenergy': 5},
        },
        "generation_by_year": {2019: 1_200, 2020: 1_400, 2021: 1_500, 2022: 1_600, 2023: 1_700, 2024: 1_800, 2025: 1_890, 2026: 1_980},
    },
    # ── NE States ────────────────────────────────
    "arunachal_pradesh": {
        "id": "arunachal_pradesh", "name": "Arunachal Pradesh", "code": "IN-AR",
        "capacity_by_year": {
            2019: {"solar": 5, "wind": 2, "hydro": 500, "nuclear": 0, "bioenergy": 5},
            2020: {"solar": 10, "wind": 3, "hydro": 550, "nuclear": 0, "bioenergy": 8},
            2021: {"solar": 20, "wind": 4, "hydro": 600, "nuclear": 0, "bioenergy": 10},
            2022: {"solar": 30, "wind": 5, "hydro": 650, "nuclear": 0, "bioenergy": 12},
            2023: {"solar": 45, "wind": 6, "hydro": 700, "nuclear": 0, "bioenergy": 15},
            2024: {"solar": 60, "wind": 7, "hydro": 750, "nuclear": 0, "bioenergy": 18}, 
            2025: {"solar": 63, "wind": 7, "hydro": 787, "nuclear": 0, "bioenergy": 18},
            2026: {'solar': 129, 'wind': 13, 'hydro': 1595, 'nuclear': 0, 'bioenergy': 34},
        },
        "generation_by_year": {2019: 1_500, 2020: 1_800, 2021: 2_000, 2022: 2_100, 2023: 2_300, 2024: 2_400, 2025: 2_520, 2026: 2_640},
    },
    "manipur": {
        "id": "manipur", "name": "Manipur", "code": "IN-MN",
        "capacity_by_year": {
            2019: {"solar": 5, "wind": 1, "hydro": 120, "nuclear": 0, "bioenergy": 5},
            2020: {"solar": 10, "wind": 2, "hydro": 130, "nuclear": 0, "bioenergy": 8},
            2021: {"solar": 18, "wind": 3, "hydro": 140, "nuclear": 0, "bioenergy": 10},
            2022: {"solar": 25, "wind": 4, "hydro": 150, "nuclear": 0, "bioenergy": 12},
            2023: {"solar": 35, "wind": 5, "hydro": 160, "nuclear": 0, "bioenergy": 15},
            2024: {"solar": 45, "wind": 6, "hydro": 170, "nuclear": 0, "bioenergy": 18}, 
            2025: {"solar": 47, "wind": 6, "hydro": 178, "nuclear": 0, "bioenergy": 18},
            2026: {'solar': 32, 'wind': 3, 'hydro': 117, 'nuclear': 0, 'bioenergy': 11},
        },
        "generation_by_year": {2019: 500, 2020: 650, 2021: 700, 2022: 750, 2023: 800, 2024: 850, 2025: 892, 2026: 935},
    },
    "meghalaya": {
        "id": "meghalaya", "name": "Meghalaya", "code": "IN-ML",
        "capacity_by_year": {
            2019: {"solar": 5, "wind": 2, "hydro": 350, "nuclear": 0, "bioenergy": 10},
            2020: {"solar": 10, "wind": 3, "hydro": 370, "nuclear": 0, "bioenergy": 15},
            2021: {"solar": 20, "wind": 4, "hydro": 390, "nuclear": 0, "bioenergy": 20},
            2022: {"solar": 30, "wind": 5, "hydro": 410, "nuclear": 0, "bioenergy": 25},
            2023: {"solar": 40, "wind": 6, "hydro": 430, "nuclear": 0, "bioenergy": 30},
            2024: {"solar": 50, "wind": 7, "hydro": 450, "nuclear": 0, "bioenergy": 35}, 
            2025: {"solar": 52, "wind": 7, "hydro": 472, "nuclear": 0, "bioenergy": 36},
            2026: {'solar': 38, 'wind': 4, 'hydro': 329, 'nuclear': 0, 'bioenergy': 24},
        },
        "generation_by_year": {2019: 900, 2020: 1_100, 2021: 1_200, 2022: 1_300, 2023: 1_400, 2024: 1_500, 2025: 1_575, 2026: 1_650},
    },
    "mizoram": {
        "id": "mizoram", "name": "Mizoram", "code": "IN-MZ",
        "capacity_by_year": {
            2019: {"solar": 5, "wind": 1, "hydro": 100, "nuclear": 0, "bioenergy": 5},
            2020: {"solar": 10, "wind": 2, "hydro": 110, "nuclear": 0, "bioenergy": 8},
            2021: {"solar": 18, "wind": 3, "hydro": 120, "nuclear": 0, "bioenergy": 10},
            2022: {"solar": 25, "wind": 4, "hydro": 130, "nuclear": 0, "bioenergy": 12},
            2023: {"solar": 35, "wind": 5, "hydro": 140, "nuclear": 0, "bioenergy": 14},
            2024: {"solar": 45, "wind": 6, "hydro": 150, "nuclear": 0, "bioenergy": 16}, 
            2025: {"solar": 47, "wind": 6, "hydro": 157, "nuclear": 0, "bioenergy": 16},
            2026: {'solar': 30, 'wind': 3, 'hydro': 97, 'nuclear': 0, 'bioenergy': 9},
        },
        "generation_by_year": {2019: 350, 2020: 450, 2021: 500, 2022: 540, 2023: 580, 2024: 620, 2025: 651, 2026: 682},
    },
    "nagaland": {
        "id": "nagaland", "name": "Nagaland", "code": "IN-NL",
        "capacity_by_year": {
            2019: {"solar": 5, "wind": 1, "hydro": 90, "nuclear": 0, "bioenergy": 8},
            2020: {"solar": 10, "wind": 2, "hydro": 100, "nuclear": 0, "bioenergy": 12},
            2021: {"solar": 18, "wind": 3, "hydro": 110, "nuclear": 0, "bioenergy": 15},
            2022: {"solar": 25, "wind": 4, "hydro": 120, "nuclear": 0, "bioenergy": 18},
            2023: {"solar": 35, "wind": 5, "hydro": 130, "nuclear": 0, "bioenergy": 20},
            2024: {"solar": 45, "wind": 6, "hydro": 140, "nuclear": 0, "bioenergy": 22}, 
            2025: {"solar": 47, "wind": 6, "hydro": 147, "nuclear": 0, "bioenergy": 23},
            2026: {'solar': 25, 'wind': 2, 'hydro': 73, 'nuclear': 0, 'bioenergy': 11},
        },
        "generation_by_year": {2019: 400, 2020: 550, 2021: 600, 2022: 650, 2023: 700, 2024: 750, 2025: 787, 2026: 825},
    },
    "sikkim": {
        "id": "sikkim", "name": "Sikkim", "code": "IN-SK",
        "capacity_by_year": {
            2019: {"solar": 2, "wind": 1, "hydro": 2000, "nuclear": 0, "bioenergy": 5},
            2020: {"solar": 5, "wind": 2, "hydro": 2050, "nuclear": 0, "bioenergy": 8},
            2021: {"solar": 10, "wind": 3, "hydro": 2100, "nuclear": 0, "bioenergy": 10},
            2022: {"solar": 15, "wind": 4, "hydro": 2150, "nuclear": 0, "bioenergy": 12},
            2023: {"solar": 20, "wind": 5, "hydro": 2200, "nuclear": 0, "bioenergy": 14},
            2024: {"solar": 25, "wind": 6, "hydro": 2250, "nuclear": 0, "bioenergy": 16}, 
            2025: {"solar": 26, "wind": 6, "hydro": 2362, "nuclear": 0, "bioenergy": 16},
            2026: {'solar': 26, 'wind': 5, 'hydro': 2299, 'nuclear': 0, 'bioenergy': 14},
        },
        "generation_by_year": {2019: 4_200, 2020: 5_000, 2021: 5_400, 2022: 5_800, 2023: 6_200, 2024: 6_500, 2025: 6_825, 2026: 7_150},
    },
    "tripura": {
        "id": "tripura", "name": "Tripura", "code": "IN-TR",
        "capacity_by_year": {
            2019: {"solar": 10, "wind": 2, "hydro": 60, "nuclear": 0, "bioenergy": 20},
            2020: {"solar": 20, "wind": 3, "hydro": 70, "nuclear": 0, "bioenergy": 25},
            2021: {"solar": 40, "wind": 4, "hydro": 80, "nuclear": 0, "bioenergy": 30},
            2022: {"solar": 60, "wind": 5, "hydro": 90, "nuclear": 0, "bioenergy": 35},
            2023: {"solar": 80, "wind": 6, "hydro": 100, "nuclear": 0, "bioenergy": 40},
            2024: {"solar": 100, "wind": 7, "hydro": 110, "nuclear": 0, "bioenergy": 45}, 
            2025: {"solar": 105, "wind": 7, "hydro": 115, "nuclear": 0, "bioenergy": 47},
            2026: {'solar': 431, 'wind': 27, 'hydro': 469, 'nuclear': 0, 'bioenergy': 191},
        },
        "generation_by_year": {2019: 1_600, 2020: 2_000, 2021: 2_200, 2022: 2_300, 2023: 2_500, 2024: 2_600, 2025: 2_730, 2026: 2_860},
    },
    # ── UTs ──────────────────────────────────────
    "delhi": {
        "id": "delhi", "name": "Delhi", "code": "IN-DL",
        "capacity_by_year": {
            2019: {"solar": 200, "wind": 0, "hydro": 0, "nuclear": 0, "bioenergy": 100},
            2020: {"solar": 400, "wind": 0, "hydro": 0, "nuclear": 0, "bioenergy": 120},
            2021: {"solar": 700, "wind": 0, "hydro": 0, "nuclear": 0, "bioenergy": 140},
            2022: {"solar": 1100, "wind": 0, "hydro": 0, "nuclear": 0, "bioenergy": 160},
            2023: {"solar": 1500, "wind": 0, "hydro": 0, "nuclear": 0, "bioenergy": 180},
            2024: {"solar": 2000, "wind": 0, "hydro": 0, "nuclear": 0, "bioenergy": 200}, 
            2025: {"solar": 2100, "wind": 0, "hydro": 0, "nuclear": 0, "bioenergy": 210},
            2026: {'solar': 2354, 'wind': 0, 'hydro': 0, 'nuclear': 0, 'bioenergy': 234},
        },
        "generation_by_year": {2019: 12_000, 2020: 14_000, 2021: 14_800, 2022: 15_600, 2023: 16_500, 2024: 17_400, 2025: 18_270, 2026: 19_140},
    },
    "puducherry": {
        "id": "puducherry", "name": "Puducherry", "code": "IN-PY",
        "capacity_by_year": {
            2019: {"solar": 10, "wind": 5, "hydro": 0, "nuclear": 0, "bioenergy": 5},
            2020: {"solar": 20, "wind": 8, "hydro": 0, "nuclear": 0, "bioenergy": 8},
            2021: {"solar": 35, "wind": 10, "hydro": 0, "nuclear": 0, "bioenergy": 10},
            2022: {"solar": 50, "wind": 12, "hydro": 0, "nuclear": 0, "bioenergy": 12},
            2023: {"solar": 70, "wind": 14, "hydro": 0, "nuclear": 0, "bioenergy": 14},
            2024: {"solar": 90, "wind": 16, "hydro": 0, "nuclear": 0, "bioenergy": 16}, 
            2025: {"solar": 94, "wind": 16, "hydro": 0, "nuclear": 0, "bioenergy": 16},
            2026: {'solar': 84, 'wind': 13, 'hydro': 0, 'nuclear': 0, 'bioenergy': 13},
        },
        "generation_by_year": {2019: 700, 2020: 850, 2021: 900, 2022: 960, 2023: 1_030, 2024: 1_100, 2025: 1_155, 2026: 1_210},
    },
    "chandigarh": {
        "id": "chandigarh", "name": "Chandigarh", "code": "IN-CH",
        "capacity_by_year": {
            2019: {"solar": 20, "wind": 0, "hydro": 0, "nuclear": 0, "bioenergy": 5},
            2020: {"solar": 35, "wind": 0, "hydro": 0, "nuclear": 0, "bioenergy": 8},
            2021: {"solar": 50, "wind": 0, "hydro": 0, "nuclear": 0, "bioenergy": 10},
            2022: {"solar": 70, "wind": 0, "hydro": 0, "nuclear": 0, "bioenergy": 12},
            2023: {"solar": 90, "wind": 0, "hydro": 0, "nuclear": 0, "bioenergy": 14},
            2024: {"solar": 110, "wind": 0, "hydro": 0, "nuclear": 0, "bioenergy": 16}, 
            2025: {"solar": 115, "wind": 0, "hydro": 0, "nuclear": 0, "bioenergy": 16},
            2026: {'solar': 69, 'wind': 0, 'hydro': 0, 'nuclear': 0, 'bioenergy': 9},
        },
        "generation_by_year": {2019: 200, 2020: 260, 2021: 280, 2022: 300, 2023: 330, 2024: 350, 2025: 367, 2026: 385},
    },
    "andaman_nicobar": {
        "id": "andaman_nicobar", "name": "Andaman and Nicobar", "code": "IN-AN",
        "capacity_by_year": {
            2019: {"solar": 10, "wind": 5, "hydro": 0, "nuclear": 0, "bioenergy": 3},
            2020: {"solar": 20, "wind": 8, "hydro": 0, "nuclear": 0, "bioenergy": 5},
            2021: {"solar": 35, "wind": 10, "hydro": 0, "nuclear": 0, "bioenergy": 7},
            2022: {"solar": 50, "wind": 12, "hydro": 0, "nuclear": 0, "bioenergy": 9},
            2023: {"solar": 70, "wind": 14, "hydro": 0, "nuclear": 0, "bioenergy": 11},
            2024: {"solar": 90, "wind": 16, "hydro": 0, "nuclear": 0, "bioenergy": 13}, 
            2025: {"solar": 94, "wind": 16, "hydro": 0, "nuclear": 0, "bioenergy": 13},
            2026: {'solar': 101, 'wind': 16, 'hydro': 0, 'nuclear': 0, 'bioenergy': 13},
        },
        "generation_by_year": {2019: 200, 2020: 260, 2021: 280, 2022: 300, 2023: 320, 2024: 340, 2025: 357, 2026: 374},
    },
    "dadra_nagar_haveli": {
        "id": "dadra_nagar_haveli", "name": "Dadra and Nagar Haveli", "code": "IN-DN",
        "capacity_by_year": {
            2019: {"solar": 20, "wind": 0, "hydro": 5, "nuclear": 0, "bioenergy": 5},
            2020: {"solar": 40, "wind": 0, "hydro": 5, "nuclear": 0, "bioenergy": 8},
            2021: {"solar": 60, "wind": 0, "hydro": 5, "nuclear": 0, "bioenergy": 10},
            2022: {"solar": 80, "wind": 0, "hydro": 5, "nuclear": 0, "bioenergy": 12},
            2023: {"solar": 100, "wind": 0, "hydro": 5, "nuclear": 0, "bioenergy": 14},
            2024: {"solar": 120, "wind": 0, "hydro": 5, "nuclear": 0, "bioenergy": 16}, 
            2025: {"solar": 126, "wind": 0, "hydro": 5, "nuclear": 0, "bioenergy": 16},
            2026: {"solar": 132, "wind": 0, "hydro": 5, "nuclear": 0, "bioenergy": 16},
        },
        "generation_by_year": {2019: 360, 2020: 440, 2021: 470, 2022: 500, 2023: 540, 2024: 580, 2025: 609, 2026: 638},
    },
    "daman_diu": {
        "id": "daman_diu", "name": "Daman and Diu", "code": "IN-DD",
        "capacity_by_year": {
            2019: {"solar": 10, "wind": 5, "hydro": 0, "nuclear": 0, "bioenergy": 3},
            2020: {"solar": 20, "wind": 8, "hydro": 0, "nuclear": 0, "bioenergy": 5},
            2021: {"solar": 30, "wind": 10, "hydro": 0, "nuclear": 0, "bioenergy": 7},
            2022: {"solar": 40, "wind": 12, "hydro": 0, "nuclear": 0, "bioenergy": 9},
            2023: {"solar": 55, "wind": 14, "hydro": 0, "nuclear": 0, "bioenergy": 11},
            2024: {"solar": 70, "wind": 16, "hydro": 0, "nuclear": 0, "bioenergy": 13}, 
            2025: {"solar": 73, "wind": 16, "hydro": 0, "nuclear": 0, "bioenergy": 13},
            2026: {"solar": 76, "wind": 16, "hydro": 0, "nuclear": 0, "bioenergy": 13},
        },
        "generation_by_year": {2019: 160, 2020: 210, 2021: 230, 2022: 245, 2023: 260, 2024: 280, 2025: 294, 2026: 308},
    },
    "lakshadweep": {
        "id": "lakshadweep", "name": "Lakshadweep", "code": "IN-LD",
        "capacity_by_year": {
            2019: {"solar": 2, "wind": 1, "hydro": 0, "nuclear": 0, "bioenergy": 1},
            2020: {"solar": 3, "wind": 1, "hydro": 0, "nuclear": 0, "bioenergy": 1},
            2021: {"solar": 5, "wind": 2, "hydro": 0, "nuclear": 0, "bioenergy": 2},
            2022: {"solar": 7, "wind": 2, "hydro": 0, "nuclear": 0, "bioenergy": 2},
            2023: {"solar": 10, "wind": 3, "hydro": 0, "nuclear": 0, "bioenergy": 3},
            2024: {"solar": 13, "wind": 3, "hydro": 0, "nuclear": 0, "bioenergy": 3}, 
            2025: {"solar": 13, "wind": 3, "hydro": 0, "nuclear": 0, "bioenergy": 3},
            2026: {'solar': 23, 'wind': 5, 'hydro': 0, 'nuclear': 0, 'bioenergy': 5},
        },
        "generation_by_year": {2019: 25, 2020: 30, 2021: 32, 2022: 34, 2023: 37, 2024: 40, 2025: 42, 2026: 44},
    },
    "ladakh": {
        "id": "ladakh", "name": "Ladakh", "code": "IN-LA",
        "capacity_by_year": {
            2019: {"solar": 10, "wind": 5, "hydro": 100, "nuclear": 0, "bioenergy": 2},
            2020: {"solar": 25, "wind": 8, "hydro": 110, "nuclear": 0, "bioenergy": 3},
            2021: {"solar": 45, "wind": 10, "hydro": 120, "nuclear": 0, "bioenergy": 4},
            2022: {"solar": 70, "wind": 12, "hydro": 130, "nuclear": 0, "bioenergy": 5},
            2023: {"solar": 100, "wind": 15, "hydro": 140, "nuclear": 0, "bioenergy": 6},
            2024: {"solar": 130, "wind": 18, "hydro": 150, "nuclear": 0, "bioenergy": 7}, 
            2025: {"solar": 136, "wind": 18, "hydro": 157, "nuclear": 0, "bioenergy": 7},
            2026: {'solar': 64, 'wind': 7, 'hydro': 72, 'nuclear': 0, 'bioenergy': 3},
        },
        "generation_by_year": {2019: 280, 2020: 350, 2021: 380, 2022: 420, 2023: 460, 2024: 500, 2025: 525, 2026: 550},
    },
}


def _hydrate_with_real_data():
    """Attempt to overlay scraped outputs into STATES_DATA if a dump is available."""
    scraper_out_dir = Path(__file__).resolve().parent.parent.parent.parent / "india_energy_scraper" / "output"
    aggregated_file = scraper_out_dir / "aggregated_energy_data.json"
    
    if aggregated_file.exists():
        try:
            with open(aggregated_file, "r") as f:
                scraped_data = json.load(f)
                
                # Mapping state_id like 'GJ' back to our internal index keys like 'gujarat'
                id_to_key = {s["code"].split('-')[1]: k for k, s in STATES_DATA.items()}
                
                for record in scraped_data:
                    state_id = record.get("state_id")
                    if state_id and state_id in id_to_key:
                        internal_key = id_to_key[state_id]
                        total_mw = record.get("total_capacity_mw", 0)
                        mix = record.get("energy_mix", {})
                        
                        # Override the latest year (2026) with real scraped data distribution
                        if total_mw > 0:
                            STATES_DATA[internal_key]["capacity_by_year"][2026] = {
                                "solar": int(total_mw * (mix.get("solar_percent", 0) / 100)),
                                "wind": int(total_mw * (mix.get("wind_percent", 0) / 100)),
                                "hydro": int(total_mw * (mix.get("hydro_percent", 0) / 100)),
                                "bioenergy": int(total_mw * (mix.get("biomass_percent", 0) / 100)),
                                "nuclear": int(total_mw * (mix.get("nuclear_percent", 0) / 100))
                            }
        except Exception as e:
            print(f"Warning: Failed to hydrate real scraped data: {e}")

_hydrate_with_real_data()

def get_all_states() -> list[dict]:
    """Return summary list: [{id, name, code}, ...]."""
    return [
        {"id": s["id"], "name": s["name"], "code": s["code"]}
        for s in STATES_DATA.values()
    ]


def get_state_raw(state_id: str) -> dict | None:
    """Return raw time-series record, or None."""
    return STATES_DATA.get(state_id)


def get_available_years() -> dict:
    """Return the available year range."""
    return {"min_year": MIN_YEAR, "max_year": MAX_YEAR}

import json, re
from collections import Counter

# Load the GeoJSON
with open(r'C:\Users\Om Patel\Videos\1 Projects\Energy Website\web\backend\data\power_plants.geojson') as f:
    gj = json.load(f)
features = gj.get("features", [])

# Load Wikipedia coal reference
coal_ref = {}
with open(r'C:\Users\Om Patel\Videos\1 Projects\Energy Website\coal_power_stations_india.csv') as f:
    lines = f.readlines()
    for line in lines[1:]:
        parts = line.strip().split(',')
        if len(parts) >= 3:
            name = parts[0].strip()
            state = parts[1].strip()
            cap = parts[2].strip()
            coal_ref[name.lower()] = {'name': name, 'state': state, 'capacity': cap}

state_plants = {}
for f in features:
    p = f.get("properties", {})
    s = p.get("state", "Unknown")
    if s not in state_plants:
        state_plants[s] = []
    state_plants[s].append(p)

def find_plant_in_gj(state_plants_list, search_name):
    search_words = search_name.lower().split()
    key_words = [w for w in search_words if w not in 
                 ['dam', 'power', 'plant', 'hydroelectric', 'project', 'station', 'thermal',
                  'the', 'a', 'an', 'in', 'of', 'and', 'phase', 'i', 'ii', 'iii', 'stage']]
    if not key_words:
        key_words = search_words[:3]
    for gjp in state_plants_list:
        gj_name = gjp.get("name", "").lower()
        match_count = sum(1 for kw in key_words[:4] if kw in gj_name)
        if match_count >= 2:
            return gjp
        if search_name.lower()[:20] in gj_name or search_name.lower() in gj_name:
            return gjp
    return None

known_major_plants = {
    "Jammu and Kashmir": {
        "hydro": [
            ("Baglihar Dam", 900, "NHPC"),
            ("Salal Hydroelectric Plant", 690, "NHPC"),
            ("Uri Hydroelectric Project", 480, "NHPC"),
            ("Dulhasti Hydroelectric Plant", 390, "NHPC"),
            ("Kishanganga Hydroelectric Project", 330, "NHPC"),
            ("Lower Jhelum Hydroelectric Plant", 105, "JKPDC"),
            ("Upper Sindh Hydroelectric Plant", 105, "JKPDC"),
            ("Sewa Hydroelectric Plant", 120, "JKPDC"),
            ("Chenani Hydroelectric Plant", 24, "JKPDC"),
            ("Nimoo Bazgo Hydroelectric Plant", 45, "NHPC"),
            ("Chutak Hydroelectric Plant", 44, "NHPC"),
            ("Dumkhar Hydroelectric Plant", 19, "NHPC"),
        ],
        "gas": [
            ("Pampore Gas Turbine Power Station", 180, "JKPDC")
        ]
    },
    "Himachal Pradesh": {
        "hydro": [
            ("Nathpa Jhakri Dam", 1500, "SJVNL"),
            ("Koldam Dam", 800, "NTPC"),
            ("Chamera Dam", 1071, "NHPC"),
            ("Bhakra Dam Left Bank", 785, "BBMB"),
            ("Dehar Power House", 990, "BBMB"),
            ("Parbati Hydroelectric Project", 830, "NHPC"),
            ("Baspa-II Hydroelectric Plant", 300, "JHPL"),
            ("Baira Siul Dam", 180, "NHPC"),
            ("Largi Hydroelectric Project", 126, "HPPCL"),
            ("Sanjay Vidyut Project Bhaba", 120, "HPPCL"),
            ("Sorang Dam", 100, "HPPCL"),
            ("Kashang Hydroelectric Plant", 65, "HPPCL"),
            ("Sainj Hydroelectric Project", 100, "HPPCL"),
            ("Shanan Power House", 110, "BBMB"),
            ("Andhra Hydroelectric Plant", 17, "HPPCL"),
            ("Malana Hydroelectric Plant", 86, "MHL"),
            ("Budhil Hydroelectric Plant", 70, "LANCO"),
            ("Tidong Hydroelectric Plant", 100, "Tidong JV"),
            ("Bajoli Holi Hydroelectric Plant", 180, "Bajoli Holi JV"),
        ]
    },
    "Punjab": {
        "coal": [
            ("Guru Gobind Singh Super Thermal Power Plant", 2100, "Punjab State Power Corp"),
            ("Guru Hargobind Thermal Power Plant", 920, "Punjab State Power Corp"),
            ("GHTP Lehra Mohabbat", 500, "Punjab State Power Corp"),
            ("Rajpura Thermal Power Plant", 1400, "L&T Nabha Power"),
            ("Talwandi Sabo Power Project", 1980, "Vedanta"),
        ],
        "hydro": [
            ("Bhakra Dam Right Bank", 785, "BBMB"),
            ("Ranjit Sagar Dam", 600, "PSPCL"),
            ("Pong Dam", 396, "BBMB"),
            ("Shahpur Kandi Dam", 206, "PSPCL"),
            ("Mukerian Hydel Complex", 215, "PSPCL"),
            ("Harike Barrage", 66, "BBMB"),
            ("UBDC Shahnehar Canal", 360, "BBMB"),
        ]
    },
    "Uttaranchal": {
        "hydro": [
            ("Tehri Dam", 1000, "THDC"),
            ("Koteshwar Dam", 400, "THDC"),
            ("Maneri Bhali Project", 304, "UJVNL"),
            ("Vishnuprayag Hydroelectric Plant", 400, "GVK/JP Group"),
            ("Srinagar Dam", 330, "THDC"),
            ("Vishnugad Pipalkoti", 444, "THDC"),
            ("Lakhwar Dam", 300, "UJVNL"),
            ("Singoli Bhatwari", 99, "LANCO"),
            ("Phata Byung", 76, "NHDC"),
            ("Dhauliganga-I", 280, "NHPC"),
            ("Dhauliganga-II", 110, "NHPC"),
            ("Tanakpur Dam", 120, "NHPC"),
            ("Chilla Hydroelectric Plant", 144, "UJVNL"),
            ("Ramganga Dam", 198, "UJVNL"),
            ("Sharda Sagar Dam", 41, "UJVNL"),
            ("Madhyamaheshwar", 60, "Him Urja"),
        ],
    },
    "Haryana": {
        "coal": [
            ("Rajiv Gandhi Thermal Power Plant", 1200, "HPGCL"),
            ("Panipat Thermal Power Station", 1230, "HPGCL"),
            ("Deenbandhu Chhotu Ram Thermal Power Plant", 1200, "HPGCL"),
            ("Indira Gandhi Super Thermal Power Project", 1500, "NTPC"),
            ("Jharli Super Thermal Power Project", 1320, "HPGCL"),
        ],
        "gas": [
            ("Faridabad Thermal Power Plant", 430, "HPGCL"),
            ("Hissar Thermal Power Plant", 120, "HPGCL"),
        ],
        "solar": [
            ("Kamalpur Solar Power Plant", 50, "Private"),
            ("SECI Solar Parks in Haryana", 750, "SECI"),
        ]
    }
}

total_known_across_all = sum(sum(len(p) for p in k.values()) for k in known_major_plants.values())
total_found = 0
total_missing = 0
total_cap_issues = 0

for state in ["Jammu and Kashmir", "Himachal Pradesh", "Punjab", "Uttaranchal", "Haryana"]:
    gj_plants = state_plants.get(state, [])
    gj_by_type = Counter(p.get("type", "unknown") for p in gj_plants)
    gj_with_cap = sum(1 for p in gj_plants if p.get("capacity_mw", 0) > 0)
    gj_zero_cap = sum(1 for p in gj_plants if p.get("capacity_mw", 0) == 0)
    
    print(f"\n{'='*80}")
    print(f"  {state.upper()}")
    print(f"  GeoJSON: {len(gj_plants)} plants | {gj_with_cap} with data | {gj_zero_cap} need data")
    print(f"  Types: {dict(gj_by_type)}")
    print(f"{'='*80}")
    
    known_data = known_major_plants.get(state, {})
    state_missing = []
    
    for ptype, plants in known_data.items():
        if not plants:
            continue
        print(f"\n  >>> {ptype.upper()} ({len(plants)} known) <<<")
        for p in plants:
            pname, pcap, pop = p[0], p[1], p[2]
            found = find_plant_in_gj(gj_plants, pname)
            if found:
                gj_cap = found.get("capacity_mw", 0)
                cap_ok = gj_cap > 0
                cap_match = abs(gj_cap - pcap) / max(pcap, 1) < 0.15 if cap_ok else False
                if cap_ok and cap_match:
                    status_icon = "OK"
                elif cap_ok and not cap_match:
                    status_icon = "MISMATCH"
                    total_cap_issues += 1
                else:
                    status_icon = "ZERO_CAP"
                    total_cap_issues += 1
                print(f"    [{status_icon:9s}] {pname[:55]:55s} | Wiki:{pcap:5d}MW | GeoJSON:{gj_cap:6.0f}MW")
                total_found += 1
            else:
                print(f"    [MISSING   ] {pname[:55]:55s} | Wiki:{pcap:5d}MW | NOT IN GeoJSON")
                state_missing.append(pname)
                total_missing += 1
    
    zero_cap_known = [p for p in gj_plants if p.get("capacity_mw", 0) == 0 and p.get("name", "").lower() not in ['unknown', 'unnamed']]
    if zero_cap_known:
        print(f"\n  >>> PLANTS IN GeoJSON WITH 0 CAPACITY ({len(zero_cap_known)} total) <<<")
        for p in zero_cap_known[:5]:
            print(f"    [DATA_NEEDED] {p.get('name','unnamed')[:55]:55s} | type={p.get('type','?'):8s} | CAPACITY=0MW")
        if len(zero_cap_known) > 5:
            print(f"    ... and {len(zero_cap_known)-5} more")

print(f"\n\n{'='*80}")
print(f"  AUDIT PROGRESS: 5/36 states completed (14%)")
print(f"  Total known plants checked: {total_known_across_all}")
print(f"  Found in GeoJSON: {total_found}")
print(f"  MISSING from GeoJSON: {total_missing}")
print(f"  Capacity issues: {total_cap_issues}")
print(f"{'='*80}")
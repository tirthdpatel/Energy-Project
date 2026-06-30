import json, re
from collections import Counter

with open(r'C:\Users\Om Patel\Videos\1 Projects\Energy Website\web\backend\data\power_plants.geojson') as f:
    gj = json.load(f)
features = gj.get("features", [])

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
                  'the', 'a', 'an', 'in', 'of', 'and', 'phase', 'i', 'ii', 'iii', 'stage', 'park']]
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
    "Delhi": {
        "gas": [
            ("Pragati Combined Cycle Gas Power Plant", 330, "IPGCL"),
            ("Pragati-III Combined Cycle Power Plant", 1500, "PPCL"),
            ("IPGCL Gas Turbine Power Station", 270, "IPGCL"),
            ("Rithala Gas Turbine Plant", 60, "IPGCL"),
        ],
        "coal": [
            ("Rajghat Power Station", 135, "IPGCL"),
            ("Badarpur Thermal Power Station", 705, "NTPC"),
        ],
        "solar": [
            ("Badarpur Solar Plant", 5, "IPGCL"),
            ("Rohini Solar Plant", 5, "IPGCL"),
        ]
    },
    "Rajasthan": {
        "coal": [
            ("Suratgarh Super Thermal Power Plant", 1500, "RVUNL"),
            ("Kota Super Thermal Power Station", 1240, "RVUNL"),
            ("Chhabra Super Thermal Power Station", 2320, "RVUNL"),
            ("Kalisthan Thermal Power Station", 600, "RVUNL"),
            ("Giral Lignite Thermal Power Station", 250, "RVUNL"),
            ("Barsingsar Thermal Power Station", 250, "NLC"),
            ("Satpura Thermal Power Station", 1330, "MPPGCL"),
        ],
        "gas": [
            ("Anta Thermal Power Station", 430, "NTPC"),
            ("Dholpur Combined Cycle Power Station", 330, "RVUNL"),
            ("Ramgarh Gas Thermal Power Station", 330, "RVUNL"),
        ],
        "hydro": [
            ("Mahi Bajaj Sagar Dam", 140, "RVUNL"),
            ("Rana Pratap Sagar Dam", 172, "RRVPNL"),
            ("Jawahar Sagar Dam", 99, "RRVPNL"),
            ("Bisalpur Dam", 172, "RRVPNL"),
        ],
        "solar": [
            ("Bhadla Solar Park", 2245, "NTPC/SECI"),
            ("Pavagada Solar Park", 2050, "SECI"),
            ("Bikaner Solar Park", 1000, "SECI/Private"),
            ("Phalodi Solar Plant", 1000, "SECI"),
            ("Jaisalmer Solar Park", 600, "SECI"),
            ("Nokh Solar Park", 1000, "SECI"),
        ],
        "nuclear": [
            ("Rajasthan Atomic Power Station", 1180, "NPCIL"),
        ]
    },
    "Uttar Pradesh": {
        "coal": [
            ("Rihand Super Thermal Power Station", 3000, "NTPC"),
            ("Singrauli Super Thermal Power Station", 2000, "NTPC"),
            ("NTPC Dadri", 1820, "NTPC"),
            ("Anpara Thermal Power Station", 2630, "UPRVUNL"),
            ("Obra Thermal Power Station", 1550, "UPRVUNL"),
            ("Harduaganj Thermal Power Station", 860, "UPRVUNL"),
            ("Panki Thermal Power Station", 1260, "UPRVUNL"),
            ("Unchahar Thermal Power Station", 1550, "NTPC"),
            ("Parichha Thermal Power Station", 750, "UPRVUNL"),
            ("Tanda Thermal Power Station", 1760, "NTPC"),
            ("Feroze Gandhi Unchahar Thermal Power Plant", 1050, "NTPC"),
            ("Lalitpur Super Thermal Power Project", 1980, "BHEL/NTPC"),
        ],
        "gas": [
            ("Auraiya Gas Power Plant", 660, "NTPC"),
            ("National Capital TPP", 817, "NTPC"),
            ("Kasimpur CCPP", 150, "private"),
            ("Khashipur CCPP", 130, "private"),
        ],
        "hydro": [
            ("Rihand Dam", 300, "UPJVNL"),
            ("Obra Dam", 99, "UPJVNL"),
            ("Koppuram Kuan", 20, "UPJVNL"),
        ],
        "nuclear": [
            ("Narora Atomic Power Station", 440, "NPCIL"),
        ],
        "solar": [
            ("Bundelkhand Solar Park", 1000, "SECI"),
            ("Jalaun Solar Park", 600, "SECI"),
            ("Gautam Buddh Nagar Solar", 100, "Private"),
        ]
    },
    "Bihar": {
        "coal": [
            ("Barauni Thermal Power Station", 720, "BSPGCL"),
            ("Kahalgaon Super Thermal Power Station", 2340, "NTPC"),
            ("Nabinagar Super Thermal Power Project", 1980, "NTPC"),
            ("Muzaffarpur Thermal Power Station", 1100, "BSPGCL"),
            ("Kanti Thermal Power Station", 600, "BSPGCL"),
            ("Koderma Thermal Power Station", 1000, "DVC"),
        ],
        "hydro": [
            ("Kosi Hydel Power Plant", 18, "BSPGCL"),
            ("Sone Barrage Power Plant", 15, "BSPGCL"),
        ],
        "solar": [
            ("Kajra Solar Plant", 50, "Private"),
            ("Buxar Solar Park", 200, "SECI"),
            ("Banka Solar Park", 250, "SECI"),
        ]
    },
    "Chandigarh": {
        "solar": [
            ("Chandigarh Solar City Project", 70, "Chandigarh Administration"),
        ]
    }
}

total_found = 0
total_missing = 0
total_cap_issues = 0

for state in ["Delhi", "Rajasthan", "Uttar Pradesh", "Bihar", "Chandigarh"]:
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
                    status_icon = f"MISMATCH(Wiki:{pcap}M->GJ:{gj_cap}M)"
                    total_cap_issues += 1
                else:
                    status_icon = "ZERO_CAP"
                    total_cap_issues += 1
                print(f"    [{status_icon:9s}] {pname[:55]:55s}")
                total_found += 1
            else:
                print(f"    [MISSING   ] {pname[:55]:55s} | Wiki:{pcap:5d}MW | {pop}")
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
print(f"  AUDIT PROGRESS: 10/36 states completed (28%)")
print(f"  Total known plants checked: {total_found + total_missing}")
print(f"  Found in GeoJSON: {total_found}")
print(f"  MISSING from GeoJSON: {total_missing}")
print(f"  Capacity issues: {total_cap_issues}")
print(f"{'='*80}")

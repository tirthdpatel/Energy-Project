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
    "Gujarat": {
        "coal": [
            ("Mundra Thermal Power Station", 4620, "Adani Power"),
            ("Mundra Ultra Mega Power Project", 4000, "Tata Power"),
            ("Wanakbori Thermal Power Station", 2270, "GSECL"),
            ("Sikka Thermal Power Station", 500, "GSECL"),
            ("Gandhinagar Thermal Power Station", 630, "GSECL"),
            ("Ukai Thermal Power Station", 1110, "GSECL"),
            ("Kutch Thermal Power Station", 150, "GSECL"),
            ("Akrimota Thermal Power Station", 250, "GMDC"),
            ("Surat Thermal Power Station", 500, "GIPCL"),
            ("Sabarmati Thermal Power Station", 362, "Torrent Power"),
            ("Essar Salaya Power Plant", 1200, "Essar Energy"),
            ("Dhuvaran Thermal Power Station", 330, "GSECL"),
        ],
        "gas": [
            ("SUGEN Combined Cycle Power Plant", 1160, "GIPCL"),
            ("Uran Gas Turbine Power Station", 672, "GAIL"),
            ("GPEC Combined Cycle Power Plant", 655, "GPEC"),
            ("Jhanor-Gandhar TPS", 660, "NTPC"),
            ("Kawas TPS", 645, "NTPC"),
            ("Pipavav Combined Cycle Power Plant", 350, "Private"),
            ("Hazira CCPP", 515, "Private"),
            ("Utran Gas Based Power Station", 343, "GSECL"),
            ("Vadodara Gas Based CCPP", 200, "GSECL"),
            ("Dhuvaran Gas Based CCPP", 220, "GSECL"),
        ],
        "nuclear": [
            ("Kakrapar Atomic Power Station", 2200, "NPCIL"),
        ],
        "hydro": [
            ("Sardar Sarovar Dam", 1450, "Sardar Sarovar Narmada Nigam"),
            ("Kadana Dam", 240, "GSECL"),
            ("Ukai Dam", 305, "GSECL"),
            ("Dharoi Dam", 28, "GSECL"),
            ("Panam Dam", 18, "GSECL"),
        ],
        "solar": [
            ("Charanka Solar Park", 790, "Gujarat State"),
            ("Adani Green Solar Park (Khavda)", 5000, "Adani"),
            ("Raghanesda Solar Plant", 100, "Private"),
        ],
        "wind": [
            ("Kutch Wind Farm (Gujarat Hybrid Renewable Energy Park)", 11500, "Various"),
            ("Mundra Wind Farm", 100, "Adani"),
        ]
    },
    "Madhya Pradesh": {
        "coal": [
            ("Vindhyachal Super Thermal Power Station", 4760, "NTPC"),
            ("Sasan Ultra Mega Power Project", 3960, "Reliance Power"),
            ("Sant Singaji Thermal Power Plant", 2520, "MPPGC"),
            ("Dada Dhuniwale Thermal Power Plant", 1200, "MPPGC"),
            ("Sanjay Gandhi Thermal Power Station", 1340, "MPPGCL"),
            ("Satpura Thermal Power Station", 1330, "MPPGCL"),
            ("Amarkantak Thermal Power Station", 210, "MPPGCL"),
        ],
        "hydro": [
            ("Bargi Dam", 220, "MPPGCL"),
            ("Indira Sagar Dam", 1000, "NHPC"),
            ("Omkareshwar Dam", 520, "NHPC"),
            ("Bansagar Dam", 425, "MPPGCL"),
        ],
        "solar": [
            ("Rewa Ultra Mega Solar Park", 750, "SECI"),
            ("Neemuch Solar Plant", 151, "Private"),
        ]
    },
    "Chhattisgarh": {
        "coal": [
            ("KSK Mahanadi Power Project", 3600, "KSK Energy"),
            ("Jindal Tamnar Thermal Power Plant", 3400, "JSPL"),
            ("Sipat Thermal Power Plant", 2980, "NTPC"),
            ("Korba Super Thermal Power Plant", 2600, "NTPC"),
            ("RKM Powergen Thermal Power Plant", 1440, "R.K. Powergen"),
            ("DB Thermal Project Ltd.", 1200, "DB POWER"),
            ("Hasdeo Thermal Power Station", 840, "CSPGCL"),
            ("Lanco Amarkantak Power Plant", 600, "Lanco Infratech"),
            ("Dr Shyama Prasad Mukherjee Thermal Power Station", 500, "CSPGCL"),
            ("NSPCL Bhilai Power Plant", 500, "NSPCL"),
        ],
        "hydro": [
            ("Hasdeo Bango Dam", 120, "CSPGCL"),
            ("Dudhawa Dam", 20, "CSPGCL"),
        ],
    },
    "Jharkhand": {
        "coal": [
            ("Koderma Thermal Power Station", 1000, "DVC"),
            ("Bokaro Thermal Power Station", 700, "DVC"),
            ("Tenughat Thermal Power Station", 420, "JSEB"),
            ("Maithon Thermal Power Station", 1050, "DVC/Tata"),
            ("Patratu Thermal Power Station", 800, "JSEB"),
            ("Chandrapura Thermal Power Station", 700, "DVC"),
            ("Adani Godda Thermal Power Plant", 1320, "Adani"),
        ],
        "hydro": [
            ("Maithon Dam", 63, "DVC"),
            ("Panchet Dam", 80, "DVC"),
            ("Tilaiya Dam", 4, "DVC"),
            ("Subarnarekha Dam", 130, "JSEB"),
        ],
    },
    "Odisha": {
        "coal": [
            ("Talcher Super Thermal Power Station", 3000, "NTPC"),
            ("NTPC Kaniha", 3000, "NTPC"),
            ("IFFCO Paradeep Thermal Plant", 1200, "IFFCO"),
            ("Nalco Captive Power Plant", 1200, "NALCO"),
            ("Vedanta Jharsuguda Power Plant", 2400, "Vedanta"),
            ("OPGC Jharsuguda", 840, "OPGC"),
        ],
        "hydro": [
            ("Hirakud Dam", 347, "OHPC"),
            ("Balimela Dam", 510, "OHPC"),
            ("Indravati Dam", 600, "OHPC"),
            ("Upper Kolab Dam", 320, "OHPC"),
            ("Rengali Dam", 250, "OHPC"),
        ],
    },
}

total_found = 0
total_missing = 0
total_cap_issues = 0

for state in ["Gujarat", "Madhya Pradesh", "Chhattisgarh", "Jharkhand", "Odisha"]:
    gj_plants = state_plants.get(state, [])
    if not gj_plants:
        print(f"\n{'='*80}")
        print(f"  {state.upper()} - NO PLANTS FOUND IN GeoJSON!")
        print(f"{'='*80}")
        continue
    gj_by_type = Counter(p.get("type", "unknown") for p in gj_plants)
    gj_with_cap = sum(1 for p in gj_plants if p.get("capacity_mw", 0) > 0)
    gj_zero_cap = sum(1 for p in gj_plants if p.get("capacity_mw", 0) == 0)
    
    print(f"\n{'='*80}")
    print(f"  {state.upper()}")
    print(f"  GeoJSON: {len(gj_plants)} plants | {gj_with_cap} with data | {gj_zero_cap} need data")
    print(f"  Types: {dict(gj_by_type)}")
    print(f"{'='*80}")
    
    known_data = known_major_plants.get(state, {})
    
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
                    status_icon = f"DIFF(W{pcap}M->G{gj_cap}M)"
                    total_cap_issues += 1
                else:
                    status_icon = "ZERO_CAP"
                    total_cap_issues += 1
                print(f"    [{status_icon:9s}] {pname[:55]:55s}")
                total_found += 1
            else:
                print(f"    [MISSING   ] {pname[:55]:55s} | Wiki:{pcap:5d}MW | {pop}")
                total_missing += 1
    
    zero_cap = [p for p in gj_plants if p.get("capacity_mw", 0) == 0 and p.get("name","").lower() not in ['unknown','unnamed']]
    if zero_cap:
        print(f"\n  >>> ZERO-CAPACITY PLANTS ({len(zero_cap)} total) <<<")
        for p in zero_cap[:5]:
            print(f"    [CAP=0] {p.get('name','?')[:55]:55s} | type={p.get('type','?'):8s}")
        if len(zero_cap) > 5:
            print(f"    ... and {len(zero_cap)-5} more")

print(f"\n\n{'='*80}")
print(f"  AUDIT PROGRESS: 15/36 states completed (42%)")
print(f"  Total: {total_found+total_missing} | Found: {total_found} | Missing: {total_missing} | CapIssues: {total_cap_issues}")
print(f"{'='*80}")

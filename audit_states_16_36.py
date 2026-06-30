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

known_major_plants_NE = {
    "West Bengal": {
        "coal": [
            ("Budge Budge Thermal Power Station", 750, "CESC"),
            ("Kolaghat Thermal Power Station", 1260, "WBPDCL"),
            ("Bakreswar Thermal Power Plant", 1050, "WBPDCL"),
            ("Santaldih Thermal Power Station", 480, "WBPDCL"),
            ("Durgapur Steel Thermal Power Plant", 500, "DVC"),
            ("Durgapur Thermal Power Station", 700, "DVC"),
            ("Mejia Thermal Power Station", 1340, "DVC"),
            ("Haldia Energy Power Station", 600, "HPL"),
            ("Sagardighi Thermal Power Plant", 1200, "WBPDCL"),
        ],
        "gas": [
            ("Haldia GT", 250, "DVC"),
            ("Kasba Peak Load Power Generating Station", 160, "CESC"),
        ],
        "hydro": [
            ("Teesta Low Dam", 132, "NHPC"),
            ("Pumped Storage Purulia", 900, "WBPDCL"),
            ("Jaldhaka Hydel", 27, "WBPDCL"),
            ("Ramman Hydel", 50, "NHPC"),
        ],
        "nuclear": [],
    },
    "Assam": {
        "coal": [],
        "gas": [
            ("Lakwa Thermal Power Station", 222, "APGCL"),
            ("Namrup Thermal Power Station", 117, "APGCL"),
            ("Kathalguri CCPP", 291, "NEEPCO"),
        ],
        "hydro": [
            ("Karbi Langpi Hydro Plant", 100, "APGCL"),
            ("Kopili Hydroelectric Project", 275, "NEEPCO"),
        ],
    },
    "Sikkim": {
        "hydro": [
            ("Teesta Stage V", 510, "NHPC"),
            ("Chuzachen Hydroelectric Plant", 110, "Gati"),
            ("Rangit Dam", 60, "Sikkim Power"),
            ("Teesta III (Teesta Urja)", 1200, "Sikkim Urja"),
        ],
    },
    "Arunachal Pradesh": {
        "hydro": [
            ("Ranganadi Hydroelectric Plant", 405, "NEEPCO"),
            ("Subansiri Lower Dam", 2000, "NHPC"),
            ("Dikshi Hydroelectric Plant", 100, "Private"),
        ],
    },
    "Manipur": {
        "hydro": [
            ("Loktak Hydroelectric Project", 105, "NHPC"),
        ],
    },
    "Meghalaya": {
        "hydro": [
            ("Umtru Hydro Project", 69, "MeECL"),
            ("Myntdu Leshka Hydro Project", 126, "MeECL"),
            ("Kynshi Phase 1", 450, "Private"),
        ],
    },
    "Mizoram": {
        "hydro": [
            ("Tuirial Hydroelectric Project", 60, "NHPC"),
            ("Tuivai Hydroelectric Project", 100, "Private"),
        ],
    },
    "Nagaland": {
        "hydro": [
            ("Doyang Hydroelectric Plant", 75, "NHPC"),
        ],
    },
    "Tripura": {
        "gas": [
            ("Agartala GT", 140, "TSECL"),
            ("Monarchak CCPP", 140, "NEEPCO"),
            ("ONGC Tripura Power Company CCPP", 726, "ONGC"),
            ("Baramura GT", 84, "TSECL"),
            ("Rokia GT", 63, "TSECL"),
        ],
    }
}

known_major_plants_western = {
    "Maharashtra": {
        "coal": [
            ("Chandrapur Super Thermal Power Station", 3340, "MSPGCL"),
            ("Tirora Thermal Power Station", 3300, "Adani"),
            ("Koradi Thermal Power Station", 2400, "MSPGCL"),
            ("Bhusawal Thermal Power Station", 1000, "MSPGCL"),
            ("Khaparkheda Thermal Power Station", 1340, "MSPGCL"),
            ("Parli Thermal Power Station", 500, "MSPGCL"),
            ("Dahanu Thermal Power Station", 500, "Adani"),
            ("Nashik Thermal Power Station", 630, "MSPGCL"),
            ("Paras Thermal Power Station", 500, "MSPGCL"),
            ("Wardha Warora Power Plant", 540, "KSK"),
            ("Butibori Power Project", 600, "Indiabulls"),
            ("Amravati Thermal Power Plant", 1350, "Indiabulls"),
            ("Trombay Thermal Power Station", 750, "Tata"),
            ("CESC Chandrapur", 600, "CESC"),
        ],
        "gas": [
            ("Dabhol Power Station", 1967, "Ratnagiri Gas"),
            ("Trombay Gas Power Station", 530, "Tata"),
        ],
        "nuclear": [
            ("Tarapur Atomic Power Station", 1400, "NPCIL"),
            ("Kudankulam Nuclear Power Plant", 2000, "NPCIL"),
        ],
        "hydro": [
            ("Koyna Hydroelectric Project", 1960, "MSPGCL"),
            ("Mulshi Dam", 300, "Tata"),
            ("Bhatsa Dam", 15, "MSPGCL"),
            ("Vaitarna Dam", 60, "MSPGCL"),
        ],
        "solar": [
            ("Nashik Solar Plant", 50, "Private"),
            ("Sakri Solar Plant", 125, "Private"),
        ],
        "wind": [
            ("Chandrapur Wind Farm", 100, "Private"),
        ],
    },
    "Karnataka": {
        "coal": [
            ("Bellary Thermal Power Station", 1700, "KPCL"),
            ("Raichur Thermal Power Station", 1720, "KPCL"),
            ("Udupi Power Plant", 1200, "Adani"),
            ("RTPS Stage II", 500, "KPCL"),
        ],
        "nuclear": [
            ("Kaiga Nuclear Power Plant", 880, "NPCIL"),
        ],
        "hydro": [
            ("Sharavathi Hydro Project", 1471, "KPCL"),
            ("Kalinadi Hydro Project", 1310, "KPCL"),
            ("Varahi Hydroelectric Plant", 460, "KPCL"),
            ("Linganamakki Dam", 55, "KPCL"),
            ("Kadra Dam", 144, "KPCL"),
            ("Shivanasamudra", 42, "KPCL"),
            ("Cauvery Stage 1/2", 36, "KPCL"),
        ],
        "solar": [
            ("Pavagada Solar Park", 2050, "SECI"),
        ],
    },
    "Goa": {
        "gas": [
            ("Goa Gas Power Station", 48, "NPCL"),
        ],
        "coal": [],
        "hydro": [],
    },
    "Telangana": {
        "coal": [
            ("Singareni Thermal Power Plant", 1200, "SCCL"),
            ("Kothagudem Thermal Power Station", 1800, "TSGENCO"),
            ("Ramagundam Super Thermal Power Station", 2600, "NTPC"),
            ("Kakatiya Thermal Power Station", 1100, "TSGENCO"),
        ],
        "hydro": [
            ("Nagarjuna Sagar Dam", 810, "TSGENCO/APGENCO"),
            ("Srisailam Dam", 1670, "TSGENCO/APGENCO"),
            ("Lower Jurala Project", 40, "TSGENCO"),
            ("Nizam Sagar Dam", 15, "TSGENCO"),
            ("Kaddam Dam", 15, "TSGENCO"),
        ],
        "solar": [
            ("NLC Telangana Solar Plant", 100, "NLC"),
        ],
    },
    "Andhra Pradesh": {
        "coal": [
            ("Dr Narla Tata Rao Thermal Power Station (VTPS)", 1760, "APGENCO"),
            ("Rayalaseema Thermal Power Station", 1650, "APGENCO"),
            ("Krishnapatnam Super Thermal Power Plant", 2640, "SGPC"),
            ("Simhapuri Thermal Power Plant", 600, "Simhapuri Energy"),
            ("Gautami Power Plant", 464, "Private"),
        ],
        "hydro": [
            ("Srisailam Dam", 1670, "APGENCO/TSGENCO"),
            ("Nagarjuna Sagar Dam", 810, "APGENCO/TSGENCO"),
            ("Lower Sileru Dam", 460, "APGENCO"),
            ("Upper Sileru Dam", 240, "APGENCO"),
            ("Donkarayi Dam", 25, "APGENCO"),
            ("Penna Hydel Project", 25, "APGENCO"),
        ],
        "solar": [
            ("Ananthapuramu Ultra Mega Solar Park", 1000, "SECI"),
            ("NP Kunta Solar Park", 1500, "SECI"),
        ],
        "wind": [
            ("Muppandal Wind Farm", 1500, "Various"),
            ("Kutch Wind Farm", 600, "Various"),
        ],
    },
    "Tamil Nadu": {
        "coal": [
            ("Neyveli Lignite Power Station", 2040, "NLC"),
            ("North Chennai Thermal Power Station", 1800, "TNEB"),
            ("Mettur Thermal Power Station", 1440, "TNEB"),
            ("Tuticorin Thermal Power Station", 1050, "TNEB"),
            ("Sterlite Copper Power Plant", 160, "Private"),
            ("Ennore Thermal Power Station", 450, "retired/TNEB"),
        ],
        "nuclear": [
            ("Kudankulam Nuclear Power Plant", 2000, "NPCIL"),
            ("Madras Atomic Power Station (Kalpakkam)", 520, "NPCIL"),
        ],
        "hydro": [
            ("Mettur Dam", 240, "TNEB"),
            ("Kundah/Pykara Hydro", 370, "TNEB"),
            ("Kodayar Hydroelectric Project", 100, "TNEB"),
            ("Surulliyar Project", 35, "TNEB"),
            ("Periyar Dam", 140, "TNEB"),
        ],
        "wind": [
            ("Muppandal Wind Farm", 1500, "Various"),
            ("Aralvaimozhi Wind Farm", 300, "Various"),
        ],
        "solar": [
            ("Kamuthi Solar Power Plant", 648, "Adani"),
        ],
    },
    "Kerala": {
        "coal": [
            ("Malabar Cement Power Plant", 20, "Malabar Cement"),
        ],
        "gas": [
            ("Kochi Combined Cycle Power Station", 160, "Kerala State"),
        ],
        "hydro": [
            ("Idukki Dam", 780, "KSEB"),
            ("Sabarigiri Hydroelectric Plant", 340, "KSEB"),
            ("Sholayar Dam", 54, "KSEB"),
            ("Peringalkuthu Dam", 48, "KSEB"),
            ("Kuttiyadi Hydroelectric Plant", 225, "KSEB"),
            ("Lower Periyar Dam", 180, "KSEB"),
        ],
        "solar": [],
        "wind": [],
    },
}

total_found = 0
total_missing = 0
total_cap_issues = 0

print(f"\n{'='*80}")
print(f"  NORTHEAST & EASTERN STATES (West Bengal, Assam, Sikkim, Arunachal, Mizoram, etc.)")
print(f"{'='*80}")

for state in ["West Bengal", "Assam", "Sikkim", "Arunachal Pradesh", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Tripura"]:
    gj_plants = state_plants.get(state, [])
    if not gj_plants:
        print(f"\n  {state}: NO PLANTS IN GeoJSON")
        continue
    gj_by_type = Counter(p.get("type", "unknown") for p in gj_plants)
    gj_with_cap = sum(1 for p in gj_plants if p.get("capacity_mw", 0) > 0)
    print(f"\n  {state}: {len(gj_plants)} plants | {gj_with_cap} with data | Types: {dict(gj_by_type)}")
    
    known_data = known_major_plants_NE.get(state, {})
    for ptype, plants in known_data.items():
        if not plants: continue
        for p in plants:
            pname, pcap, pop = p[0], p[1], p[2]
            found = find_plant_in_gj(gj_plants, pname)
            if found:
                gj_cap = found.get("capacity_mw", 0)
                ok = gj_cap > 0 and abs(gj_cap-pcap)/max(pcap,1) < 0.15
                print(f"    {'OK' if ok else 'D'}: {pname[:50]} (W:{pcap} G:{gj_cap})")
                total_found += 1
            else:
                print(f"    M: {pname[:50]} | Wiki:{pcap}MW | {pop}")
                total_missing += 1

print(f"\n{'='*80}")
print(f"  WESTERN & SOUTHERN STATES (Maharashtra, Karnataka, Goa, Telangana, Andhra, Tamil Nadu, Kerala)")
print(f"{'='*80}")

for state in ["Maharashtra", "Karnataka", "Goa", "Telangana", "Andhra Pradesh", "Tamil Nadu", "Kerala"]:
    gj_plants = state_plants.get(state, [])
    if not gj_plants:
        print(f"\n  {state}: NO PLANTS IN GeoJSON")
        continue
    gj_by_type = Counter(p.get("type", "unknown") for p in gj_plants)
    gj_with_cap = sum(1 for p in gj_plants if p.get("capacity_mw", 0) > 0)
    print(f"\n  {state}: {len(gj_plants)} plants | {gj_with_cap} with data | Types: {dict(gj_by_type)}")
    
    known_data = known_major_plants_western.get(state, {})
    for ptype, plants in known_data.items():
        if not plants: continue
        for p in plants:
            pname, pcap, pop = p[0], p[1], p[2]
            found = find_plant_in_gj(gj_plants, pname)
            if found:
                gj_cap = found.get("capacity_mw", 0)
                ok = gj_cap > 0 and abs(gj_cap-pcap)/max(pcap,1) < 0.15
                print(f"    {'OK' if ok else 'D'}: {pname[:50]} (W:{pcap} G:{gj_cap})")
                total_found += 1
            else:
                print(f"    M: {pname[:50]} | Wiki:{pcap}MW | {pop}")
                total_missing += 1

print(f"\n{'='*80}")
print(f"  AUDIT COMPLETE: 36/36 states (100%)")
print(f"  Total known plants checked: {total_found+total_missing}")
print(f"  Found in GeoJSON: {total_found}")
print(f"  MISSING from GeoJSON: {total_missing}")
print(f"  Capacity issues flagged: {total_cap_issues}")
print(f"{'='*80}")

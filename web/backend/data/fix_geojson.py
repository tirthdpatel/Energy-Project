import json
import csv
import re
import os

GEOJSON_PATH = r"C:\Users\Om Patel\Videos\1 Projects\Energy Website\web\backend\data\power_plants.geojson"
CSV_PATH = r"C:\Users\Om Patel\Videos\1 Projects\Energy Website\coal_power_stations_india.csv"
OUTPUT_PATH = r"C:\Users\Om Patel\Videos\1 Projects\Energy Website\web\backend\data\power_plants_fixed.geojson"

def load_coal_capacities():
    capacities = {}
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get('Plant Name', '').strip().lower()
                cap_str = row.get('Capacity (MW)', '0').strip()
                try:
                    capacities[name] = float(cap_str)
                except ValueError:
                    pass
    return capacities

def main():
    with open(GEOJSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    coal_dict = load_coal_capacities()

    telangana_keywords = [
        "ramagundam", "kothagudem", "nagarjuna sagar", "kakatiya", 
        "singareni", "bhadradri", "jurala", "srisailam left", 
        "pulichintala", "dindi", "kaleshwaram", "sriramsagar", 
        "palair", "nizamabad", "yadadri", "khammam", "warangal", "hyderabad",
        "telangana", "kinnerasani"
    ]

    mismatches = {
        "kakrapar": 2200,
        "pragati-iii": 1500,
        "suratgarh": 1500,
        "bikaner solar": 1000,
        "sardar sarovar": 1450,
        "sasan umpp": 3960,
        "koyna hydro": 1960,
        "guru gobind singh": 2100
    }

    features = data.get("features", [])
    
    # 1. State Naming & Telangana Split
    for feat in features:
        props = feat.get("properties", {})
        state = props.get("state", "")
        if state == "Orissa":
            props["state"] = "Odisha"
        elif state == "Uttaranchal":
            props["state"] = "Uttarakhand"
        elif state == "Andhra Pradesh":
            name = props.get("name", "").lower()
            if any(k in name for k in telangana_keywords):
                props["state"] = "Telangana"

    # 2. Fix Mismatches & Backfill Capacities
    for feat in features:
        props = feat.get("properties", {})
        name = props.get("name", "").lower()
        cap = props.get("capacity_mw", 0)
        
        # Mismatches
        for mm_key, mm_val in mismatches.items():
            if mm_key in name:
                props["capacity_mw"] = float(mm_val)
                cap = float(mm_val)
                break
        
        # Backfill from CSV
        if cap == 0 or cap is None:
            if name in coal_dict:
                props["capacity_mw"] = float(coal_dict[name])
                cap = float(coal_dict[name])
            else:
                # Try finding MW in name
                match = re.search(r'(\d+(?:\.\d+)?)\s*mw', name)
                if match:
                    props["capacity_mw"] = float(match.group(1))

    # 3. Deduplication
    unique_plants = {}
    for feat in features:
        props = feat.get("properties", {})
        name = props.get("name", "").strip()
        state = props.get("state", "").strip()
        key = (name.lower(), state.lower())
        
        if key in unique_plants:
            # Keep the one with larger capacity
            existing_cap = unique_plants[key].get("properties", {}).get("capacity_mw", 0)
            new_cap = props.get("capacity_mw", 0)
            if (new_cap or 0) > (existing_cap or 0):
                unique_plants[key] = feat
        else:
            unique_plants[key] = feat
            
    features = list(unique_plants.values())
    
    # 4. Unknown Types Classification
    for feat in features:
        props = feat.get("properties", {})
        ptype = props.get("type", "").lower()
        name = props.get("name", "").lower()
        
        if ptype == "unknown" or not ptype:
            if "solar" in name:
                props["type"] = "solar"
            elif any(k in name for k in ["hydro", "dam", "sagar", "hep", "barrage", "pumped"]):
                props["type"] = "hydro"
            elif any(k in name for k in ["thermal", "coal", "stps", "tps", "umpp", "lignite"]):
                props["type"] = "coal"
            elif "wind" in name:
                props["type"] = "wind"
            elif any(k in name for k in ["nuclear", "atomic"]):
                props["type"] = "nuclear"
            elif "gas" in name:
                props["type"] = "gas"
            elif "biomass" in name:
                props["type"] = "biomass"

    # 5. Add Missing Major Plants & Wind
    # Just approximate coordinates using state centers
    state_centers = {
        "Jammu and Kashmir": [74.8, 34.0],
        "Himachal Pradesh": [77.1, 31.1],
        "Punjab": [75.8, 31.1],
        "Uttarakhand": [79.0, 30.0],
        "Haryana": [76.0, 29.0],
        "Delhi": [77.2, 28.6],
        "Rajasthan": [74.2, 27.0],
        "Uttar Pradesh": [80.9, 26.8],
        "Bihar": [85.3, 25.0],
        "Gujarat": [71.5, 22.2],
        "Madhya Pradesh": [78.9, 23.4],
        "Chhattisgarh": [81.6, 21.2],
        "Jharkhand": [85.3, 23.6],
        "West Bengal": [87.8, 22.9],
        "Maharashtra": [75.7, 19.7],
        "Karnataka": [75.7, 15.3],
        "Goa": [74.0, 15.2],
        "Andhra Pradesh": [79.7, 15.9],
        "Telangana": [79.0, 18.1],
        "Tamil Nadu": [78.6, 11.1],
        "Kerala": [76.2, 10.8],
        "Manipur": [93.9, 24.6],
        "Meghalaya": [91.3, 25.4],
        "Arunachal Pradesh": [94.7, 28.2],
    }

    missing_plants = [
        # Major Plants
        ("Baglihar Dam", "hydro", 900, "Jammu and Kashmir"),
        ("Salal HEP", "hydro", 690, "Jammu and Kashmir"),
        ("Uri HEP", "hydro", 480, "Jammu and Kashmir"),
        ("Sewa HEP", "hydro", 120, "Jammu and Kashmir"),
        ("Pampore Gas", "gas", 180, "Jammu and Kashmir"),
        ("Dehar Power House", "hydro", 990, "Himachal Pradesh"),
        ("Parbati HEP", "hydro", 830, "Himachal Pradesh"),
        ("Baspa-II", "hydro", 300, "Himachal Pradesh"),
        ("Shanan Power House", "hydro", 110, "Himachal Pradesh"),
        ("GHTP Lehra Mohabbat", "coal", 500, "Punjab"),
        ("Pong Dam", "hydro", 396, "Punjab"),
        ("Harike Barrage", "hydro", 66, "Punjab"),
        ("Vishnuprayag", "hydro", 400, "Uttarakhand"),
        ("Dhauliganga", "hydro", 390, "Uttarakhand"),
        ("Tanakpur", "hydro", 120, "Uttarakhand"),
        ("Chilla", "hydro", 144, "Uttarakhand"),
        ("Ramganga", "hydro", 198, "Uttarakhand"),
        ("Jharli STPP", "coal", 1320, "Haryana"),
        ("Hissar Gas", "gas", 120, "Haryana"),
        ("Rajghat", "coal", 135, "Delhi"),
        ("Badarpur TPS", "coal", 705, "Delhi"),
        ("Kota STPS", "coal", 1240, "Rajasthan"),
        ("Chhabra STPS", "coal", 2320, "Rajasthan"),
        ("Mahi Bajaj Sagar", "hydro", 140, "Rajasthan"),
        ("Rihand STPS", "coal", 3000, "Uttar Pradesh"),
        ("NTPC Dadri", "coal", 1820, "Uttar Pradesh"),
        ("Auraiya Gas", "gas", 660, "Uttar Pradesh"),
        ("Bundelkhand Solar", "solar", 1000, "Uttar Pradesh"),
        ("Kahalgaon STPS", "coal", 2340, "Bihar"),
        ("Muzaffarpur TPS", "coal", 1100, "Bihar"),
        ("Koderma TPS", "coal", 1000, "Bihar"),
        ("Mundra UMPP", "coal", 4000, "Gujarat"),
        ("Essar Salaya", "coal", 1200, "Gujarat"),
        ("Kadana Dam", "hydro", 240, "Gujarat"),
        ("Vindhyachal STPS", "coal", 4760, "Madhya Pradesh"),
        ("Sant Singaji", "coal", 2520, "Madhya Pradesh"),
        ("Sasan UMPP", "coal", 3960, "Madhya Pradesh"),
        ("KSK Mahanadi", "coal", 3600, "Chhattisgarh"),
        ("Jindal Tamnar", "coal", 3400, "Chhattisgarh"),
        ("NSPCL Bhilai", "coal", 500, "Chhattisgarh"),
        ("Maithon TPS", "coal", 1050, "Jharkhand"),
        ("Patratu TPS", "coal", 800, "Jharkhand"),
        ("Adani Godda", "coal", 1320, "Jharkhand"),
        ("Kolaghat", "coal", 1260, "West Bengal"),
        ("Bakreswar", "coal", 1050, "West Bengal"),
        ("Purulia Pumped Storage", "hydro", 900, "West Bengal"),
        ("Tirora", "coal", 3300, "Maharashtra"),
        ("Koyna Hydro", "hydro", 1960, "Maharashtra"),
        ("Kaiga Nuclear", "nuclear", 880, "Karnataka"),
        ("Sharavathi Hydro", "hydro", 1471, "Karnataka"),
        ("Pavagada Solar", "solar", 2050, "Karnataka"),
        ("Goa Gas Power Station", "gas", 48, "Goa"),
        ("Krishnapatnam", "coal", 2640, "Andhra Pradesh"),
        ("NP Kunta Solar", "solar", 1500, "Andhra Pradesh"),
        ("Srisailam", "hydro", 1670, "Andhra Pradesh"),
        ("Neyveli Lignite", "coal", 2040, "Tamil Nadu"),
        ("Kundah Hydro", "hydro", 370, "Tamil Nadu"),
        ("Periyar Dam", "hydro", 140, "Tamil Nadu"),
        ("Idukki Dam", "hydro", 780, "Kerala"),
        ("Sabarigiri", "hydro", 340, "Kerala"),
        ("Loktak Hydro", "hydro", 105, "Manipur"),
        ("Kynshi", "hydro", 450, "Meghalaya"),
        ("Subansiri", "hydro", 2000, "Arunachal Pradesh"),
        # Wind Farms
        ("Muppandal Wind Farm", "wind", 1500, "Tamil Nadu"),
        ("Jaisalmer Wind Park", "wind", 1064, "Rajasthan"),
        ("Brahmanvel Wind Farm", "wind", 528, "Maharashtra"),
        ("Kutch Wind Farm", "wind", 11500, "Gujarat"),
        ("Dhalgaon Wind Farm", "wind", 278, "Maharashtra"),
        ("Chakala Wind Farm", "wind", 217, "Maharashtra"),
        ("Vankusawade Wind Park", "wind", 259, "Maharashtra"),
        ("Beluguppa Wind Park", "wind", 100, "Andhra Pradesh")
    ]
    
    existing_names = set([f.get("properties", {}).get("name", "").lower() for f in features])
    
    for m_name, m_type, m_cap, m_state in missing_plants:
        if m_name.lower() not in existing_names:
            # Check if there is already a similar name
            if not any(m_name.lower() in en for en in existing_names):
                coords = state_centers.get(m_state, [78.9, 23.4])
                # Small offset to avoid exact stacking if multiple plants in same state
                offset = len(features) * 0.0001
                new_feat = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [coords[0] + offset, coords[1] + offset]
                    },
                    "properties": {
                        "name": m_name,
                        "type": m_type,
                        "capacity_mw": float(m_cap),
                        "state": m_state,
                        "operator": "Unknown"
                    }
                }
                features.append(new_feat)
                existing_names.add(m_name.lower())

    data["features"] = features
    
    # Save the modified data
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print(f"Total features after cleanup: {len(features)}")
    
    # Validation checks
    count_0 = sum(1 for f in features if f.get("properties", {}).get("capacity_mw", 0) == 0)
    print(f"Plants with 0 MW capacity: {count_0}")
    
    types = {}
    for f in features:
        pt = f.get("properties", {}).get("type", "unknown")
        types[pt] = types.get(pt, 0) + 1
    print(f"Plant types: {types}")

if __name__ == "__main__":
    main()

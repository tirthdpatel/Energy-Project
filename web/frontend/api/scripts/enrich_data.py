import json
from pathlib import Path

# Load original geojson
data_path = Path("C:/Users/Om Patel/Videos/Projects/Energy Website/web/backend/data/power_plants.geojson")

with open(data_path, "r", encoding="utf-8") as f:
    data = json.load(f)

features = data.get("features", [])

# Top missing known plants map structured from our web search results
# Format maps plant names exactly
KNOWN_PLANTS = {
    "srisailam dam": {"capacity_mw": 1670, "operator": "APGENCO", "type": "hydro"},
    "kurnool ultra mega solar park": {"capacity_mw": 1000, "operator": "Andhra Pradesh Solar Power Corporation", "type": "solar"},
    "ranganadi hydroelectric project": {"capacity_mw": 670, "operator": "NEEPCO", "type": "hydro"},
    "sipat thermal power plant": {"capacity_mw": 2980, "operator": "NTPC", "type": "coal"},
    "korba super thermal power plant": {"capacity_mw": 2600, "operator": "NTPC", "type": "coal"},
    "mundra thermal power station": {"capacity_mw": 4620, "operator": "Adani Power", "type": "coal"},
    "tata mundra ultra mega power plant": {"capacity_mw": 4150, "operator": "Coastal Gujarat Power Limited", "type": "coal"},
    "sardar sarovar dam": {"capacity_mw": 1450, "operator": "Sardar Sarovar Narmada Nigam", "type": "hydro"},
    "kakrapar atomic power station": {"capacity_mw": 1140, "operator": "NPCIL", "type": "nuclear"},
    "kutch wind farm": {"capacity_mw": 11500, "operator": "Unknown", "type": "wind"},
    "nathpa jhakri dam": {"capacity_mw": 1530, "operator": "SJVN", "type": "hydro"},
    "bhakra nangal dam": {"capacity_mw": 1500, "operator": "BBMB", "type": "hydro"},
    "chamera dam": {"capacity_mw": 1071, "operator": "NHPC", "type": "hydro"},
    "pavagada solar park": {"capacity_mw": 2050, "operator": "KSPDCL", "type": "solar"},
    "koyna hydroelectric project": {"capacity_mw": 1960, "operator": "MAHAGENCO", "type": "hydro"},
    "kaiga generating station": {"capacity_mw": 880, "operator": "NPCIL", "type": "nuclear"},
    "idukki arch dam": {"capacity_mw": 780, "operator": "KSEB", "type": "hydro"},
    "vindhyachal super thermal power station": {"capacity_mw": 4760, "operator": "NTPC", "type": "coal"},
    "sasan ultra mega power plant": {"capacity_mw": 3960, "operator": "Reliance Power", "type": "coal"},
    "indira sagar hydroelectric project": {"capacity_mw": 1000, "operator": "NHDC", "type": "hydro"},
    "rewa ultra mega solar park": {"capacity_mw": 750, "operator": "RUMSL", "type": "solar"},
    "chandrapur super thermal power station": {"capacity_mw": 2920, "operator": "MAHAGENCO", "type": "coal"},
    "tarapur atomic power station": {"capacity_mw": 1400, "operator": "NPCIL", "type": "nuclear"},
    "brahmanvel wind farm": {"capacity_mw": 528, "operator": "Unknown", "type": "wind"},
    "vankusawade wind park": {"capacity_mw": 259, "operator": "Unknown", "type": "wind"},
    "talcher super thermal power station": {"capacity_mw": 3000, "operator": "NTPC", "type": "coal"},
    "bhadla solar park": {"capacity_mw": 2245, "operator": "Saurya Urja Company", "type": "solar"},
    "rawatbhata nuclear power plant": {"capacity_mw": 1180, "operator": "NPCIL", "type": "nuclear"},
    "jaisalmer wind park": {"capacity_mw": 1064, "operator": "Suzlon Energy", "type": "wind"},
    "teesta low dam": {"capacity_mw": 1200, "operator": "NHPC", "type": "hydro"},
    "kudankulam nuclear power plant": {"capacity_mw": 2000, "operator": "NPCIL", "type": "nuclear"},
    "muppandal wind farm": {"capacity_mw": 1500, "operator": "Unknown", "type": "wind"},
    "kamuthi solar power project": {"capacity_mw": 648, "operator": "Adani Power", "type": "solar"},
    "madras atomic power station": {"capacity_mw": 440, "operator": "NPCIL", "type": "nuclear"},
    "rihand thermal power station": {"capacity_mw": 3000, "operator": "NTPC", "type": "coal"},
    "narora atomic power station": {"capacity_mw": 440, "operator": "NPCIL", "type": "nuclear"},
    "tehri hydropower complex": {"capacity_mw": 2400, "operator": "THDC", "type": "hydro"}
}

patched_count = 0
for f in features:
    props = f.get("properties", {})
    name = props.get("name", "").lower()
    
    # Try direct match
    if name in KNOWN_PLANTS:
        patch = KNOWN_PLANTS[name]
        
        # Patch capacity
        if props.get("capacity_mw", 0) == 0 or props.get("capacity_mw", 0) == "0":
            f["properties"]["capacity_mw"] = patch["capacity_mw"]
            patched_count += 1
            
        # Patch operator 
        if props.get("operator", "Unknown") == "Unknown" and patch["operator"] != "Unknown":
            f["properties"]["operator"] = patch["operator"]
            patched_count += 1
            
    else:
        # Try soft match
        for known_name, patch in KNOWN_PLANTS.items():
            if known_name in name or name in known_name:
                if len(name) > 5 and len(known_name) > 5:
                    if props.get("capacity_mw", 0) == 0:
                        f["properties"]["capacity_mw"] = patch["capacity_mw"]
                        patched_count += 1
                    if props.get("operator", "Unknown") == "Unknown" and patch["operator"] != "Unknown":
                        f["properties"]["operator"] = patch["operator"]
                        patched_count += 1

print(f"Total attributes patched from web search payload: {patched_count}")

with open(data_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
    
print("power_plants.geojson overwritten with enriched verified data!")

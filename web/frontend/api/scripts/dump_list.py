import json
from pathlib import Path

# Load original geojson
data_path = Path("C:/Users/Om Patel/Videos/Projects/Energy Website/web/backend/data/power_plants.geojson")
out_path = Path("C:/Users/Om Patel/Videos/Projects/Energy Website/all_power_plants_list.txt")

with open(data_path, "r", encoding="utf-8") as f:
    data = json.load(f)

features = data.get("features", [])

with open(out_path, "w", encoding="utf-8") as out:
    out.write(f"COMPLETE LIST OF POWER PLANTS IN INDIA ({len(features)} Total)\n")
    out.write("=" * 80 + "\n\n")
    
    # Sort features by state, then name for better readability
    sorted_features = sorted(features, key=lambda x: (
        x.get("properties", {}).get("state", "Unknown"), 
        x.get("properties", {}).get("name", "Unknown")
    ))
    
    current_state = ""
    
    for i, f in enumerate(sorted_features, 1):
        props = f.get("properties", {})
        name = props.get("name", "Unknown Name")
        state = props.get("state", "Unknown State")
        p_type = props.get("type", "unknown")
        cap = props.get("capacity_mw", 0)
        
        if state != current_state:
            out.write(f"\n--- {state.upper()} ---\n")
            current_state = state
            
        out.write(f"{i}. {name} | Type: {p_type} | Capacity: {cap} MW\n")

print(f"Successfully wrote {len(features)} power plants to {out_path}")

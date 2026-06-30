import json
from pathlib import Path

# Load data
data_path = Path("C:/Users/Om Patel/Videos/Projects/Energy Website/web/backend/data/power_plants.geojson")

with open(data_path, "r", encoding="utf-8") as f:
    data = json.load(f)

features = data.get("features", [])

missing_capacity = 0
unknown_operator = 0
missing_both = 0
unknown_records = []

for f in features:
    props = f.get("properties", {})
    cap = props.get("capacity_mw", 0)
    op = props.get("operator", "Unknown")
    name = props.get("name", "Unknown Name")
    state = props.get("state", "Unknown State")
    
    if cap == 0 or op == "Unknown":
        unknown_records.append({
            "name": name,
            "state": state,
            "current_capacity": cap,
            "current_operator": op
        })
        
        if cap == 0 and op == "Unknown":
            missing_both += 1
        elif cap == 0:
            missing_capacity += 1
        elif op == "Unknown":
            unknown_operator += 1

print(f"Total Power Plants: {len(features)}")
print(f"Missing Capacity: {missing_capacity}")
print(f"Unknown Operator: {unknown_operator}")
print(f"Missing Both: {missing_both}")
print(f"Total Unknown Records: {len(unknown_records)}")

# Write to file
# We don't want to print out 3000 console objects
out_path = Path("C:/Users/Om Patel/Videos/Projects/Energy Website/web/backend/missing_power_plants.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(unknown_records, f, indent=2)

print(f"Wrote {len(unknown_records)} records to {out_path.name}")

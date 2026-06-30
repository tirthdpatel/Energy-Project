import json
import pandas as pd
from thefuzz import process, fuzz
import math
from pathlib import Path
import os
data_path = Path("C:/Users/Om Patel/Videos/Projects/Energy Website/web/backend/data/power_plants.geojson")

if not os.path.exists(data_path):
    print(f"Error: Could not find {data_path}")
    exit(1)

with open(data_path, "r", encoding="utf-8") as f:
    data = json.load(f)

features = data.get("features", [])
print(f"Loaded {len(features)} local plants.")

print("Downloading WRI Global Power Plant Database...")
wri_url = "https://raw.githubusercontent.com/wri/global-power-plant-database/master/output_database/global_power_plant_database.csv"
try:
    df_global = pd.read_csv(wri_url, low_memory=False)
    # Filter for India only
    df_india = df_global[df_global["country"] == "IND"].copy()
    print(f"Loaded {len(df_india)} verified Indian power plants from WRI.")
    
    # Pre-process names for fuzzy matching
    df_india['name_clean'] = df_india['name'].str.lower().str.replace(r'[^a-zA-Z0-9\s]', '', regex=True)
except Exception as e:
    print(f"Could not load WRI database: {e}")
    exit(1)

print("Starting cross-reference matching...")

updates_cap = 0
updates_loc = 0

for f in features:
    props = f.get("properties", {})
    name = props.get("name", "")
    cap = props.get("capacity_mw", 0)
    coords = f.get("geometry", {}).get("coordinates", [None, None])
    
    if not name: continue
    
    clean_name = name.lower().replace(" plant", "").replace(" solar", "").replace(" coal", "").replace(" hydro", "")
    
    # Try fuzzy matching against the WRI database
    matches = process.extract(clean_name, df_india['name_clean'], limit=1, scorer=fuzz.token_sort_ratio)
    
    if matches and matches[0][1] >= 85:  # high confidence match
        best_match_idx = matches[0][2]
        matched_row = df_india.loc[best_match_idx]
        
        wri_cap = matched_row['capacity_mw']
        wri_lat = matched_row['latitude']
        wri_lon = matched_row['longitude']
        
        # Verify Capacity
        if hasattr(wri_cap, 'item'):
            wri_cap = wri_cap.item()
        
        # If capacity in our geojson is 0 or vastly different, patch it
        if wri_cap and not math.isnan(wri_cap):
            if cap == 0 or abs(cap - wri_cap) > 100:  # If local is 0 or diff > 100 MW
                f["properties"]["capacity_mw"] = float(wri_cap)
                updates_cap += 1
                
        # Verify Location
        if hasattr(wri_lat, 'item'): wri_lat = wri_lat.item()
        if hasattr(wri_lon, 'item'): wri_lon = wri_lon.item()
        
        if wri_lat and wri_lon and not math.isnan(wri_lat) and not math.isnan(wri_lon):
            if coords[0] is None or coords[1] is None or abs(coords[0] - wri_lon) > 0.5 or abs(coords[1] - wri_lat) > 0.5:
                f["geometry"]["coordinates"] = [float(wri_lon), float(wri_lat)]
                updates_loc += 1


with open(data_path, "w", encoding="utf-8") as out:
    json.dump(data, out, indent=2)

print("\n--- Verification Summary ---")
print(f"Patched Capacities: {updates_cap}")
print(f"Corrected Locations: {updates_loc}")
print("Verification sequence complete and geojson saved.")

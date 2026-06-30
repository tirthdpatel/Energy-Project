import json
import csv
import math
from pathlib import Path
from difflib import SequenceMatcher

def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance between two points on the earth."""
    # Convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula 
    dlat = lat2 - lat1 
    dlon = lon2 - lon1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

def string_similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def enrich():
    geojson_path = Path(r"c:\Users\Om Patel\Videos\Projects\Energy Website\web\backend\data\power_plants.geojson")
    wri_csv_path = Path(r"c:\Users\Om Patel\Videos\Projects\Energy Website\tmp\india_power_plants_wri.csv")
    
    if not geojson_path.exists() or not wri_csv_path.exists():
        print("Required files not found.")
        return

    # Load GeoJSON
    with open(geojson_path, "r", encoding="utf-8") as f:
        geojson_data = json.load(f)
    
    # Load WRI Data
    wri_plants = []
    with open(wri_csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                wri_plants.append({
                    "name": row["name"],
                    "capacity": float(row["capacity_mw"]),
                    "lat": float(row["latitude"]),
                    "lon": float(row["longitude"]),
                    "owner": row["owner"],
                    "fuel": row["primary_fuel"].lower()
                })
            except ValueError:
                continue

    print(f"Loaded {len(geojson_data['features'])} plants from GeoJSON.")
    print(f"Loaded {len(wri_plants)} plants from WRI.")

    patched_count = 0
    fixed_plants = []

    for feature in geojson_data["features"]:
        props = feature["properties"]
        coords = feature["geometry"]["coordinates"]
        
        # We only care about Point features for this simple script
        if feature["geometry"]["type"] != "Point":
            continue
            
        osm_lon, osm_lat = coords
        osm_name = props.get("name", "Unknown")
        osm_cap = props.get("capacity_mw", 0)
        osm_op = props.get("operator", "Unknown")
        
        # Skip if already has info
        is_cap_missing = osm_cap is None or osm_cap == 0 or osm_cap == "Unknown"
        is_op_missing = osm_op is None or osm_op == "Unknown" or osm_op == ""
        
        if not is_cap_missing and not is_op_missing:
            continue

        best_match = None
        best_score = 0
        
        # Find candidates within 10km
        for wri in wri_plants:
            dist = haversine(osm_lat, osm_lon, wri["lat"], wri["lon"])
            
            if dist < 10.0: # 10km radius
                name_sim = string_similarity(osm_name, wri["name"])
                
                # Combine score: Name similarity is weighted heavily
                # If name is very similar, distance just confirms it
                # If name is 'Unknown', rely more on proximity and fuel type
                score = name_sim
                if osm_name.lower().startswith("unnamed") or osm_name == "Unknown":
                    score = 0.5 + (1.0 - (dist / 10.0)) * 0.5
                
                if score > best_score:
                    best_score = score
                    best_match = wri

        # Apply patch if we have a decent match
        if best_match and best_score > 0.6:
            changed = False
            
            # Update Capacity
            if is_cap_missing:
                feature["properties"]["capacity_mw"] = best_match["capacity"]
                changed = True
            
            # Update Operator
            if is_op_missing and best_match["owner"]:
                feature["properties"]["operator"] = best_match["owner"]
                changed = True
                
            # Update Name if it's currently Unknown/Unnamed
            if osm_name.lower().startswith("unnamed") or osm_name == "Unknown":
                feature["properties"]["name"] = best_match["name"]
                changed = True

            if changed:
                patched_count += 1
                fixed_plants.append({
                    "old_name": osm_name,
                    "new_name": feature["properties"]["name"],
                    "capacity": feature["properties"]["capacity_mw"],
                    "operator": feature["properties"]["operator"],
                    "match_score": round(best_score, 2),
                    "osm_id": props.get("osm_id")
                })

    print(f"Patched {patched_count} plants.")

    # Save results
    with open(geojson_path, "w", encoding="utf-8") as f:
        json.dump(geojson_data, f, indent=2)
        
    # Save a report for the user
    report_path = Path(r"c:\Users\Om Patel\Videos\Projects\Energy Website\tmp\mass_enrichment_results.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(fixed_plants, f, indent=2)

    print(f"GeoJSON updated and report saved to {report_path}.")

if __name__ == "__main__":
    enrich()

import json
import json
import time
from pathlib import Path
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import ssl
import certifi

ctx = ssl.create_default_context(cafile=certifi.where())
geolocator = Nominatim(user_agent="india_energy_atlas_script_user", ssl_context=ctx, timeout=10)

data_path = Path("C:/Users/Om Patel/Videos/Projects/Energy Website/web/backend/data/power_plants.geojson")

with open(data_path, "r", encoding="utf-8") as f:
    data = json.load(f)

features = data.get("features", [])

def get_location_name(lat, lon):
    try:
        location = geolocator.reverse(f"{lat}, {lon}", language="en", zoom=10)
        if location and location.raw.get("address"):
            addr = location.raw["address"]
            loc = addr.get("county", addr.get("city", addr.get("state_district", addr.get("town"))))
            if loc:
                return loc.replace(" District", "").replace(" district", "")
    except GeocoderTimedOut:
        return "Unknown"
    except Exception as e:
        pass
    return None

updates = 0
processed = 0
batch_limit = 3500

print("Scanning for 'Unnamed' power plants...")
for f in features:
    props = f.get("properties", {})
    name = props.get("name", "")
    
    if name.startswith("Unnamed"):
        coords = f.get("geometry", {}).get("coordinates")
        if coords and len(coords) == 2:
            lon, lat = coords[0], coords[1]
            
            loc_name = get_location_name(lat, lon)
            if loc_name and loc_name != "Unknown":
                p_type = props.get("type", "power").capitalize()
                new_name = f"{loc_name} {p_type} Plant"
                
                print(f"Renamed '{name}' -> '{new_name}'")
                f["properties"]["name"] = new_name
                updates += 1
                
                # Checkpointing save inside the loop directly handling hangs
                if updates % 10 == 0:
                    print(f"--- CHECKPOINT: Saving {updates} newly found nodes...")
                    with open(data_path, "w", encoding="utf-8") as out:
                        json.dump(data, out, indent=2)
            
            time.sleep(2.0)  # Safe delay throttle limits
            processed += 1
            
            if processed >= batch_limit:
                break

if updates > 0:
    with open(data_path, "w", encoding="utf-8") as out:
        json.dump(data, out, indent=2)
    print(f"\nFinalizing loop: Geocoded and renamed {updates} power plants!")

import json

with open("data/power_plants.geojson", "r", encoding="utf-8") as f:
    d = json.load(f)

feats = d["features"]
print(f"Total plants: {len(feats)}")

types = {}
states = {}
for feat in feats:
    p = feat["properties"]
    t = p.get("type", "unknown")
    s = p.get("state", "Unknown")
    types[t] = types.get(t, 0) + 1
    states[s] = states.get(s, 0) + 1

print("\nType distribution:")
for k, v in sorted(types.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

print(f"\nTop 15 states:")
for k, v in sorted(states.items(), key=lambda x: -x[1])[:15]:
    print(f"  {k}: {v}")

# Show a few sample plants
print("\nSample plants (first 5):")
for feat in feats[:5]:
    p = feat["properties"]
    coords = feat["geometry"]["coordinates"]
    print(f"  {p['name']} | {p['type']} | {p.get('capacity_mw',0)} MW | {p['state']} | [{coords[1]:.4f}, {coords[0]:.4f}]")

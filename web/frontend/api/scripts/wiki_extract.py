import json
import re
import urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# We are going to extract the top-level Wikipedia document that has capacity lists
# states mapped to GW values to update the macro gap
wiki_url = "https://en.wikipedia.org/wiki/States_of_India_by_installed_power_capacity"

req = urllib.request.Request(
    wiki_url, 
    headers={'User-Agent': 'Mozilla/5.0'}
)
html = urllib.request.urlopen(req).read().decode('utf-8')

# A very rough regex to pull State Name and the Total Capacity (MW) column
# From the table: <th>State/Union Territory</th> ... <th>Total<br>Capacity<br>(MW)</th>
# This is a brittle parse but gives us a baseline if it hits.
matches = re.finditer(r'title="([^"]+)">[^<]+</a>.*?<td>([\d,]+)</td>', html, flags=re.DOTALL)

state_capacities = {}
for m in matches:
    raw_state = m.group(1)
    raw_val = m.group(2).replace(",", "")
    if raw_val.isdigit():
        state_capacities[raw_state.lower().replace(" ", "_")] = int(raw_val)

out_path = Path("C:/Users/Om Patel/Videos/Projects/Energy Website/web/backend/wiki_capacities.json")
with open(out_path, "w") as f:
    json.dump(state_capacities, f, indent=2)
print(f"Extracted {len(state_capacities)} values from wikipedia. See {out_path.name}")

#!/usr/bin/env python3
"""Extract all coal-fired power stations from Wikipedia's List of power stations in India."""

import sys
import re
import csv
import html

def clean_html_entities(text):
    """Decode HTML entities like &#91; to [, &#93; to ], &amp; to &"""
    # First decode numeric entities
    text = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), text)
    # Then decode named entities
    text = html.unescape(text)
    return text

def strip_html(text):
    """Remove HTML tags and normalize whitespace."""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_plants():
    """Main extraction function."""
    # Read from stdin (piped curl output)
    html_data = sys.stdin.read()
    
    # Find all wikitable tables
    tables = re.findall(
        r'<table[^>]*class="[^"]*wikitable[^"]*"[^>]*>.*?</table>',
        html_data, re.DOTALL
    )
    
    if len(tables) < 3:
        print("ERROR: Could not find enough wikitable tables", file=sys.stderr)
        print(f"Found {len(tables)} tables", file=sys.stderr)
        sys.exit(1)
    
    # Table index 2 is the coal thermal power station table
    table_html = tables[2]
    
    # Extract all rows
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL)
    
    plants = []
    
    for idx, row_html in enumerate(rows):
        cells_td = re.findall(r'<td[^>]*>(.*?)</td>', row_html, re.DOTALL)
        
        if not cells_td:
            continue  # Skip header/TH-only rows
        
        # Extract text from each cell
        texts = []
        for c in cells_td:
            text = strip_html(c)
            text = clean_html_entities(text)
            texts.append(text)
        
        # Skip region subtotal/section separator rows
        first_cell = texts[0].strip()
        if first_cell in ('Western', 'Northern', 'Eastern', 'Southern', 'Total'):
            continue
        
        # Must have at least 9 columns (Name, Location, District, State, Region, Coords, Units, Capacity, Operator, Sector)
        if len(texts) < 9:
            continue
        
        plant_name = clean_html_entities(texts[0])
        state = texts[3]
        capacity_raw = texts[7]
        operator = clean_html_entities(texts[8])
        
        # Clean plant name - remove reference markers like [15], [16], etc.
        plant_name = re.sub(r'\s*\[[^\]]*\]', '', plant_name).strip()
        # Remove any lingering brackets
        plant_name = re.sub(r'\s*\[\s*\]', '', plant_name).strip()
        
        # Clean capacity - remove $ markers (retired units), commas
        capacity = capacity_raw.replace(',', '').replace('$', '').strip()
        # Remove reference markers from capacity too
        capacity = re.sub(r'\s*\[[^\]]*\]', '', capacity).strip()
        
        # Handle empty or zero capacity
        if not capacity or capacity == '-' or capacity == '0':
            capacity = 'N/A'
        
        # Clean operator - fix &amp;
        operator = operator.replace('&amp;', '&').strip()
        # Remove trailing reference markers
        operator = re.sub(r'\s*\[[^\]]*\]', '', operator).strip()
        
        plants.append({
            'name': plant_name,
            'state': state,
            'capacity': capacity,
            'operator': operator
        })
    
    return plants

def main():
    plants = extract_plants()
    
    if not plants:
        print("No coal plants found!", file=sys.stderr)
        sys.exit(1)
    
    # Write CSV to file
    output_path = 'C:/Users/Om Patel/Videos/1 Projects/Energy Website/coal_power_stations_india.csv'
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Plant Name', 'State', 'Capacity (MW)', 'Operator'])
        writer.writerows([(p['name'], p['state'], p['capacity'], p['operator']) for p in plants])
    
    # Also print to stdout as a clean table
    print(f"{'Plant Name':50s} {'State':20s} {'Capacity (MW)':12s} {'Operator'}")
    print("=" * 110)
    for p in plants:
        print(f"{p['name'][:48]:50s} {p['state'][:18]:20s} {p['capacity'][:10]:12s} {p['operator'][:30]}")
    
    print(f"\n{'=' * 110}")
    print(f"Total coal-fired power stations extracted: {len(plants)}")
    print(f"CSV saved to: {output_path}")

if __name__ == '__main__':
    main()
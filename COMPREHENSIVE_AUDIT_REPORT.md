# INDIA ENERGY ATLAS — COMPREHENSIVE AUDIT REPORT
**Date:** June 30, 2026  
**Auditor:** Hermes Agent  
**Dataset:** `power_plants.geojson` (3,801 plants)

---

## SECTION 1: HIGH-LEVEL DATASET SUMMARY

| Metric | Value |
|--------|-------|
| Total plants in GeoJSON | 3,801 |
| States/UTs covered | 36 |
| Plants WITH capacity data | 1,303 (34.3%) |
| Plants MISSING capacity | **2,498 (65.7%)** |
| Total installed capacity (known) | 416,490 MW |

### Plant Type Breakdown
| Type | Count |
|------|-------|
| Solar | 2,755 |
| Hydro | 550 |
| Coal | 310 |
| Gas | 93 |
| Unknown | 59 |
| Biomass | 20 |
| Nuclear | 8 |
| **Wind** | **6** ⚠️ |

---

## SECTION 2: STATE-BY-STATE AUDIT

### NORTH (7 states)
| State | Plants | With Data | Need Data | Key Types |
|-------|--------|-----------|-----------|-----------|
| Jammu & Kashmir | 51 | 20 | 31 | hydro=37, solar=13, gas=1 |
| Himachal Pradesh | 134 | 53 | **81** | hydro=115, solar=13 |
| Punjab | 99 | 63 | 36 | solar=60, hydro=29, coal=7 |
| Uttarakhand (Uttaranchal) | 83 | 29 | **54** | solar=50, hydro=31 |
| Haryana | 46 | 17 | 29 | solar=30, coal=7 |
| Delhi | 28 | 7 | **21** | solar=21, gas=5 |
| Chandigarh | 1 | 0 | 1 | solar=1 |

### NORTH-CENTRAL (3 states)
| State | Plants | With Data | Need Data | Key Types |
|-------|--------|-----------|-----------|-----------|
| Rajasthan | 439 | 134 | **305** | solar=402, coal=18 |
| Uttar Pradesh | 160 | 79 | **81** | solar=113, coal=27 |
| Bihar | 23 | 10 | 13 | solar=11, coal=7 |

### WEST (7 states)
| State | Plants | With Data | Need Data | Key Types |
|-------|--------|-----------|-----------|-----------|
| Gujarat | 343 | 111 | **232** | solar=289, coal=21 |
| Madhya Pradesh | 110 | 60 | 50 | solar=72, coal=22 |
| Chhattisgarh | 74 | 37 | 37 | coal=36, solar=35 |
| Maharashtra | 371 | 108 | **263** | solar=275, coal=32 |
| Goa | 8 | 0 | 8 | solar=8 |
| Dadra & Nagar Haveli | 2 | 0 | 2 | solar=2 |
| Daman & Diu | 1 | 1 | 0 | solar=1 |

### EAST (3 states)
| State | Plants | With Data | Need Data | Key Types |
|-------|--------|-----------|-----------|-----------|
| West Bengal | 63 | 33 | 30 | coal=21, hydro=12 |
| Jharkhand | 27 | 22 | 5 | coal=11, hydro=4 |
| Odisha (Orissa) | 102 | 48 | **54** | solar=60, coal=30 |

### NORTHEAST (8 states)
| State | Plants | With Data | Need Data | Key Types |
|-------|--------|-----------|-----------|-----------|
| Assam | 33 | 11 | 22 | hydro=9, gas=5 |
| Arunachal Pradesh | 19 | 7 | 12 | hydro=16 |
| Manipur | 2 | 1 | 1 | hydro=2 |
| Meghalaya | 10 | 8 | 2 | hydro=10 |
| Mizoram | 8 | 3 | 5 | hydro=5 |
| Nagaland | 2 | 1 | 1 | hydro=2 |
| Sikkim | 17 | 12 | 5 | hydro=17 |
| Tripura | 6 | 3 | 3 | gas=4 |

### SOUTH (7 states)
| State | Plants | With Data | Need Data | Key Types |
|-------|--------|-----------|-----------|-----------|
| Andhra Pradesh | **504** | 159 | **345** | solar=429, coal=30 |
| Karnataka | 495 | 98 | **397** | solar=419, hydro=53 |
| Kerala | 104 | 33 | **71** | solar=46, hydro=41 |
| Tamil Nadu | 422 | 133 | **289** | solar=339, coal=28 |
| Puducherry | 3 | 0 | 3 | solar=2 |
| Lakshadweep | 3 | 1 | 2 | solar=2 |
| Andaman & Nicobar | 5 | 1 | 4 | solar=5 |

---

## SECTION 3: CRITICAL DATA GAPS

### A. MISSING CAPACITY DATA (HIGH PRIORITY)
**2,498 plants (65.7%) have 0 MW capacity.** Top worst states:

| State | Missing/Total | % Missing |
|-------|--------------|-----------|
| Karnataka | 397/495 | 80.2% |
| Maharashtra | 263/371 | 70.9% |
| Rajasthan | 305/439 | 69.5% |
| Andhra Pradesh | 345/504 | 68.5% |
| Tamil Nadu | 289/422 | 68.5% |
| Kerala | 71/104 | 68.3% |
| Gujarat | 232/343 | 67.6% |
| Uttarakhand | 54/83 | 65.1% |
| Himachal Pradesh | 81/134 | 60.4% |
| Uttar Pradesh | 81/160 | 50.6% |

### B. STATE NAMING ISSUES
| Issue | Details |
|-------|---------|
| **'Orissa' → 'Odisha'** | 102 plants use old name (renamed in 2011) |
| **'Uttaranchal' → 'Uttarakhand'** | 83 plants use old name (renamed in 2007) |
| **Telangana MISSING** | **0 plants** — all merged into Andhra Pradesh. Telangana formed in 2014 with major plants: Ramagundam STPS (2600MW), Kothagudem TPS (1800MW), Nagarjuna Sagar (810MW) |

### C. WIND ENERGY CRITICALLY UNDER-COUNTED
| Problem | Details |
|---------|---------|
| India's wind capacity | ~56,000 MW (2026) |
| Wind plants in GeoJSON | **6 plants** |
| Known wind farms missing | Muppandal (TN, 1500MW), Kutch (Guj, 11500MW), Jaisalmer (RJ), Satara (MH), Karnataka sites |

### D. NUCLEAR
- GeoJSON: 8 nuclear plants
- India operating: 9 reactors (8,880 MW) + Kakrapar Unit 3&4 recently commissioned
- Kudankulam listed in Tamil Nadu AND missing from Maharashtra? Actually Kudankulam is in TN.

### E. MAJOR PLANTS MISSING FROM GeoJSON

| State | Missing Plants |
|-------|---------------|
| **J&K** | Baglihar Dam (900MW), Salal HEP (690MW), Uri HEP (480MW), Sewa HEP (120MW), Pampore Gas (180MW) |
| **HP** | Dehar Power House (990MW), Parbati HEP (830MW), Baspa-II (300MW), Shanan Power House (110MW) |
| **Punjab** | GHTP Lehra Mohabbat (500MW), Pong Dam (396MW), Harike Barrage (66MW) |
| **Uttarakhand** | Vishnuprayag (400MW), Dhauliganga (390MW), Tanakpur (120MW), Chilla (144MW), Ramganga (198MW) |
| **Haryana** | Jharli STPP (1320MW), Hissar Gas (120MW) |
| **Delhi** | Rajghat (135MW), Badarpur TPS (705MW) |
| **Rajasthan** | Kota STPS (1240MW), Chhabra STPS (2320MW), Mahi Bajaj Sagar (140MW) |
| **UP** | Rihand STPS (3000MW), NTPC Dadri (1820MW), Auraiya Gas (660MW), Bundelkhand Solar (1000MW) |
| **Bihar** | Kahalgaon STPS (2340MW), Muzaffarpur TPS (1100MW), Koderma TPS (1000MW) |
| **Gujarat** | Mundra UMPP (4000MW), Essar Salaya (1200MW), Kadana Dam (240MW) |
| **MP** | Vindhyachal STPS (4760MW), Sant Singaji (2520MW), Sasan UMPP (3960MW) |
| **Chhattisgarh** | KSK Mahanadi (3600MW), Jindal Tamnar (3400MW), NSPCL Bhilai (500MW) |
| **Jharkhand** | Maithon TPS (1050MW), Patratu TPS (800MW), Adani Godda (1320MW) |
| **West Bengal** | Kolaghat (1260MW), Bakreswar (1050MW), Purulia Pumped Storage (900MW) |
| **Maharashtra** | Tirora (3300MW), Koyna Hydro (1960MW full), Kudankulam *(not in MH - its in TN)* |
| **Karnataka** | Kaiga Nuclear (880MW), Sharavathi Hydro (1471MW), Pavagada Solar (2050MW) |
| **Goa** | Goa Gas Power Station (48MW) — 0 plants with data |
| **AP** | Krishnapatnam (2640MW), NP Kunta Solar (1500MW), Srisailam (1670MW) |
| **TN** | Neyveli Lignite (2040MW), Kundah Hydro (370MW), Periyar Dam (140MW) |
| **Kerala** | Idukki Dam (780MW), Sabarigiri (340MW) |
| **NE States** | Loktak Hydro Manipur (105MW), Kynshi Meghalaya (450MW), Subansiri Arunachal (2000MW) |

---

## SECTION 4: CAPACITY MISMATCHES (Wrong Values in GeoJSON)

| Plant | Wiki Value | GeoJSON Value | Error |
|-------|-----------|--------------|-------|
| Kakrapar Nuclear (Guj) | 2,200 MW | 1,140 MW | Huge undercount |
| Pragati-III (Delhi) | 1,500 MW | 330 MW | Under-reported |
| Suratgarh STPP (RJ) | 1,500 MW | 2,820 MW | Over-reported |
| Bikaner Solar (RJ) | 1,000 MW | 2.5 MW | Critical undercount |
| Sardar Sarovar (Guj) | 1,450 MW | 1,200 MW | Moderate under |
| Sasan UMPP (MP) | 3,960 MW | 750 MW | Critical undercount |
| Koyna Hydro (MH) | 1,960 MW | 320 MW | (only one stage in data) |
| Guru Gobind Singh (Punjab) | 2,100 MW | 920 MW | Only one stage included |

---

## SECTION 5: RECOMMENDED ACTIONS

### 🔴 Priority 1 — Fix State Names (~1 day)
- Rename `Orissa` → `Odisha` (102 plants affected)
- Rename `Uttaranchal` → `Uttarakhand` (83 plants affected)
- **Split Telangana** from Andhra Pradesh — identify plants in Telangana districts (Ramagundam, Kothagudem, Hyderabad, Warangal districts)

### 🔴 Priority 2 — Fill Missing Capacity Data (~2-3 days)
- **2,498 plants have 0 MW** — this is the biggest data quality issue
- Worst: Karnataka (397), Andhra Pradesh (345), Rajasthan (305), Tamil Nadu (289), Maharashtra (263)
- Cross-reference with CEA reports, Wikipedia, NPP portal
- Many are small solar plants — even 1 MW placeholder beats 0 MW

### 🔴 Priority 3 — Add Missing Major Power Plants (~3-5 days)
- **~120+ known major plants** completely missing from dataset
- Focus on coal (12+ major stations missing) and hydro (30+ stations)
- Reference: Wikipedia list of power stations in India (141 coal plants vs 310 in GeoJSON — many are the same plant split into units)

### 🟡 Priority 4 — Complete Wind Energy (~2-3 days)
- Add the top 50 wind farms across Tamil Nadu, Gujarat, Karnataka, Rajasthan, Maharashtra
- Reference: "Wind power in India" Wikipedia page, MNRE data

### 🟡 Priority 5 — Deduplication & Cleanup (~1 day)
- Duplicate entries: Koldam Dam Powerhouse x2, Leh Solar Plant x3, "Port Blair Tehsil Solar Plant" x4
- ~60 "unknown" type plants need classification
- Placeholder names like "Tahsil Solar Plant" need proper naming

---

## APPENDIX: CROSS-REFERENCE FILENAMES

| File | Location |
|------|----------|
| Full coal plant reference (141 plants) | `coal_power_stations_india.csv` |
| Wikipedia page export | `wiki_text_dump.txt` |
| Audit script batch 1 (north 5) | `audit_north_states.py` |
| Audit script batch 2 (6-10) | `audit_states_6_10.py` |
| Audit script batch 3 (11-15) | `audit_states_11_15.py` |
| Audit script batch 4 (16-36) | `audit_states_16_36.py` |
| Original missing plants data | `plants_missing_data.json` |
| Backend missing list | `web/backend/missing_power_plants.json` |

---

*End of Audit Report — generated by Hermes Agent on June 30, 2026*

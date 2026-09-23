# World War II Aerial Operations & Combat Chronology Dataset

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![R 4.0+](https://img.shields.io/badge/R-4.0+-276DC3.svg)](https://www.r-project.org/)
[![Data Formats](https://img.shields.io/badge/formats-Parquet%20%7C%20SQLite%20%7C%20GeoJSON%20%7C%20CSV-green.svg)]()
[![License: Public Domain](https://img.shields.io/badge/license-Public%20Domain-lightgrey.svg)](https://creativecommons.org/publicdomain/mark/1.0/)

A comprehensive, curated, and query-optimized compilation uniting two foundational historical archives of World War II aerial warfare:
1. **The U.S. DoD / AFRI Theater History of Operations (THOR) Database**: 178,281 target-level bombing attack records with target coordinates and bomb tonnages, plus Imada-level cartography of the Tunisia Campaign.
2. **The USAAF Combat Chronology (1941–1945)**: Jack McKillop's day-by-day narrative (based on Carter & Mueller's *Combat Chronology*), split into 8,585 events, with claims, losses, casualties (KIA/WIA/MIA) and unit moves extracted from the text by regular expressions.

---

## 🎯 Key Capabilities & Integrated Analytics

```text
WWII AERIAL WARFARE CORPUS
├── 1. QUANTITATIVE BOMBING TELEMETRY (THOR WWII)
│   ├── 178,281 attack records across all theaters (3 Sep 1939 – 31 Dec 1945)
│   ├── 169,429 records (95.0%) with valid target coordinates
│   ├── 4.30 million tons recorded (3.48M HE, 554k incendiary, 203k fragmentation; see caveats)
│   └── Imada (عمادة) spatial join for Tunisia: 1,909 geolocated strikes, 1,750 inside 90 of the 2,084 sectors
│
└── 2. OPERATIONAL COMBAT NARRATIVES (USAAF Combat Chronology)
    ├── 1,328 dated entries (6 Dec 1941 order of battle, then 7 Dec 1941 – 2 Sep 1945; 39 days have no entry)
    ├── 8,585 narrative blocks naming 16 Numbered Air Forces
    ├── 798 claim/loss records (537 with enemy-aircraft claims, 349 with probable/damaged figures)
    ├── 435 casualty records totalling 39,024 MIA, 2,886 KIA and 5,041 WIA
    ├── 1,367 unit move / transfer / arrival mentions
    └── Daily crosswalk view joining the chronology to THOR bombing totals by date
```

---

## 🌐 Interactive Web Applications

This repository includes three interactive web applications ready to open in any web browser without backend setup:

1. **[USAAF Combat Chronology Explorer (`docs/chronology_explorer.html`)](docs/chronology_explorer.html)**: Instant search and filtering across all 8,585 combat events, dogfight claims, casualties, unit base moves, and direct links to THOR bombing records.
2. **[Global Bombing Dashboard (`docs/index.html`)](docs/index.html)**: Global dark-matter Leaflet map with live theater filtering (ETO, MTO, PTO, CBI, Tunisia) and yearly tonnage breakdown charts.
3. **[Interactive Tunisia Imada Map (`docs/tunisia_bombing_imadas_interactive.html`)](docs/tunisia_bombing_imadas_interactive.html)**: Sector-level Leaflet map displaying all 2,084 Imada boundaries and 1,909 clickable bombing strike pins with ordnance details.

---

## 🗺️ Minimalist Publication Cartographic Atlas (`maps/`)

All maps are designed with minimalist aesthetic principles (high contrast, pure white background `#FFFFFF`, delicate administrative boundaries, and strike markers sized proportionally to ordnance tonnage). Available in both **300 DPI high-resolution PNG** and **infinite-resolution vector PDF**:

### 1. Global & Theater Strategic Maps
- **WWII Global Bombing Footprint** (169,429 geolocated records): [`maps/wwii_global_bombing_footprint.pdf`](maps/wwii_global_bombing_footprint.pdf) • [PNG](maps/wwii_global_bombing_footprint.png)
- **European Theater (ETO) Strategic Bombing** (3.15M tons, Germany/France): [`maps/wwii_eto_strategic_bombing.pdf`](maps/wwii_eto_strategic_bombing.pdf) • [PNG](maps/wwii_eto_strategic_bombing.png)
- **Mediterranean Theater (MTO) Campaign** (Italy, Balkans, Ploesti, North Africa): [`maps/wwii_mto_mediterranean_campaign.pdf`](maps/wwii_mto_mediterranean_campaign.pdf) • [PNG](maps/wwii_mto_mediterranean_campaign.png)
- **Pacific War & CBI Theater (PTO / CBI)** (Island-hopping & Japan B-29 raids): [`maps/wwii_pto_cbi_pacific_war.pdf`](maps/wwii_pto_cbi_pacific_war.pdf) • [PNG](maps/wwii_pto_cbi_pacific_war.png)
- **Strategic Bombing of the Third Reich (Germany & Austria)**: [`maps/wwii_germany_strategic_bombing_closeup.pdf`](maps/wwii_germany_strategic_bombing_closeup.pdf) • [PNG](maps/wwii_germany_strategic_bombing_closeup.png)

### 2. Tunisia Campaign: Temporal Progression & Imada Analytics
- **4-Phase Campaign Progression Grid** (Composite 2×2 timeline): [`maps/tunisia_campaign_phases_grid.pdf`](maps/tunisia_campaign_phases_grid.pdf) • [PNG](maps/tunisia_campaign_phases_grid.png)
  - **Phase 1: Torch & Airfield Neutralization (Nov–Dec 1942)**: [`maps/tunisia_phase1_torch_airfields.pdf`](maps/tunisia_phase1_torch_airfields.pdf) • [PNG](maps/tunisia_phase1_torch_airfields.png)
  - **Phase 2: Kasserine Pass (Jan–Feb 1943)**: [`maps/tunisia_phase2_kasserine_pass.pdf`](maps/tunisia_phase2_kasserine_pass.pdf) • [PNG](maps/tunisia_phase2_kasserine_pass.png)
  - **Phase 3: Mareth Line & Coastal Breakthrough (Mar–Apr 1943)**: [`maps/tunisia_phase3_mareth_line.pdf`](maps/tunisia_phase3_mareth_line.pdf) • [PNG](maps/tunisia_phase3_mareth_line.png)
  - **Phase 4: Operation Vulcan & Axis Surrender (May 1943)**: [`maps/tunisia_phase4_vulcan_surrender.pdf`](maps/tunisia_phase4_vulcan_surrender.pdf) • [PNG](maps/tunisia_phase4_vulcan_surrender.png)
- **Imada-Level Bombing Density Choropleth** (90 of 2,084 sectors bombed): [`maps/tunisia_imada_bombing_density.pdf`](maps/tunisia_imada_bombing_density.pdf) • [PNG](maps/tunisia_imada_bombing_density.png)
- **Target Functional Taxonomy Map** (Airfields, Ports, Rail, Fortifications): [`maps/tunisia_target_types_distribution.pdf`](maps/tunisia_target_types_distribution.pdf) • [PNG](maps/tunisia_target_types_distribution.png)
- **National Crimson Edition**: [`maps/tunisia_minimalist_national_crimson.pdf`](maps/tunisia_minimalist_national_crimson.pdf) • [PNG](maps/tunisia_minimalist_national_crimson.png)
- **National Monochrome Edition**: [`maps/tunisia_minimalist_national_monochrome.pdf`](maps/tunisia_minimalist_national_monochrome.pdf) • [PNG](maps/tunisia_minimalist_national_monochrome.png)

### 3. Micro-Regional Tactical Battle Closeups (Imada Level)
- **Greater Tunis & Bizerte Naval Complex**: [`maps/tunisia_tactical_tunis_bizerte.pdf`](maps/tunisia_tactical_tunis_bizerte.pdf) • [PNG](maps/tunisia_tactical_tunis_bizerte.png)
- **The Mareth Line & Gulf of Gabès**: [`maps/tunisia_tactical_mareth_gabes.pdf`](maps/tunisia_tactical_mareth_gabes.pdf) • [PNG](maps/tunisia_tactical_mareth_gabes.png)
- **Kasserine, Gafsa & Central Front**: [`maps/tunisia_tactical_kasserine_gafsa.pdf`](maps/tunisia_tactical_kasserine_gafsa.pdf) • [PNG](maps/tunisia_tactical_kasserine_gafsa.png)
- **Eastern Sahel Ports & Coastal Rail Line**: [`maps/tunisia_tactical_sahel_ports.pdf`](maps/tunisia_tactical_sahel_ports.pdf) • [PNG](maps/tunisia_tactical_sahel_ports.png)

---

## 📁 Repository Structure

```text
wwii-thor-dataset/
├── maps/                                       # 20 publication-grade maps (PDF & PNG)
│   ├── wwii_global_bombing_footprint.*         # Global Allied bombing footprint
│   ├── wwii_eto_strategic_bombing.*            # ETO European strategic bombing
│   ├── wwii_mto_mediterranean_campaign.*       # MTO Mediterranean air war
│   ├── wwii_pto_cbi_pacific_war.*              # PTO & CBI Pacific campaign
│   ├── wwii_germany_strategic_bombing_closeup.*# Strategic bombing of Third Reich
│   ├── tunisia_campaign_phases_grid.*          # 4-Phase composite campaign grid
│   ├── tunisia_phase1_torch_airfields.*        # Phase 1 standalone map
│   ├── tunisia_phase2_kasserine_pass.*         # Phase 2 standalone map
│   ├── tunisia_phase3_mareth_line.*            # Phase 3 standalone map
│   ├── tunisia_phase4_vulcan_surrender.*       # Phase 4 standalone map
│   ├── tunisia_imada_bombing_density.*         # Imada density choropleth (90 bombed sectors)
│   ├── tunisia_target_types_distribution.*     # Target taxonomy classification
│   ├── tunisia_tactical_tunis_bizerte.*        # Tunis & Bizerte tactical closeup
│   ├── tunisia_tactical_mareth_gabes.*         # Mareth Line tactical closeup
│   ├── tunisia_tactical_kasserine_gafsa.*      # Kasserine Pass tactical closeup
│   ├── tunisia_tactical_sahel_ports.*          # Sahel ports & rail closeup
│   ├── tunisia_minimalist_national_crimson.*   # Full national crimson edition
│   └── tunisia_minimalist_national_monochrome.*# Full national monochrome edition
├── data/
│   ├── raw/
│   │   ├── THOR_WWII_DATA_CLEAN.csv            # Original AFRI mission records (35.9 MB)
│   │   ├── THOR_WWII_AIRCRAFT_GLOSS.csv        # Aircraft reference glossary (52 models)
│   │   └── THOR_WWII_WEAPON_GLOSS.csv          # Munitions glossary (59 types)
│   ├── processed/
│   │   ├── thor_wwii_enriched.parquet          # Fast columnar format (6.57 MB, 78 attributes)
│   │   ├── thor_wwii.sqlite.gz                 # Compressed THOR database (14.0 MB)
│   │   ├── thor_wwii_clean.csv.gz              # Compressed CSV archive (5.88 MB)
│   │   ├── usaaf_combat_chronology.sqlite      # Normalized relational database (7.5 MB)
│   │   ├── usaaf_combat_chronology.sqlite.gz   # Compressed SQLite archive (1.9 MB)
│   │   ├── usaaf_chronology_events.parquet     # Columnar events dataset (1.8 MB)
│   │   ├── usaaf_chronology_days.csv.gz        # Dated entries (1,328 days)
│   │   ├── usaaf_chronology_events.csv.gz      # Operational events (8,585 rows)
│   │   ├── usaaf_chronology_missions.csv.gz    # Sortie details (2,562 rows)
│   │   ├── usaaf_chronology_combat.csv.gz      # Aerial claims & losses (798 rows)
│   │   ├── usaaf_chronology_casualties.csv.gz  # KIA, WIA, MIA tallies (435 rows)
│   │   └── usaaf_chronology_movements.csv.gz   # Unit base relocations (1,367 rows)
│   └── gis/
│       ├── tunisia_imadas/                     # Shapefiles: 2,084 sectors, 24 governorates, 350 municipalities
│       ├── tunisia_bombing_by_imada.csv        # Bombing statistics for the 90 bombed Imadas (UTF-8)
│       ├── tunisia_wwii_combat_chronology.csv  # 267 operational narratives for Tunisia
│       ├── targets_aggregated.geojson          # 10,261 target clusters with statistics
│       └── flight_paths.geojson                # 2,555 takeoff-to-target lines
├── docs/
│   ├── chronology_explorer.html                # Interactive USAAF Chronology web explorer
│   ├── chronology_data.js                      # Instant client-side search data
│   ├── index.html                              # Global WWII bombing operations dashboard
│   ├── tunisia_bombing_imadas_interactive.html # Interactive Tunisia sector map
│   ├── wwii_thor_full_analysis.html            # Compiled R Markdown analytical report
│   ├── SCHEMA_DICTIONARY.md                    # THOR database codebook (78 variables)
│   └── CHRONOLOGY_DATA_DICTIONARY.md           # Combat Chronology schema & data dictionary
├── notebooks/
│   ├── wwii_thor_full_analysis.ipynb           # Python Jupyter notebook (Folium maps & EDA)
│   └── wwii_thor_full_analysis.Rmd             # R Markdown source notebook
├── scripts/
│   ├── fetch_data.py                           # Downloads the raw THOR CSVs
│   ├── build_thor_dataset.py                   # Ingestion & export for THOR
│   ├── analyze_all.py                          # Dashboard (docs/index.html) & notebook generator
│   ├── build_chronology_dataset.py             # Parser & builder for the USAAF Chronology
│   ├── apply_chronology_corrections.py         # Re-applies chronology corrections to the committed DB
│   ├── verify_chronology_dataset.py            # Automated test suite for Chronology
│   ├── build_tunisia_imada_stats.py            # THOR x Imada point-in-polygon statistics
│   ├── build_tunisia_governorates.R            # Dissolves sectors into the 24 governorates
│   ├── generate_minimalist_maps.R              # Original minimalist white maps
│   ├── generate_tunisia_maps.R                 # Tunisia light/dark maps & interactive Leaflet map
│   ├── generate_tunisia_expanded_maps.R        # 11 expanded Tunisia campaign & tactical maps
│   ├── generate_theater_global_maps.R          # 5 Global & Theater strategic maps
│   └── verify_dataset.py                       # Automated test suite for THOR
├── requirements.txt
└── README.md
```

---

## 🚀 Quickstart & Queries

### 1. Python (Relational & Analytical Queries)
```python
import sqlite3
import pandas as pd

# Connect to the normalized USAAF Chronology database
conn = sqlite3.connect("data/processed/usaaf_combat_chronology.sqlite")

# Query the crosswalk view: Daily operational synergy on D-Day
dday = pd.read_sql_query("""
    SELECT * FROM v_daily_operational_crosswalk 
    WHERE date = '1944-06-06';
""", conn)
print(dday)

# Query air-to-air dogfight claims against the Luftwaffe in 1944
dogfights = pd.read_sql_query("""
    SELECT date, air_force, claims_destroyed, claims_probable, claims_damaged, friendly_lost, context_snippet
    FROM chronology_aerial_combat
    WHERE claims_destroyed >= 20 AND date LIKE '1944%'
    ORDER BY claims_destroyed DESC
    LIMIT 5;
""", conn)
print(dogfights)
```

### 2. Loading Parquet Events
```python
# Read the 8,585 narrative events
events = pd.read_parquet("data/processed/usaaf_chronology_events.parquet")

# Filter for Tunisia missions in March 1943 (Mareth Line battle)
mareth = events[
    (events["sub_region"] == "Tunisia") & 
    (events["date"].str.startswith("1943-03"))
]
print(f"Mareth campaign operational events: {len(mareth)}")
```

### 3. Regenerating All Publication Maps
```bash
# Rebuild the Tunisia GIS inputs (Imada statistics, governorate layer)
python3 scripts/build_tunisia_imada_stats.py
Rscript scripts/build_tunisia_governorates.R

# Generate all 11 Tunisia campaign and tactical maps
# (run in a UTF-8 locale, e.g. LANG=C.UTF-8, or accented labels render as "..")
Rscript scripts/generate_tunisia_expanded_maps.R

# Generate all 5 Global and Theater strategic maps
Rscript scripts/generate_theater_global_maps.R
```

---

## ⚠️ Data Caveats
- **THOR records are not missions.** Each row is a target-level attack entry; one raid can span several rows.
- **Tonnage outliers are kept.** `total_tons_clean` is the greater of the recorded total and HE + IC + Frag, which raises 345 records. It includes the Hiroshima and Nagasaki records (15,000 t and 20,000 t, TNT-equivalent yield rather than bombs dropped) and a 4,750 t record for 6 aircraft at Kassala (17 Aug 1940).
- **Tunisia phases** cover Nov 1942 – May 1943 only; 14 Tunisia records dated outside that window are left out of the phase maps. 159 geolocated Tunisia strikes fall outside every Imada polygon: offshore targets plus records whose coordinates are mis-coded in THOR (e.g. Fondouk, La Sebala).
- **Chronology fields are regex extractions** from narrative text. They index the narrative; they are not verified tallies. 31% of events have no recognised theater header (`OTHER`). See [`docs/CHRONOLOGY_DATA_DICTIONARY.md`](docs/CHRONOLOGY_DATA_DICTIONARY.md) for the corrections applied (re-dated 1943 entries, a duplicated day, page footers).
- **Rebuilding the chronology from scratch** needs a local mirror of the source pages, which is not included. `scripts/apply_chronology_corrections.py` re-applies the corrections to the committed database.

---

## 📜 Attribution & Sources
- **THOR Dataset**: Lt. Col. Jenns Robertson and the United States Air Force Research Institute (AFRI), Data.mil / U.S. Department of Defense. The raw CSVs are downloaded by `scripts/fetch_data.py` from the `dlozeve/ww2-bombings` GitHub mirror.
- **USAAF Combat Chronology**: Jack McKillop, *USAAF Combat Operations in WWII*, published at [aircrewremembered.com](https://aircrewremembered.com/USAAFCombatOperations/); based on Kit C. Carter and Robert Mueller, *The Army Air Forces in World War II: Combat Chronology, 1941–1945*, Office of Air Force History.
- **Administrative GIS Boundaries**: 2,084 Imada (sector) and 350 municipality boundaries from `jmgclark/tunisia_shapefiles`. The sector file carries OpenStreetMap IDs, so OpenStreetMap attribution (© OpenStreetMap contributors, ODbL) likely applies. The 24 governorates are dissolved from the sectors.

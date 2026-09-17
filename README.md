# World War II Aerial Operations & Combat Chronology Dataset

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![R 4.0+](https://img.shields.io/badge/R-4.0+-276DC3.svg)](https://www.r-project.org/)
[![Data Formats](https://img.shields.io/badge/formats-Parquet%20%7C%20SQLite%20%7C%20GeoJSON%20%7C%20CSV-green.svg)]()
[![License: Public Domain](https://img.shields.io/badge/license-Public%20Domain-lightgrey.svg)](https://creativecommons.org/publicdomain/mark/1.0/)

A comprehensive, curated, and query-optimized compilation uniting two foundational historical archives of World War II aerial warfare:
1. **The U.S. DoD / AFRI Theater History of Operations (THOR) Database**: Quantitative combat bombing missions (178,281 records), exact target coordinates, bomb tonnages, and granular Imada-level cartography of the Tunisia Campaign.
2. **The USAAF Worldwide Combat Chronology (1941–1945)**: Official day-by-day operational combat logs (8,742 events), air-to-air dogfight scorecards (Destroyed-Probable-Damaged claims), personnel casualties (KIA/WIA/MIA), and order-of-battle airfield relocations.

---

## 🎯 Key Capabilities & Integrated Analytics

```text
WWII AERIAL WARFARE CORPUS
├── 1. QUANTITATIVE BOMBING TELEMETRY (THOR WWII)
│   ├── 178,281 combat missions across all theaters (1939–1945)
│   ├── 169,429 geolocated strike coordinates (95.0% precision)
│   ├── 4.2 million tons of high explosive, incendiary, and fragmentation bombs
│   └── Granular Imada (عمادة) spatial intersection for Tunisia (1,909 strikes across 2,084 sectors)
│
└── 2. OPERATIONAL COMBAT NARRATIVES (USAAF Combat Chronology)
    ├── 1,329 calendar days (7 Dec 1941 – 2 Sep 1945)
    ├── 8,742 structured operational narrative blocks across 16 Numbered Air Forces
    ├── 799 aerial dogfight scorecards with standard Destroyed-Probable-Damaged (D-P-D) claims
    ├── 436 casualty reports tracking 39,000+ MIA, 2,700+ KIA, and 5,000+ WIA
    ├── 1,368 Order-of-Battle unit movements (airfield-to-airfield relocations)
    └── Relational Crosswalk View bridging narrative history to quantitative strike data
```

---

## 🌐 Interactive Web Applications

This repository includes three interactive web applications ready to open in any web browser without backend setup:

1. **[USAAF Combat Chronology Explorer (`docs/chronology_explorer.html`)](docs/chronology_explorer.html)**: Instant search and filtering across all 8,742 combat events, dogfight claims, casualties, unit base moves, and direct links to THOR bombing records.
2. **[Global Bombing Dashboard (`docs/index.html`)](docs/index.html)**: Global dark-matter Leaflet map with live theater filtering (ETO, MTO, PTO, CBI, Tunisia) and yearly tonnage breakdown charts.
3. **[Interactive Tunisia Imada Map (`docs/tunisia_bombing_imadas_interactive.html`)](docs/tunisia_bombing_imadas_interactive.html)**: Sector-level Leaflet map displaying all 2,084 Imada boundaries and 1,909 clickable bombing mission pins with complete ordnance details.

---

## 🗺️ Minimalist Publication Cartographic Atlas (`maps/`)

All maps are designed with minimalist aesthetic principles (high contrast, pure white background `#FFFFFF`, delicate administrative boundaries, and strike markers sized proportionally to ordnance tonnage). Available in both **300 DPI high-resolution PNG** and **infinite-resolution vector PDF**:

### 1. Global & Theater Strategic Maps
- **WWII Global Bombing Footprint** (170,000+ strikes): [`maps/wwii_global_bombing_footprint.pdf`](maps/wwii_global_bombing_footprint.pdf) • [PNG](maps/wwii_global_bombing_footprint.png)
- **European Theater (ETO) Strategic Bombing** (3.15M tons, Germany/France): [`maps/wwii_eto_strategic_bombing.pdf`](maps/wwii_eto_strategic_bombing.pdf) • [PNG](maps/wwii_eto_strategic_bombing.png)
- **Mediterranean Theater (MTO) Campaign** (Italy, Balkans, Ploesti, North Africa): [`maps/wwii_mto_mediterranean_campaign.pdf`](maps/wwii_mto_mediterranean_campaign.pdf) • [PNG](maps/wwii_mto_mediterranean_campaign.png)
- **Pacific War & CBI Theater (PTO / CBI)** (Island-hopping & Japan B-29 raids): [`maps/wwii_pto_cbi_pacific_war.pdf`](maps/wwii_pto_cbi_pacific_war.pdf) • [PNG](maps/wwii_pto_cbi_pacific_war.png)
- **Strategic Bombing of the Third Reich (Germany & Austria)**: [`maps/wwii_germany_strategic_bombing_closeup.pdf`](maps/wwii_germany_strategic_bombing_closeup.pdf) • [PNG](maps/wwii_germany_strategic_bombing_closeup.png)

### 2. Tunisia Campaign: Temporal Progression & Imada Analytics
- **4-Phase Campaign Progression Grid** (Composite 2×2 timeline): [`maps/tunisia_campaign_phases_grid.pdf`](maps/tunisia_campaign_phases_grid.pdf) • [PNG](maps/tunisia_campaign_phases_grid.png)
  - **Phase 1: Torch & Airfield Neutralization (Nov–Dec 1942)**: [`maps/tunisia_phase1_torch_airfields.pdf`](maps/tunisia_phase1_torch_airfields.pdf) • [PNG](maps/tunisia_phase1_torch_airfields.png)
  - **Phase 2: Battle of Kasserine Pass (Jan–Feb 1943)**: [`maps/tunisia_phase2_kasserine_pass.pdf`](maps/tunisia_phase2_kasserine_pass.pdf) • [PNG](maps/tunisia_phase2_kasserine_pass.png)
  - **Phase 3: Mareth Line & Coastal Breakthrough (Mar–Apr 1943)**: [`maps/tunisia_phase3_mareth_line.pdf`](maps/tunisia_phase3_mareth_line.pdf) • [PNG](maps/tunisia_phase3_mareth_line.png)
  - **Phase 4: Operation Vulcan & Axis Surrender (May 1943)**: [`maps/tunisia_phase4_vulcan_surrender.pdf`](maps/tunisia_phase4_vulcan_surrender.pdf) • [PNG](maps/tunisia_phase4_vulcan_surrender.png)
- **Imada-Level Bombing Density Choropleth** (2,084 sectors): [`maps/tunisia_imada_bombing_density.pdf`](maps/tunisia_imada_bombing_density.pdf) • [PNG](maps/tunisia_imada_bombing_density.png)
- **Target Functional Taxonomy Map** (Airfields, Ports, Rail, Fortifications): [`maps/tunisia_target_types_distribution.pdf`](maps/tunisia_target_types_distribution.pdf) • [PNG](maps/tunisia_target_types_distribution.png)
- **National Crimson Edition**: [`maps/tunisia_minimalist_national_crimson.pdf`](maps/tunisia_minimalist_national_crimson.pdf) • [PNG](maps/tunisia_minimalist_national_crimson.png)
- **National Monochrome Edition**: [`maps/tunisia_minimalist_national_monochrome.pdf`](maps/tunisia_minimalist_national_monochrome.pdf) • [PNG](maps/tunisia_minimalist_national_monochrome.png)

### 3. Micro-Regional Tactical Battle Closeups (Imada Level)
- **Greater Tunis & Bizerte Naval Complex**: [`maps/tunisia_tactical_tunis_bizerte.pdf`](maps/tunisia_tactical_tunis_bizerte.pdf) • [PNG](maps/tunisia_tactical_tunis_bizerte.png)
- **The Mareth Line & Gulf of Gabès**: [`maps/tunisia_tactical_mareth_gabes.pdf`](maps/tunisia_tactical_mareth_gabes.pdf) • [PNG](maps/tunisia_tactical_mareth_gabes.png)
- **Kasserine Pass, Sbeitla & Central Front**: [`maps/tunisia_tactical_kasserine_gafsa.pdf`](maps/tunisia_tactical_kasserine_gafsa.pdf) • [PNG](maps/tunisia_tactical_kasserine_gafsa.png)
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
│   ├── tunisia_imada_bombing_density.*         # Imada 2,084-sector density choropleth
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
│   │   ├── usaaf_combat_chronology.sqlite      # Normalized relational database (7.6 MB)
│   │   ├── usaaf_combat_chronology.sqlite.gz   # Compressed SQLite archive (1.9 MB)
│   │   ├── usaaf_chronology_events.parquet     # Columnar events dataset (1.8 MB)
│   │   ├── usaaf_chronology_days.csv.gz        # Calendar summary (1,329 days)
│   │   ├── usaaf_chronology_events.csv.gz      # Operational events (8,742 rows)
│   │   ├── usaaf_chronology_missions.csv.gz    # Sortie details (2,565 rows)
│   │   ├── usaaf_chronology_combat.csv.gz      # Aerial claims & losses (799 rows)
│   │   ├── usaaf_chronology_casualties.csv.gz  # KIA, WIA, MIA tallies (436 rows)
│   │   └── usaaf_chronology_movements.csv.gz   # Unit base relocations (1,368 rows)
│   └── gis/
│       ├── tunisia_imadas/                     # Shapefiles: 2,084 sectors & 24 governorates
│       ├── tunisia_bombing_by_imada.csv        # Imada-level bombing statistics
│       ├── tunisia_wwii_combat_chronology.csv  # 267 operational narratives for Tunisia
│       ├── targets_aggregated.geojson          # 10,261 target clusters with statistics
│       └── flight_paths.geojson                # 2,555 mission trajectories
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
│   ├── build_thor_dataset.py                   # Ingestion & export for THOR
│   ├── build_chronology_dataset.py             # Complete parser & builder for USAAF Chronology
│   ├── verify_chronology_dataset.py            # Automated test suite for Chronology
│   ├── generate_minimalist_maps.R              # Original minimalist white maps
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
# Lightning-fast read of 8,742 narrative events
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
# Generate all 11 Tunisia campaign and tactical maps
Rscript scripts/generate_tunisia_expanded_maps.R

# Generate all 5 Global and Theater strategic maps
Rscript scripts/generate_theater_global_maps.R
```

---

## 📜 Attribution & Sources
- **THOR Dataset**: Lt. Col. Jenns Robertson and the United States Air Force Research Institute (AFRI), Data.mil / U.S. Department of Defense.
- **USAAF Combat Chronology**: Kit C. Carter and Robert Mueller, *The Army Air Forces in World War II: Combat Chronology, 1941–1945*, Office of Air Force History / AFHRA.
- **Administrative GIS Boundaries**: Official 2,084 sector shapefiles courtesy of `jmgclark/tunisia_shapefiles`.

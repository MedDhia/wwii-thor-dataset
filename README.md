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

## 🗺️ Tunisia Campaign: Minimalist Publication Cartography

The repository provides publication-ready 300 DPI PNGs and infinite-resolution vector PDFs in `data/gis/`:
- **National Crimson Edition**: [`data/gis/tunisia_minimalist_national_crimson.pdf`](data/gis/tunisia_minimalist_national_crimson.pdf) & [PNG](data/gis/tunisia_minimalist_national_crimson.png)
- **National Monochrome Edition**: [`data/gis/tunisia_minimalist_national_monochrome.pdf`](data/gis/tunisia_minimalist_national_monochrome.pdf) & [PNG](data/gis/tunisia_minimalist_national_monochrome.png)
- **Northern Inset (Tunis, Bizerte, Cap Bon)**: [`data/gis/tunisia_minimalist_north.png`](data/gis/tunisia_minimalist_north.png)
- **Central & Southern Inset (Kasserine, Gafsa, Sfax, Mareth)**: [`data/gis/tunisia_minimalist_south_central.png`](data/gis/tunisia_minimalist_south_central.png)

---

## 📁 Repository Structure

```text
wwii-thor-dataset/
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
│       ├── tunisia_wwii_combat_chronology.csv  # 267 operational narratives for Tunisia
│       ├── targets_aggregated.geojson          # 10,261 target clusters with statistics
│       ├── flight_paths.geojson                # 2,555 mission trajectories
│       └── *.png / *.pdf                       # Minimalist white-background maps
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
│   ├── generate_minimalist_maps.R              # Publication-grade minimalist white maps
│   ├── generate_tunisia_maps.R                 # Full cartographic & Leaflet generation script
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

---

## 📜 Attribution & Sources
- **THOR Dataset**: Lt. Col. Jenns Robertson and the United States Air Force Research Institute (AFRI), Data.mil / U.S. Department of Defense.
- **USAAF Combat Chronology**: Kit C. Carter and Robert Mueller, *The Army Air Forces in World War II: Combat Chronology, 1941–1945*, Office of Air Force History / AFHRA.
- **Administrative GIS Boundaries**: Official 2,084 sector shapefiles courtesy of `jmgclark/tunisia_shapefiles`.

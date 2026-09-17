# World War II Theater History of Operations (THOR) Dataset

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![R 4.0+](https://img.shields.io/badge/R-4.0+-276DC3.svg)](https://www.r-project.org/)
[![Data Formats](https://img.shields.io/badge/formats-Parquet%20%7C%20SQLite%20%7C%20GeoJSON%20%7C%20CSV-green.svg)]()
[![License: Public Domain](https://img.shields.io/badge/license-Public%20Domain-lightgrey.svg)](https://creativecommons.org/publicdomain/mark/1.0/)

A comprehensive, curated, and query-optimized compilation of the complete United States Department of Defense / Air Force Research Institute (AFRI) **Theater History of Operations (THOR)** World War II aerial bombing operations database, featuring cross-theater analytics, interactive web GIS dashboards, and granular sector-level (*Imada* / عمادة) cartography of the Tunisia Campaign (1942–1943).

---

## 🎯 Overview & Scope

- **Total Missions Recorded**: **178,281** combat bombing operations.
- **Timeline**: September 1, 1939 – December 31, 1945 (complete WWII conflict duration).
- **Theaters Covered**: 
  - **European Theater (ETO)**: 95,827 missions | 3,154,320.6 tons
  - **Mediterranean Theater (MTO)**: 30,532 missions | 591,589.1 tons
  - **Pacific Theater (PTO)**: 36,192 missions | 438,268.4 tons
  - **China-Burma-India (CBI)**: 12,404 missions | 53,260.0 tons
  - **East Africa & Madagascar**: 168 missions | 6,622.6 tons
- **Participating Allied Air Forces**: USAAF (8th, 9th, 12th, 15th, 5th, 13th, 20th Air Forces), Royal Air Force (RAF Bomber Command & Desert Air Force), Royal Australian Air Force (RAAF), Royal New Zealand Air Force (RNZAF), South African Air Force (SAAF).
- **Geolocation Precision**: **169,429 missions (95.0%)** contain verified target coordinates; **2,555 missions** contain full takeoff-to-target flight trajectories.

---

## 🗺️ Tunisia Campaign & Imada-Level Cartography (1942–1943)

This repository includes a spatial intersection of **1,909 verified WWII bombing missions** across Tunisia's **2,084 Imada (عمادة / Sector)** administrative units.

### Minimalist Publication Maps (White Background)
The repository provides publication-ready 300 DPI PNGs and infinite-resolution vector PDFs in `data/gis/`:
- **National Crimson Edition**: [`data/gis/tunisia_minimalist_national_crimson.pdf`](data/gis/tunisia_minimalist_national_crimson.pdf) & [PNG](data/gis/tunisia_minimalist_national_crimson.png)
- **National Monochrome / Charcoal Edition**: [`data/gis/tunisia_minimalist_national_monochrome.pdf`](data/gis/tunisia_minimalist_national_monochrome.pdf) & [PNG](data/gis/tunisia_minimalist_national_monochrome.png)
- **Northern Inset (Tunis, Bizerte, Cap Bon)**: [`data/gis/tunisia_minimalist_north.png`](data/gis/tunisia_minimalist_north.png)
- **Central & Southern Inset (Kasserine, Gafsa, Sfax, Mareth)**: [`data/gis/tunisia_minimalist_south_central.png`](data/gis/tunisia_minimalist_south_central.png)

### Top 5 Bombed Imadas in Tunisia
1. **Ezzouarâa (Nefza, Béja)**: 84 strikes | **932.0 tons** (Axis road/rail choke point to Bizerte)
2. **Teboulbou (Gabès Sud, Gabès)**: 82 strikes | **669.1 tons** (Mareth Line coastal approaches)
3. **Sahloul (Sousse Jawhara, Sousse)**: 98 strikes | **616.2 tons** (Sousse port & rail marshalling yards)
4. **Bou Derbala (El Amra, Sfax)**: 90 strikes | **584.0 tons** (Coastal rail line interdiction)
5. **Enfidha (Enfidha, Sousse)**: 64 strikes | **362.5 tons** (Enfidha defensive perimeter)

---

## 📁 Repository Structure

```text
wwii-thor-dataset/
├── data/
│   ├── raw/
│   │   ├── THOR_WWII_DATA_CLEAN.csv            # Original AFRI mission records (35.9 MB)
│   │   ├── THOR_WWII_AIRCRAFT_GLOSS.csv        # Aircraft reference glossary (52 models)
│   │   └── THOR_WWII_WEAPON_GLOSS.csv          # Munitions & ordnance glossary (59 types)
│   ├── processed/
│   │   ├── thor_wwii_enriched.parquet          # Fast columnar format (6.57 MB, 78 attributes)
│   │   ├── thor_wwii.sqlite.gz                 # Compressed SQLite database with indexes (14.0 MB)
│   │   └── thor_wwii_clean.csv.gz              # Compressed CSV archive (5.88 MB)
│   └── gis/
│       ├── tunisia_imadas/                     # Shapefiles: 2,084 sectors & 24 governorates
│       ├── targets_aggregated.geojson          # 10,261 target clusters with tons & statistics
│       ├── flight_paths.geojson                # 2,555 takeoff-to-target mission linestrings
│       ├── tunisia_minimalist_national_crimson.png
│       ├── tunisia_minimalist_national_crimson.pdf
│       ├── tunisia_minimalist_national_monochrome.png
│       ├── tunisia_minimalist_national_monochrome.pdf
│       ├── tunisia_minimalist_north.png
│       └── tunisia_minimalist_south_central.png
├── docs/
│   ├── index.html                              # Interactive Leaflet web dashboard & charts
│   ├── tunisia_bombing_imadas_interactive.html # Interactive Tunisia sector map with popups
│   ├── wwii_thor_full_analysis.html            # Compiled R Markdown analytical report
│   └── SCHEMA_DICTIONARY.md                    # Data dictionary of all 78 columns
├── notebooks/
│   ├── wwii_thor_full_analysis.ipynb           # Python Jupyter notebook (Folium maps & EDA)
│   └── wwii_thor_full_analysis.Rmd             # R Markdown source notebook
├── scripts/
│   ├── fetch_data.py                           # Raw file downloader from GitHub / AFRI
│   ├── build_thor_dataset.py                   # Enrichment, cleanup, and SQLite/Parquet export
│   ├── analyze_all.py                          # Cross-theater statistics and HTML builders
│   ├── generate_tunisia_maps.R                 # Full cartographic & Leaflet generation script
│   ├── generate_minimalist_maps.R              # Publication-grade minimalist white maps
│   └── verify_dataset.py                       # Automated test & benchmark suite
├── requirements.txt
└── README.md
```

---

## 🚀 Quickstart & Usage

### 1. Setup & Dependencies
```bash
git clone https://github.com/MedDhia/wwii-thor-dataset.git
cd wwii-thor-dataset

# Python
pip install -r requirements.txt

# Decompress SQLite database (optional, needed for SQLite queries)
gunzip -k data/processed/thor_wwii.sqlite.gz
```

### 2. Python (Pandas / PyArrow)
```python
import pandas as pd

# Load the complete 178k mission dataset in milliseconds
df = pd.read_parquet("data/processed/thor_wwii_enriched.parquet")

# Filter for B-17 missions over Germany in 1944
b17_1944 = df[
    (df["aircraft_full_name"] == "B-17 Flying Fortress") &
    (df["TGT_COUNTRY"] == "GERMANY") &
    (df["year"] == 1944)
]
print(f"B-17 raids over Germany in 1944: {len(b17_1944):,}")
print(f"Total bomb weight: {b17_1944['total_tons_clean'].sum():,.1f} tons")
```

### 3. R / Tidyverse
```r
library(sf)
library(dplyr)
library(ggplot2)

# Load Tunisia sectors and mission shapefiles
sectors <- st_read("data/gis/tunisia_imadas/TN_sectors.shp")
# Run publication map generator
source("scripts/generate_minimalist_maps.R")
```

### 4. SQLite Queries
```sql
sqlite3 data/processed/thor_wwii.sqlite

-- Top 5 bombed target cities in Italy
SELECT target_location, mission_count, total_tons, first_mission, last_mission
FROM targets_summary
WHERE target_country = 'ITALY'
ORDER BY total_tons DESC
LIMIT 5;
```

---

## 🌐 Interactive Dashboards

1. **Global WWII Bombing Operations**: Open `docs/index.html` in any browser to explore global raids with theater filters (ETO, MTO, PTO, CBI, Tunisia) and yearly tonnage breakdowns.
2. **Interactive Tunisia Sector Map**: Open `docs/tunisia_bombing_imadas_interactive.html` to click individual bomb strikes (aircraft, tons, units) and inspect sector-level aggregates.
3. **Comprehensive Report**: Open `docs/wwii_thor_full_analysis.html` for in-depth statistical tables, theater comparisons, and weapon distributions.

---

## 📜 Attribution & License
The dataset originates from the **Theater History of Operations (THOR)** project by Lt. Col. Jenns Robertson and the United States Air Force Research Institute (AFRI), originally released via Data.mil and the U.S. Department of Defense. Public domain / US Government Work. Administrative boundaries for Tunisia courtesy of `jmgclark/tunisia_shapefiles`.

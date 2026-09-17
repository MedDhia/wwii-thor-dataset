#!/usr/bin/env python3
"""
build_thor_dataset.py - Clean, enrich, and compile the full WWII THOR dataset.

Transforms 178,281 mission operations across all theaters (ETO, PTO, MTO, CBI)
into optimized analytical formats (Parquet, SQLite, GeoJSON, CSV.GZ).
"""

import os
import sys
import json
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
GIS_DIR = os.path.join(BASE_DIR, "data", "gis")

RAW_OPS_CSV = os.path.join(RAW_DIR, "THOR_WWII_DATA_CLEAN.csv")
RAW_AC_CSV = os.path.join(RAW_DIR, "THOR_WWII_AIRCRAFT_GLOSS.csv")
RAW_WEAPON_CSV = os.path.join(RAW_DIR, "THOR_WWII_WEAPON_GLOSS.csv")

OUT_PARQUET = os.path.join(PROCESSED_DIR, "thor_wwii_enriched.parquet")
OUT_CSV_GZ = os.path.join(PROCESSED_DIR, "thor_wwii_clean.csv.gz")
OUT_SQLITE = os.path.join(PROCESSED_DIR, "thor_wwii.sqlite")
OUT_TARGETS_GEOJSON = os.path.join(GIS_DIR, "targets_aggregated.geojson")
OUT_FLIGHT_PATHS_GEOJSON = os.path.join(GIS_DIR, "flight_paths.geojson")

def clean_str(val):
    if pd.isna(val):
        return None
    s = str(val).strip()
    return s if s else None

def parse_coord(lat, lon):
    try:
        flat = float(lat)
        flon = float(lon)
        if -90.0 <= flat <= 90.0 and -180.0 <= flon <= 180.0 and not (flat == 0.0 and flon == 0.0):
            return flat, flon, True
    except (ValueError, TypeError):
        pass
    return None, None, False

def load_and_enrich():
    print(f"Reading raw operations data from {RAW_OPS_CSV}...")
    df = pd.read_csv(RAW_OPS_CSV, encoding="latin1", low_memory=False)
    print(f"Loaded {len(df):,} raw records with {len(df.columns)} columns.")

    print("Loading reference glossaries...")
    ac_gloss = pd.read_csv(RAW_AC_CSV, encoding="latin1")
    weap_gloss = pd.read_csv(RAW_WEAPON_CSV, encoding="latin1")

    # Build aircraft lookup map
    # AIRCRAFT -> (FULL_NAME, AIRCRAFT_TYPE, HYPERLINK)
    ac_map = {}
    for _, row in ac_gloss.iterrows():
        code = clean_str(row.get("AIRCRAFT"))
        name = clean_str(row.get("NAME"))
        full_name = clean_str(row.get("FULL_NAME"))
        ac_type = clean_str(row.get("AIRCRAFT_TYPE"))
        link = clean_str(row.get("HYPERLINK"))
        info = {
            "aircraft_full_name": full_name or name or code,
            "aircraft_category": ac_type,
            "aircraft_glossary_link": link,
        }
        if code:
            ac_map[code.upper()] = info
        if name:
            ac_map[name.upper()] = info

    # Add common aliases and unlisted designations
    custom_aliases = {
        "GB17": ac_map.get("B17", {}),
        "LANCASTER": ac_map.get("HVY", {"aircraft_full_name": "Avro Lancaster", "aircraft_category": "Heavy Bomber / Reconnaissance", "aircraft_glossary_link": "http://militaryfactory.com/aircraft/detail.asp?aircraft_id=234"}),
        "HALIFAX": ac_map.get("HALI", {}),
        "MOSQUITO": {"aircraft_full_name": "de Havilland Mosquito", "aircraft_category": "Fast Bomber / Night Fighter / Reconnaissance", "aircraft_glossary_link": "https://en.wikipedia.org/wiki/De_Havilland_Mosquito"},
        "TYPHOON": {"aircraft_full_name": "Hawker Typhoon", "aircraft_category": "Fighter-Bomber", "aircraft_glossary_link": "https://en.wikipedia.org/wiki/Hawker_Typhoon"},
        "TEMPEST": {"aircraft_full_name": "Hawker Tempest", "aircraft_category": "Fighter-Bomber", "aircraft_glossary_link": "https://en.wikipedia.org/wiki/Hawker_Tempest"},
        "SPITFIRE": {"aircraft_full_name": "Supermarine Spitfire", "aircraft_category": "Fighter / Fighter-Bomber", "aircraft_glossary_link": "https://en.wikipedia.org/wiki/Supermarine_Spitfire"},
        "BEAUFORT": ac_map.get("BEAUF", {}),
        "BEAUFIGHTER": ac_map.get("BEAU", {}),
        "BLENHEIM": ac_map.get("BLEN", {}),
        "WELLINGTON": ac_map.get("WELL", {}),
        "STIRLING": ac_map.get("STIR", {}),
        "BOSTON": ac_map.get("A20", {}),
        "MITCHELL": ac_map.get("B25", {}),
        "MARAUDER": ac_map.get("B26", {}),
        "LIBERATOR": ac_map.get("B24", {}),
        "FORTRESS": ac_map.get("B17", {}),
        "SUPERFORTRESS": ac_map.get("B29", {}),
        "LIGHTNING": ac_map.get("P38", {}),
        "THUNDERBOLT": ac_map.get("P47", {}),
        "MUSTANG": ac_map.get("P51", {}),
        "WARHAWK": ac_map.get("P40", {}),
        "AIRACOBRA": ac_map.get("P39", {}),
        "INVADER": ac_map.get("A26", {}),
        "HAVOC": ac_map.get("A20", {}),
        "CORSAIR": ac_map.get("F4U", {}),
        "DAUNTLESS": ac_map.get("SBD", {}),
        "AVENGER": ac_map.get("TBF AVENGER", {}),
        "VENTURA": ac_map.get("PV-1 VENTURA", {}),
        "CATALINA": ac_map.get("CATALINA", {}),
    }
    for k, v in custom_aliases.items():
        if k not in ac_map and v:
            ac_map[k] = v

    print("Cleaning dates and timestamps...")
    # Parse dates
    parsed_dates = pd.to_datetime(df["MSNDATE"], format="%m/%d/%Y", errors="coerce")
    df["mission_date_iso"] = parsed_dates.dt.strftime("%Y-%m-%d")
    df["year"] = parsed_dates.dt.year.astype("Int64")
    df["month"] = parsed_dates.dt.month.astype("Int64")
    df["year_month"] = parsed_dates.dt.strftime("%Y-%m")

    print("Processing and validating geolocation coordinates...")
    target_lats, target_lons, valid_tgt = [], [], []
    for lat, lon in zip(df["LATITUDE"], df["LONGITUDE"]):
        plat, plon, ok = parse_coord(lat, lon)
        target_lats.append(plat)
        target_lons.append(plon)
        valid_tgt.append(ok)
    
    df["target_lat"] = target_lats
    df["target_lon"] = target_lons
    df["has_valid_target_coords"] = valid_tgt

    takeoff_lats, takeoff_lons, valid_to = [], [], []
    for lat, lon in zip(df["TAKEOFF_LATITUDE"], df["TAKEOFF_LONGITUDE"]):
        plat, plon, ok = parse_coord(lat, lon)
        takeoff_lats.append(plat)
        takeoff_lons.append(plon)
        valid_to.append(ok)

    df["takeoff_lat"] = takeoff_lats
    df["takeoff_lon"] = takeoff_lons
    df["has_valid_takeoff_coords"] = valid_to
    df["has_flight_path"] = [t and o for t, o in zip(valid_tgt, valid_to)]

    print(f"  Valid target coordinates: {sum(valid_tgt):,} / {len(df):,} ({sum(valid_tgt)/len(df)*100:.1f}%)")
    print(f"  Valid takeoff coordinates: {sum(valid_to):,} / {len(df):,} ({sum(valid_to)/len(df)*100:.1f}%)")
    print(f"  Missions with complete flight vectors: {df['has_flight_path'].sum():,}")

    print("Enriching aircraft metadata from glossary...")
    full_names, categories, links = [], [], []
    for mds, ac_name in zip(df["MDS"], df["AIRCRAFT_NAME"]):
        mds_clean = str(mds).strip().upper() if pd.notna(mds) else ""
        ac_clean = str(ac_name).strip().upper() if pd.notna(ac_name) else ""

        match = None
        if mds_clean in ac_map:
            match = ac_map[mds_clean]
        elif ac_clean in ac_map:
            match = ac_map[ac_clean]
        else:
            # check prefix
            for k, v in ac_map.items():
                if k and (mds_clean.startswith(k) or ac_clean.startswith(k)):
                    match = v
                    break

        if match:
            full_names.append(match.get("aircraft_full_name"))
            categories.append(match.get("aircraft_category"))
            links.append(match.get("aircraft_glossary_link"))
        else:
            full_names.append(ac_clean or mds_clean or None)
            categories.append(None)
            links.append(None)

    df["aircraft_full_name"] = full_names
    df["aircraft_category"] = categories
    df["aircraft_glossary_link"] = links

    print("Cleaning Country, Theater, and Bomb Tonnages...")
    # Standardize country
    df["country_flying_mission_clean"] = df["COUNTRY_FLYING_MISSION"].str.strip().str.upper()
    # Fill known country from air force / NAF if missing
    naf_clean = df["NAF"].fillna("").astype(str).str.upper()
    usa_mask = df["country_flying_mission_clean"].isna() & (
        naf_clean.str.contains("AF|USAAF|USA") | df["UNIT_ID"].fillna("").astype(str).str.contains("BG|FG|FBG")
    )
    df.loc[usa_mask, "country_flying_mission_clean"] = "USA"

    raf_mask = df["country_flying_mission_clean"].isna() & (
        naf_clean.str.contains("RAF|BOMBER COMMAND|TACTICAL")
    )
    df.loc[raf_mask, "country_flying_mission_clean"] = "GREAT BRITAIN"

    # Numeric tonnages
    for col in ["TONS_OF_HE", "TONS_OF_IC", "TONS_OF_FRAG", "TOTAL_TONS"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    computed_tons = df["TONS_OF_HE"] + df["TONS_OF_IC"] + df["TONS_OF_FRAG"]
    df["total_tons_clean"] = np.maximum(df["TOTAL_TONS"], computed_tons)

    return df, ac_gloss, weap_gloss

def export_parquet(df):
    print(f"\nExporting Parquet to {OUT_PARQUET}...")
    df.to_parquet(OUT_PARQUET, index=False, compression="snappy")
    size = os.path.getsize(OUT_PARQUET)
    print(f"Parquet saved: {size:,} bytes ({size / (1024*1024):.2f} MB).")

def export_csv_gz(df):
    print(f"\nExporting Gzipped CSV to {OUT_CSV_GZ}...")
    df.to_csv(OUT_CSV_GZ, index=False, compression="gzip")
    size = os.path.getsize(OUT_CSV_GZ)
    print(f"Gzipped CSV saved: {size:,} bytes ({size / (1024*1024):.2f} MB).")

def export_sqlite(df, ac_gloss, weap_gloss):
    print(f"\nExporting SQLite database to {OUT_SQLITE}...")
    if os.path.exists(OUT_SQLITE):
        os.remove(OUT_SQLITE)

    conn = sqlite3.connect(OUT_SQLITE)
    
    print("  Writing table 'missions'...")
    df.to_sql("missions", conn, index=False, if_exists="replace")
    
    print("  Writing table 'aircraft_glossary'...")
    ac_gloss.to_sql("aircraft_glossary", conn, index=False, if_exists="replace")

    print("  Writing table 'weapon_glossary'...")
    weap_gloss.to_sql("weapon_glossary", conn, index=False, if_exists="replace")

    print("  Creating database indexes for high-speed queries...")
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX idx_missions_date ON missions (mission_date_iso);")
    cursor.execute("CREATE INDEX idx_missions_year ON missions (year);")
    cursor.execute("CREATE INDEX idx_missions_theater ON missions (THEATER);")
    cursor.execute("CREATE INDEX idx_missions_country ON missions (country_flying_mission_clean);")
    cursor.execute("CREATE INDEX idx_missions_target_country ON missions (TGT_COUNTRY);")
    cursor.execute("CREATE INDEX idx_missions_target_loc ON missions (TGT_LOCATION);")
    cursor.execute("CREATE INDEX idx_missions_aircraft ON missions (aircraft_full_name);")
    cursor.execute("CREATE INDEX idx_missions_category ON missions (aircraft_category);")
    cursor.execute("CREATE INDEX idx_missions_coords ON missions (target_lat, target_lon);")
    cursor.execute("CREATE INDEX idx_missions_theater_year ON missions (THEATER, year);")
    
    print("  Creating aggregated targets summary view...")
    cursor.execute("""
        CREATE TABLE targets_summary AS
        SELECT 
            TGT_COUNTRY as target_country,
            TGT_LOCATION as target_location,
            THEATER as theater,
            ROUND(AVG(target_lat), 4) as avg_lat,
            ROUND(AVG(target_lon), 4) as avg_lon,
            COUNT(*) as mission_count,
            ROUND(SUM(total_tons_clean), 2) as total_tons,
            ROUND(SUM(TONS_OF_HE), 2) as he_tons,
            ROUND(SUM(TONS_OF_IC), 2) as ic_tons,
            ROUND(SUM(TONS_OF_FRAG), 2) as frag_tons,
            MIN(mission_date_iso) as first_mission,
            MAX(mission_date_iso) as last_mission
        FROM missions
        WHERE has_valid_target_coords = 1
        GROUP BY TGT_COUNTRY, TGT_LOCATION, THEATER
        ORDER BY total_tons DESC;
    """)
    cursor.execute("CREATE INDEX idx_tgt_summary_tons ON targets_summary (total_tons DESC);")
    cursor.execute("CREATE INDEX idx_tgt_summary_loc ON targets_summary (target_country, target_location);")
    
    conn.commit()
    conn.close()

    size = os.path.getsize(OUT_SQLITE)
    print(f"SQLite database saved: {size:,} bytes ({size / (1024*1024):.2f} MB).")

def export_geojson(df):
    print(f"\nGenerating aggregated targets GeoJSON: {OUT_TARGETS_GEOJSON}...")
    valid_tgt_df = df[df["has_valid_target_coords"]].copy()

    # Aggregate by rounded coordinates + location to produce high quality point layer
    grouped = valid_tgt_df.groupby(["target_lat", "target_lon", "TGT_COUNTRY", "TGT_LOCATION", "THEATER"]).agg(
        mission_count=("WWII_ID", "count"),
        total_tons=("total_tons_clean", "sum"),
        he_tons=("TONS_OF_HE", "sum"),
        ic_tons=("TONS_OF_IC", "sum"),
        frag_tons=("TONS_OF_FRAG", "sum"),
        first_date=("mission_date_iso", "min"),
        last_date=("mission_date_iso", "max"),
        primary_aircraft=("aircraft_full_name", lambda s: s.mode().iloc[0] if not s.empty and not s.mode().empty else "Unknown"),
        primary_country=("country_flying_mission_clean", lambda s: s.mode().iloc[0] if not s.empty and not s.mode().empty else "Unknown")
    ).reset_index()

    features = []
    for _, row in grouped.iterrows():
        feat = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [round(row["target_lon"], 4), round(row["target_lat"], 4)]
            },
            "properties": {
                "target_location": clean_str(row["TGT_LOCATION"]) or "Unknown",
                "target_country": clean_str(row["TGT_COUNTRY"]) or "Unknown",
                "theater": clean_str(row["THEATER"]) or "Unknown",
                "mission_count": int(row["mission_count"]),
                "total_tons": round(float(row["total_tons"]), 2),
                "he_tons": round(float(row["he_tons"]), 2),
                "ic_tons": round(float(row["ic_tons"]), 2),
                "frag_tons": round(float(row["frag_tons"]), 2),
                "first_date": row["first_date"],
                "last_date": row["last_date"],
                "primary_aircraft": clean_str(row["primary_aircraft"]) or "Unknown",
                "primary_country": clean_str(row["primary_country"]) or "Unknown"
            }
        }
        features.append(feat)

    geojson = {
        "type": "FeatureCollection",
        "name": "wwii_thor_targets_aggregated",
        "features": features
    }
    with open(OUT_TARGETS_GEOJSON, "w", encoding="utf-8") as f:
        json.dump(geojson, f, separators=(",", ":"))
    size = os.path.getsize(OUT_TARGETS_GEOJSON)
    print(f"Target GeoJSON saved: {len(features):,} target clusters ({size / (1024*1024):.2f} MB).")

    print(f"\nGenerating flight paths GeoJSON: {OUT_FLIGHT_PATHS_GEOJSON}...")
    fp_df = df[df["has_flight_path"]].copy()
    fp_features = []
    for _, row in fp_df.iterrows():
        feat = {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [round(row["takeoff_lon"], 4), round(row["takeoff_lat"], 4)],
                    [round(row["target_lon"], 4), round(row["target_lat"], 4)]
                ]
            },
            "properties": {
                "mission_id": int(row["WWII_ID"]) if pd.notna(row["WWII_ID"]) else None,
                "date": row["mission_date_iso"],
                "theater": clean_str(row["THEATER"]),
                "aircraft": clean_str(row["aircraft_full_name"]),
                "takeoff_base": clean_str(row["TAKEOFF_BASE"]),
                "target_location": clean_str(row["TGT_LOCATION"]),
                "target_country": clean_str(row["TGT_COUNTRY"]),
                "total_tons": round(float(row["total_tons_clean"]), 2)
            }
        }
        fp_features.append(feat)

    fp_geojson = {
        "type": "FeatureCollection",
        "name": "wwii_thor_flight_paths",
        "features": fp_features
    }
    with open(OUT_FLIGHT_PATHS_GEOJSON, "w", encoding="utf-8") as f:
        json.dump(fp_geojson, f, separators=(",", ":"))
    fpsize = os.path.getsize(OUT_FLIGHT_PATHS_GEOJSON)
    print(f"Flight paths GeoJSON saved: {len(fp_features):,} flight vectors ({fpsize / (1024*1024):.2f} MB).")

def main():
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(GIS_DIR, exist_ok=True)
    
    start_time = datetime.now()
    print("=" * 60)
    print("STARTING WWII THOR DATASET BUILD AND ENRICHMENT")
    print("=" * 60)
    
    df, ac_gloss, weap_gloss = load_and_enrich()
    
    export_parquet(df)
    export_csv_gz(df)
    export_sqlite(df, ac_gloss, weap_gloss)
    export_geojson(df)
    
    duration = datetime.now() - start_time
    print("=" * 60)
    print(f"BUILD COMPLETE in {duration.total_seconds():.2f} seconds!")
    print("=" * 60)

if __name__ == "__main__":
    main()

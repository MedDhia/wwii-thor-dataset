#!/usr/bin/env python3
"""
verify_dataset.py - Validate the generated WWII THOR assets.
"""

import os
import sys
import json
import time
import sqlite3
import pandas as pd

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
GIS_DIR = os.path.join(BASE_DIR, "data", "gis")

PARQUET_FILE = os.path.join(PROCESSED_DIR, "thor_wwii_enriched.parquet")
SQLITE_FILE = os.path.join(PROCESSED_DIR, "thor_wwii.sqlite")
CSV_GZ_FILE = os.path.join(PROCESSED_DIR, "thor_wwii_clean.csv.gz")
TARGETS_GEOJSON = os.path.join(GIS_DIR, "targets_aggregated.geojson")
FLIGHT_PATHS_GEOJSON = os.path.join(GIS_DIR, "flight_paths.geojson")

def test_parquet():
    print("=== Testing Parquet File ===")
    t0 = time.time()
    df = pd.read_parquet(PARQUET_FILE)
    dur = time.time() - t0
    print(f"Read {len(df):,} rows and {len(df.columns)} columns in {dur*1000:.1f} ms.")
    assert len(df) == 178281, f"Expected 178,281 rows, got {len(df)}"
    assert "mission_date_iso" in df.columns
    assert "aircraft_full_name" in df.columns
    assert "has_valid_target_coords" in df.columns
    assert "total_tons_clean" in df.columns
    
    # Check date coverage
    years = sorted(df["year"].dropna().unique())
    print(f"Covered years: {years}")
    assert years == [1939, 1940, 1941, 1942, 1943, 1944, 1945]
    print("Parquet verification PASSED!\n")

def test_sqlite():
    print("=== Testing SQLite Database ===")
    if not os.path.exists(SQLITE_FILE) and os.path.exists(SQLITE_FILE + ".gz"):
        import gzip, shutil
        print("Decompressing thor_wwii.sqlite.gz...")
        with gzip.open(SQLITE_FILE + ".gz", "rb") as f_in:
            with open(SQLITE_FILE, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
    conn = sqlite3.connect(SQLITE_FILE)
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cursor.fetchall()]
    print(f"Tables found: {tables}")
    assert "missions" in tables
    assert "aircraft_glossary" in tables
    assert "weapon_glossary" in tables
    assert "targets_summary" in tables

    # Row count
    cursor.execute("SELECT COUNT(*) FROM missions;")
    count = cursor.fetchone()[0]
    print(f"Missions count: {count:,}")
    assert count == 178281

    # Check indexes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
    indexes = [r[0] for r in cursor.fetchall()]
    print(f"Indexes created: {len(indexes)}")

    # Benchmark analytical queries
    print("\nBenchmark Query 1: Total Bomb Tonnage by Theater")
    t0 = time.time()
    cursor.execute("""
        SELECT THEATER, COUNT(*) as missions, ROUND(SUM(total_tons_clean), 1) as total_tons
        FROM missions
        GROUP BY THEATER
        ORDER BY total_tons DESC;
    """)
    rows = cursor.fetchall()
    dur = (time.time() - t0) * 1000
    for r in rows:
        print(f"  {r[0] or 'UNASSIGNED':<12}: {r[1]:>6,} missions | {r[2]:>10,.1f} tons")
    print(f"Query executed in {dur:.2f} ms.")

    print("\nBenchmark Query 2: Top 10 Heaviest Bombing Targets")
    t0 = time.time()
    cursor.execute("""
        SELECT target_country, target_location, theater, mission_count, total_tons, first_mission, last_mission
        FROM targets_summary
        LIMIT 10;
    """)
    rows = cursor.fetchall()
    dur = (time.time() - t0) * 1000
    for r in rows:
        print(f"  {r[1] or 'Unknown'} ({r[0] or 'Unknown'}, {r[2]}): {r[4]:,.1f} tons ({r[3]:,} missions) [{r[5]} to {r[6]}]")
    print(f"Query executed in {dur:.2f} ms.")

    print("\nBenchmark Query 3: Top Aircraft Models by Total Missions")
    t0 = time.time()
    cursor.execute("""
        SELECT aircraft_full_name, aircraft_category, COUNT(*) as missions, ROUND(SUM(total_tons_clean), 1) as total_tons
        FROM missions
        WHERE aircraft_full_name IS NOT NULL
        GROUP BY aircraft_full_name, aircraft_category
        ORDER BY missions DESC
        LIMIT 10;
    """)
    rows = cursor.fetchall()
    dur = (time.time() - t0) * 1000
    for r in rows:
        print(f"  {r[0]:<28} | {r[1] or 'Unknown':<35} | {r[2]:>6,} missions | {r[3]:>10,.1f} tons")
    print(f"Query executed in {dur:.2f} ms.")

    conn.close()
    print("\nSQLite verification PASSED!\n")

def test_geojson():
    print("=== Testing GeoJSON Exports ===")
    with open(TARGETS_GEOJSON, "r") as f:
        tgt_data = json.load(f)
    assert tgt_data["type"] == "FeatureCollection"
    print(f"Targets GeoJSON features: {len(tgt_data['features']):,}")
    sample_feat = tgt_data["features"][0]
    print(f"Sample target properties: {sample_feat['properties']}")

    with open(FLIGHT_PATHS_GEOJSON, "r") as f:
        fp_data = json.load(f)
    assert fp_data["type"] == "FeatureCollection"
    print(f"Flight Paths GeoJSON features: {len(fp_data['features']):,}")
    sample_fp = fp_data["features"][0]
    print(f"Sample flight path properties: {sample_fp['properties']}")
    print("GeoJSON verification PASSED!\n")

def main():
    print("=" * 60)
    print("RUNNING AUTOMATED VERIFICATION SUITE")
    print("=" * 60)
    test_parquet()
    test_sqlite()
    test_geojson()
    print("=" * 60)
    print("ALL VERIFICATION CHECKS PASSED!")
    print("=" * 60)

if __name__ == "__main__":
    main()

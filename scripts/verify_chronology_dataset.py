#!/usr/bin/env python3
"""
verify_chronology_dataset.py

Verification suite for the USAAF Combat Chronology (1941–1945) dataset.
Checks database consistency, relational schemas, cross-referencing views, and Parquet/CSV exports.
"""

import os
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
SQLITE_PATH = os.path.join(PROCESSED_DIR, "usaaf_combat_chronology.sqlite")
PARQUET_PATH = os.path.join(PROCESSED_DIR, "usaaf_chronology_events.parquet")
DAYS_CSV_GZ = os.path.join(PROCESSED_DIR, "usaaf_chronology_days.csv.gz")
TN_CSV = os.path.join(BASE_DIR, "data", "gis", "tunisia_wwii_combat_chronology.csv")

def verify_all():
    print("==================================================")
    print("1. VERIFYING SQLITE DATABASE INTEGRITY & SCHEMAS")
    print("==================================================")
    assert os.path.exists(SQLITE_PATH), f"SQLite database not found at {SQLITE_PATH}"
    
    conn = sqlite3.connect(SQLITE_PATH)
    cur = conn.cursor()
    
    # Check tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = set([r[0] for r in cur.fetchall()])
    expected_tables = {
        'chronology_days', 'chronology_events', 'chronology_missions',
        'chronology_aerial_combat', 'chronology_casualties',
        'chronology_unit_movements', 'thor_daily_summary'
    }
    print(f"Tables present: {tables}")
    assert expected_tables.issubset(tables), f"Missing tables: {expected_tables - tables}"
    
    # Verify counts
    counts = {}
    for tbl in expected_tables:
        cur.execute(f"SELECT COUNT(*) FROM {tbl};")
        counts[tbl] = cur.fetchone()[0]
        print(f"  • {tbl}: {counts[tbl]:,} records")
        
    # Day-level consistency: one row per date, printed weekday matches the calendar,
    # and events_count adds up to the events table.
    df_days_db = pd.read_sql("SELECT date, day_of_week, events_count FROM chronology_days", conn)
    dup_dates = df_days_db['date'][df_days_db['date'].duplicated()].tolist()
    assert not dup_dates, f"Duplicate day entries: {dup_dates}"
    bad_wd = df_days_db[pd.to_datetime(df_days_db['date']).dt.day_name() != df_days_db['day_of_week']]
    assert bad_wd.empty, f"Weekday does not match date: {bad_wd['date'].tolist()}"
    assert df_days_db['events_count'].sum() == counts['chronology_events'], "events_count does not match chronology_events"
    assert counts['chronology_days'] >= 1300, f"Expected 1,300+ days, got {counts['chronology_days']}"

    # Event-level consistency: IDs embed the event date; no page footers parsed as events;
    # every child record points at an existing event with the same date.
    cur.execute("SELECT COUNT(*) FROM chronology_events WHERE substr(event_id, 5, 8) != replace(date, '-', '')")
    assert cur.fetchone()[0] == 0, "event_id date tag does not match event date"
    cur.execute("SELECT COUNT(*) FROM chronology_events WHERE event_text LIKE 'SOURCES:%' "
                "OR event_text LIKE 'Jack McKillop%' OR event_text LIKE '-----%'")
    assert cur.fetchone()[0] == 0, "Page footer text found in chronology_events"
    for child in ['chronology_missions', 'chronology_aerial_combat', 'chronology_casualties', 'chronology_unit_movements']:
        cur.execute(f"SELECT COUNT(*) FROM {child} c LEFT JOIN chronology_events e ON c.event_id = e.event_id "
                    f"WHERE e.event_id IS NULL OR c.date != e.date")
        assert cur.fetchone()[0] == 0, f"{child} has orphaned or mis-dated rows"
    assert counts['chronology_events'] >= 8500, f"Expected 8,500+ events, got {counts['chronology_events']}"
    assert counts['chronology_missions'] >= 2000, f"Expected 2,000+ missions, got {counts['chronology_missions']}"
    assert counts['chronology_aerial_combat'] >= 700, f"Expected 700+ combat logs, got {counts['chronology_aerial_combat']}"
    assert counts['chronology_unit_movements'] >= 1000, f"Expected 1,000+ unit moves, got {counts['chronology_unit_movements']}"
    
    # Check indexes
    cur.execute("SELECT name FROM sqlite_master WHERE type='index';")
    indexes = [r[0] for r in cur.fetchall()]
    print(f"\nIndexes created: {len(indexes)}")
    assert len(indexes) >= 10, "Relational indexes incomplete."
    
    print("\n==================================================")
    print("2. VERIFYING CROSS-REFERENCING BRIDGE (THOR + USAAF)")
    print("==================================================")
    cur.execute("SELECT name FROM sqlite_master WHERE type='view';")
    views = [r[0] for r in cur.fetchall()]
    print(f"Views present: {views}")
    assert 'v_daily_operational_crosswalk' in views, "Crosswalk view missing."
    
    cur.execute("""
        SELECT date, day_of_week, theaters_active, usaaf_events_count, thor_bombing_missions, thor_tons_dropped
        FROM v_daily_operational_crosswalk
        WHERE date = '1944-06-06';
    """)
    dday = cur.fetchone()
    print(f"D-Day (1944-06-06) verification: {dday}")
    assert dday[4] > 500, f"Expected >500 THOR missions on D-Day, got {dday[4]}"
    assert dday[5] > 20000.0, f"Expected >20,000 tons on D-Day, got {dday[5]}"
    
    print("\n==================================================")
    print("3. VERIFYING PARQUET & COMPRESSED CSV EXPORTS")
    print("==================================================")
    assert os.path.exists(PARQUET_PATH), f"Parquet file missing: {PARQUET_PATH}"
    df_parquet = pd.read_parquet(PARQUET_PATH)
    print(f"Parquet events: {len(df_parquet):,} rows, {len(df_parquet.columns)} columns.")
    assert len(df_parquet) == counts['chronology_events']
    
    df_days = pd.read_csv(DAYS_CSV_GZ)
    print(f"Days CSV: {len(df_days):,} days from {df_days['date'].min()} to {df_days['date'].max()}.")
    assert len(df_days) == counts['chronology_days']
    
    print("\n==================================================")
    print("4. VERIFYING TUNISIA SUBSET EXPORT")
    print("==================================================")
    assert os.path.exists(TN_CSV), f"Tunisia CSV missing: {TN_CSV}"
    df_tn = pd.read_csv(TN_CSV)
    print(f"Tunisia operational events: {len(df_tn):,} records.")
    assert len(df_tn) >= 250, f"Expected >=250 Tunisia records, got {len(df_tn)}"
    
    conn.close()
    print("\n>>> ALL VERIFICATION TESTS PASSED SUCCESSFULLY! <<<\n")

if __name__ == "__main__":
    verify_all()

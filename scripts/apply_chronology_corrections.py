#!/usr/bin/env python3
"""
apply_chronology_corrections.py

Applies build_chronology_dataset.apply_corrections() to the committed
usaaf_combat_chronology.sqlite and regenerates every derived export
(SQLite/.gz, Parquet, CSV.GZ, Tunisia subset, docs/chronology_data.js).

Use this when the raw aircrewremembered.com HTML mirror is not available;
with the mirror, run build_chronology_dataset.py instead (it applies the
same corrections during parsing).

Year typos: the printed weekday is compared with the calendar. A day is
re-dated only when (a) its printed weekday fits a different year and (b) an
adjacent entry is the calendar day right before or after the re-dated date,
e.g. "SATURDAY, 2 JANUARY 1942" followed by 3 January 1943. The day and all its
child records are re-dated; headers that fail either test are weekday typos.
"""

import os
import sqlite3
import sys

from datetime import date, timedelta

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_chronology_dataset as bcd  # noqa: E402

DB_PATH = os.path.join(bcd.PROCESSED_DIR, "usaaf_combat_chronology.sqlite")
CHILD_TABLES = [
    ("chronology_missions", "mission_id"),
    ("chronology_aerial_combat", "combat_id"),
    ("chronology_casualties", "casualty_id"),
    ("chronology_unit_movements", "movement_id"),
]


def load_tables():
    conn = sqlite3.connect(DB_PATH)
    days = pd.read_sql("SELECT * FROM chronology_days ORDER BY rowid", conn)
    events = pd.read_sql("SELECT * FROM chronology_events ORDER BY rowid", conn)
    children = [pd.read_sql(f"SELECT * FROM {t} ORDER BY rowid", conn) for t, _ in CHILD_TABLES]
    conn.close()
    return days, events, children


def attach_day_seq(days, events):
    """Events were written in parse order, days after their events: rebuild the link."""
    seq = [i for i, n in enumerate(days["events_count"]) for _ in range(int(n))]
    assert len(seq) == len(events), "events_count does not add up to the events table"
    events = events.copy()
    events["_day_seq"] = seq
    assert (events["date"].values == days["date"].values[seq]).all(), "event/day alignment failed"
    return events


def redate(days, events, children):
    days = days.copy()
    events = events.copy()
    children = [c.copy() for c in children]
    for i in range(len(days)):
        d = days.loc[i]
        y, m, dd = (int(x) for x in d["date"].split("-"))
        adjacent = {days.loc[j, "date"] for j in (i - 1, i + 1) if 0 <= j < len(days)}
        neighbours = [int(x[:4]) for x in sorted(adjacent)]
        new_y = bcd.repair_year(y, m, dd, d["day_of_week"], neighbours)
        if new_y == y:
            continue
        cand = date(new_y, m, dd)
        if not {str(cand - timedelta(days=1)), str(cand + timedelta(days=1))} & adjacent:
            continue
        old_iso, new_iso = d["date"], cand.isoformat()
        old_tag, new_tag = old_iso.replace("-", ""), new_iso.replace("-", "")
        print(f"  re-dating {old_iso} ({d['day_of_week']}) -> {new_iso}")
        days.loc[i, ["date", "year"]] = [new_iso, new_y]

        ev_mask = events["_day_seq"] == i
        old_ids = set(events.loc[ev_mask, "event_id"])
        events.loc[ev_mask, "date"] = new_iso
        events.loc[ev_mask, "year"] = new_y
        events.loc[ev_mask, "event_id"] = events.loc[ev_mask, "event_id"].str.replace(old_tag, new_tag, n=1)
        for c, (_, id_col) in zip(children, CHILD_TABLES):
            cm = c["event_id"].isin(old_ids)
            c.loc[cm, "date"] = new_iso
            c.loc[cm, "event_id"] = c.loc[cm, "event_id"].str.replace(old_tag, new_tag, n=1)
            c.loc[cm, id_col] = c.loc[cm, id_col].str.replace(old_tag, new_tag, n=1)
    return days, events, children


def main():
    days, events, children = load_tables()
    print(f"Loaded {len(days):,} days, {len(events):,} events.")
    events = attach_day_seq(days, events)
    days, events, children = redate(days, events, children)
    days, events, *children = bcd.apply_corrections(days, events, *children)
    assert not days["date"].duplicated().any(), "duplicate dates remain"
    print(f"Now {len(days):,} days, {len(events):,} events, "
          + ", ".join(f"{t}={len(c):,}" for (t, _), c in zip(CHILD_TABLES, children)))

    bcd.build_database(days, events, *children)
    bcd.export_tunisia_subset(events, children[0], children[3])
    bcd.export_explorer_js()


if __name__ == "__main__":
    main()

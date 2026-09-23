#!/usr/bin/env python3
"""
build_tunisia_imada_stats.py - Aggregate THOR strikes in Tunisia by Imada (sector).

Point-in-polygon join of every THOR record with TGT_COUNTRY == TUNISIA and valid
target coordinates against data/gis/tunisia_imadas/TN_sectors.shp (2,084 sectors).
Strikes whose coordinates fall outside every sector polygon (offshore targets, or
records with mis-coded coordinates) are counted and reported but not assigned.

Output: data/gis/tunisia_bombing_by_imada.csv (UTF-8), one row per bombed Imada,
sorted by total tonnage.
"""

import os
import re

import pandas as pd
import shapefile
from shapely.geometry import Point, shape
from shapely.strtree import STRtree

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PARQUET = os.path.join(BASE_DIR, "data", "processed", "thor_wwii_enriched.parquet")
SECTORS_SHP = os.path.join(BASE_DIR, "data", "gis", "tunisia_imadas", "TN_sectors")
OUT_CSV = os.path.join(BASE_DIR, "data", "gis", "tunisia_bombing_by_imada.csv")

# Bidirectional-text control characters present in some shapefile name fields.
BIDI_RE = re.compile("[‎‏‪-‮]")


def clean_name(val):
    return BIDI_RE.sub("", str(val)).strip()


def main():
    reader = shapefile.Reader(SECTORS_SHP, encoding="utf-8")
    fields = [f[0] for f in reader.fields[1:]]
    sectors = pd.DataFrame(reader.records(), columns=fields)
    geoms = [shape(s.__geo_interface__) for s in reader.shapes()]
    tree = STRtree(geoms)

    df = pd.read_parquet(PARQUET)
    tn = df[df["TGT_COUNTRY"].astype(str).str.upper().str.contains("TUNIS") & df["has_valid_target_coords"]].copy()
    for col in ["TONS_OF_HE", "TONS_OF_FRAG", "TONS_OF_IC"]:
        tn[col] = pd.to_numeric(tn[col], errors="coerce").fillna(0)

    def locate(lon, lat):
        hits = tree.query(Point(lon, lat), predicate="within")
        return int(sectors.at[int(hits[0]), "sec_uid"]) if len(hits) else None

    tn["imada_uid"] = [locate(x, y) for x, y in zip(tn["target_lon"], tn["target_lat"])]
    unmatched = tn["imada_uid"].isna().sum()
    tn = tn.dropna(subset=["imada_uid"])
    tn["imada_uid"] = tn["imada_uid"].astype(int)

    stats = tn.groupby("imada_uid").agg(
        bomb_strikes=("WWII_ID", "size"),
        total_bomb_tons=("total_tons_clean", "sum"),
        tons_he=("TONS_OF_HE", "sum"),
        tons_frag=("TONS_OF_FRAG", "sum"),
        tons_ic=("TONS_OF_IC", "sum"),
        first_raid=("mission_date_iso", "min"),
        last_raid=("mission_date_iso", "max"),
    ).reset_index()

    names = pd.DataFrame({
        "imada_uid": sectors["sec_uid"].astype(int),
        "governorate_name_en": sectors["gov_en"].map(clean_name),
        "governorate_name_ar": sectors["gov_ar"].map(clean_name),
        "delegation_name_en": sectors["dl_n_2018"].map(clean_name),
        "delegation_name_ar": sectors["dl_r_2018"].map(clean_name),
        "imada_name_en": sectors["sec_en"].map(clean_name),
        "imada_name_ar": sectors["sec_ar"].map(clean_name),
    })
    out = names.merge(stats, on="imada_uid", how="inner")
    out = out[[
        "governorate_name_en", "governorate_name_ar", "delegation_name_en", "delegation_name_ar",
        "imada_name_en", "imada_name_ar", "imada_uid", "bomb_strikes", "total_bomb_tons",
        "tons_he", "tons_frag", "tons_ic", "first_raid", "last_raid",
    ]]
    for col in ["total_bomb_tons", "tons_he", "tons_frag", "tons_ic"]:
        out[col] = out[col].round(2)
    out = out.sort_values(["total_bomb_tons", "imada_uid"], ascending=[False, True])
    out.to_csv(OUT_CSV, index=False, encoding="utf-8", quoting=1)

    print(f"Tunisia strikes with valid coordinates: {len(tn) + unmatched:,}")
    print(f"  assigned to an Imada: {len(tn):,} across {len(out)} Imadas")
    print(f"  outside every Imada polygon: {unmatched:,}")
    print(f"Saved: {OUT_CSV}")


if __name__ == "__main__":
    main()

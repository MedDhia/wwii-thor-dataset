#!/usr/bin/env python3
"""
fetch_data.py - Fetch raw WWII THOR dataset and reference glossaries.
"""

import os
import sys
import urllib.request

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

FILES = [
    {
        "name": "THOR_WWII_DATA_CLEAN.csv",
        "url": "https://raw.githubusercontent.com/dlozeve/ww2-bombings/master/THOR_WWII_DATA_CLEAN.csv",
        "expected_min_bytes": 35_000_000,
    },
    {
        "name": "THOR_WWII_AIRCRAFT_GLOSS.csv",
        "url": "https://raw.githubusercontent.com/dlozeve/ww2-bombings/master/THOR_WWII_AIRCRAFT_GLOSS.csv",
        "expected_min_bytes": 5_000,
    },
    {
        "name": "THOR_WWII_WEAPON_GLOSS.csv",
        "url": "https://raw.githubusercontent.com/dlozeve/ww2-bombings/master/THOR_WWII_WEAPON_GLOSS.csv",
        "expected_min_bytes": 5_000,
    },
]

def download_file(url: str, dest_path: str, expected_min_bytes: int):
    print(f"Fetching {os.path.basename(dest_path)} from {url}...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req) as resp, open(dest_path, "wb") as f:
        total = 0
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)
            total += len(chunk)
            print(f"  Downloaded {total / (1024*1024):.2f} MB...", end="\r", flush=True)
    print()
    size = os.path.getsize(dest_path)
    print(f"  Complete: {size:,} bytes saved to {dest_path}")
    if size < expected_min_bytes:
        raise ValueError(f"Downloaded file {dest_path} is smaller than expected ({size} < {expected_min_bytes})")

def main():
    os.makedirs(RAW_DIR, exist_ok=True)
    print(f"Raw data target directory: {RAW_DIR}")
    for item in FILES:
        dest = os.path.join(RAW_DIR, item["name"])
        if os.path.exists(dest) and os.path.getsize(dest) >= item["expected_min_bytes"]:
            print(f"File {item['name']} already exists ({os.path.getsize(dest):,} bytes), skipping.")
        else:
            download_file(item["url"], dest, item["expected_min_bytes"])
    print("\nAll raw dataset files successfully acquired!")

if __name__ == "__main__":
    main()

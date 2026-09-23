#!/usr/bin/env python3
"""
build_chronology_dataset.py

Constructs the USAAF Combat Chronology (1941–1945) dataset by regex-parsing the
day-by-day narrative text (see Source below).

Extracts:
1. chronology_days (one row per dated day entry in the source)
2. chronology_events (operational narratives categorized by theater and air force)
3. chronology_missions (structured missions with sortie dispatched/attacking counts & targets)
4. chronology_aerial_combat (dogfight scorecards with D-P-D claims & aircraft attrition)
5. chronology_casualties (daily KIA, WIA, MIA tallies and named aviators)
6. chronology_unit_movements (order of battle airfield-to-airfield relocations)

Outputs:
- SQLite: data/processed/usaaf_combat_chronology.sqlite (+ .sqlite.gz)
- Parquet: data/processed/usaaf_chronology_events.parquet
- CSVs: data/processed/usaaf_chronology_*.csv.gz
- Tunisia: data/gis/tunisia_wwii_combat_chronology.csv
- Explorer: docs/chronology_data.js

Source: Jack McKillop's day-by-day USAAF combat operations chronology (based on
Kit C. Carter and Robert Mueller, "The Army Air Forces in World War II: Combat
Chronology, 1941-1945"), as published at aircrewremembered.com. Point
USAAF_CHRONOLOGY_HTML_DIR (or the first CLI argument) at a local mirror of
https://aircrewremembered.com/USAAFCombatOperations/.

The committed database has been corrected in place with
scripts/apply_chronology_corrections.py, which applies the same
apply_corrections() step defined here.
"""

import os
import re
import glob
import json
import sqlite3
import gzip
import shutil
from datetime import datetime
import sys
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_HTML_DIR = os.environ.get(
    "USAAF_CHRONOLOGY_HTML_DIR",
    "/Users/mohameddhiahammami/Downloads/us.sitesucker.mac.sitesucker/aircrewremembered.com/USAAFCombatOperations"
)
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
GIS_DIR = os.path.join(BASE_DIR, "data", "gis")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
MAPSTN_DIR = os.environ.get("MAPSTN_DIR", "/Users/mohameddhiahammami/.gemini/antigravity/scratch/MapsTN")

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(GIS_DIR, exist_ok=True)

MONTH_MAP = {
    'JANUARY': 1, 'FEBRUARY': 2, 'MARCH': 3, 'APRIL': 4, 'MAY': 5, 'JUNE': 6,
    'JULY': 7, 'AUGUST': 8, 'SEPTEMBER': 9, 'OCTOBER': 10, 'NOVEMBER': 11, 'DECEMBER': 12
}

DATE_RE = re.compile(
    r'^(SUNDAY|MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY),\s+(\d{1,2})\s+([A-Z]+)\s+(\d{4})',
    re.M
)

THEATER_HEADER_RE = re.compile(
    r'^(AMERICAN THEATER OF OPERATIONS|CHINA-BURMA-INDIA(?:\s+\(CBI\))?\s+THEATER OF OPERATIONS|'
    r'EUROPEAN THEATER OF OPERATIONS(?:\s+\(ETO\))?|MEDITERRANEAN THEATER OF OPERATIONS(?:\s+\(MTO\))?|'
    r'PACIFIC OCEAN AREA(?:\s+\(POA\))?|SOUTH PACIFIC AREA(?:\s+\(SOPAC\))?|'
    r'SOUTHWEST PACIFIC AREA(?:\s+\(SWPA\))?|SOUTHWEST PACIFIC THEATER OF OPERATIONS|'
    r'CENTRAL PACIFIC|WESTERN PACIFIC|TWENTIETH AIR FORCE|FAR EAST AIR FORCES|'
    r'STRATEGIC OPERATIONS|TACTICAL OPERATIONS|ZONE OF INTERIOR|MIDDLE EAST|ASW OPERATIONS)',
    re.M | re.I
)

AIR_FORCE_RE = re.compile(
    r'\b(First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth|Eleventh|'
    r'Twelfth|Thirteenth|Fourteenth|Fifteenth|Twentieth)\s+Air\s+Force\b|'
    r'\b(NAAF|NASAF|NATAF|NACAF|FEAF|USASTAF|USAMEAF|AAF Antisubmarine Command)\b',
    re.I
)

COMMAND_RE = re.compile(
    r'\b(VIII\s+Bomber\s+Command|VIII\s+Fighter\s+Command|VIII\s+Air\s+Support\s+Command|'
    r'XII\s+Air\s+Support\s+Command|XII\s+Bomber\s+Command|XII\s+Fighter\s+Command|'
    r'India\s+Air\s+Task\s+Force|China\s+Air\s+Task\s+Force|Iceland\s+Base\s+Command)\b',
    re.I
)

SUB_REGION_RE = re.compile(
    r'\b(?:In\s+)?(Tunisia|French\s+Morocco|Morocco|Algeria|Libya|Egypt|Italy|Sicily|Sardinia|'
    r'Corsica|France|Germany|Belgium|Netherlands|Holland|Austria|Yugoslavia|Greece|Crete|'
    r'Burma|India|China|French\s+Indochina|Thailand|New\s+Guinea|Solomon\s+Islands|'
    r'Bismarck\s+Archipelago|Philippines|Marianas|Bonin\s+Islands|Ryukyu\s+Islands|Japan|'
    r'Aleutian\s+Islands|Aleutians|Kuril\s+Islands)\b',
    re.I
)

AC_MODEL_RE = re.compile(
    r'\b(B-17|B-24|B-25|B-26|B-29|A-20|A-26|P-38|P-39|P-40|P-47|P-51|C-47|Spitfire|Lancaster|Wellington|Beaufighter|Mosquito)(?:\'s|s)?\b',
    re.I
)

CLAIM_DPD_RE = re.compile(
    r'\bclaims?\s+(\d+)[–-](\d+)[–-](\d+)(?:\s+([A-Za-z0-9\s/-]+?)(?:aircraft|fighters|bombers))?\b',
    re.I
)

CLAIM_SINGLE_RE = re.compile(
    r'\bclaims?\s+(\d+)\s+([A-Za-z0-9\s/-]+?)\s+(?:shot down|destroyed)\b',
    re.I
)

CASUALTY_RE = re.compile(
    r'(\d+)\s*(?:airm[ae]n|casualties)?\s*(?:is|are)?\s*(KIA|WIA|MIA)\b',
    re.I
)

AC_WORD_PAT = r'(?:B-17|B-24|B-25|B-26|B-29|A-20|A-26|P-38|P-39|P-40|P-47|P-51|C-47|bombers?|fighters?|aircraft|airplanes?)(?:\'s|s)?'
LOST_RE = re.compile(rf'(\d+)\s+({AC_WORD_PAT})?\s*(?:is|are)?\s*lost', re.I)
DMG_REP_RE = re.compile(rf'(\d+)\s+({AC_WORD_PAT})?\s*(?:is|are)?\s*damaged\s+beyond\s+repair', re.I)
DMG_RE = re.compile(rf'(\d+)\s+({AC_WORD_PAT})?\s*(?:is|are)?\s*damaged(?!\s+beyond\s+repair)', re.I)

UNIT_MOVE_RE = re.compile(
    r'((?:HQ\s+)?[0-9A-Za-z\s\(\)]+?(?:Squadron|Group|Wing|Flight|Command|Detachment)[^\.,;]*?)\s+'
    r'(moves?|transfers?|arrives?|begins?\s+operating)\s+'
    r'(?:from\s+([^,\n;]+(?:,[^,\n;]+)?)\s+to\s+([^,\n;]+(?:,[^,\n;]+)?)|'
    r'(?:at|on)\s+([^,\n;]+(?:,[^,\n;]+)?)\s+from\s+([^,\n;]+(?:,[^,\n;]+)?)|'
    r'(?:at|on)\s+([^,\n;]+(?:,[^,\n;]+)?)|'
    r'(?:to|from)\s+([^,\n;]+(?:,[^,\n;]+)?))',
    re.I
)

MISSION_NUM_RE = re.compile(r'\bMission\s+(\d+)\b', re.I)
SORTIE_OF_RE = re.compile(r'(\d+)\s+of\s+(\d+)\s+([A-Za-z0-9-]+(?:\'s|s)?)\s+(?:bomb|hit|strike|attack|target|drop)\s+([^;\.\n]+)', re.I)
SORTIE_DIRECT_RE = re.compile(r'(?:^|\b)(\d+)\s+([A-Za-z0-9-]+(?:\'s|s)?)\s+(?:bomb|hit|strike|attack|drop)\s+([^;\.\n]+)', re.I)

# Page furniture repeated at the end of each monthly page (source list, compiler's
# signature box, separator rules). These are not operational events.
FOOTER_RE = re.compile(r'^(?:SOURCES:|Jack McKillop\b|-{5,}|\|)')

WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

def weekday_of(iso_date):
    return WEEKDAYS[datetime.strptime(iso_date, "%Y-%m-%d").weekday()]

def repair_year(year, month, day, day_name, candidate_years):
    """Return a corrected year when the printed weekday only fits a candidate year.

    The source has year typos in some day headers (e.g. "SATURDAY, 2 JANUARY 1942"
    inside the January 1943 page). The printed weekday is used to confirm the fix;
    headers whose weekday fits no candidate are left as printed (weekday typo).
    """
    def fits(y):
        try:
            return WEEKDAYS[datetime(y, month, day).weekday()].upper() == day_name.upper()
        except ValueError:
            return False
    if fits(year):
        return year
    for y in candidate_years:
        if y and y != year and fits(y):
            return y
    return year

def standardize_theater(raw_name):
    u = raw_name.upper()
    if 'EUROPEAN' in u or 'ETO' in u:
        return 'ETO'
    elif 'MEDITERRANEAN' in u or 'MTO' in u or 'MIDDLE EAST' in u:
        return 'MTO'
    elif 'CHINA-BURMA-INDIA' in u or 'CBI' in u:
        return 'CBI'
    elif 'SOUTHWEST PACIFIC' in u or 'SWPA' in u:
        return 'SWPA'
    elif 'SOUTH PACIFIC' in u or 'SOPAC' in u:
        return 'SOPAC'
    elif 'PACIFIC OCEAN' in u or 'POA' in u or 'CENTRAL PACIFIC' in u or 'WESTERN PACIFIC' in u:
        return 'POA'
    elif 'TWENTIETH' in u or 'USASTAF' in u:
        return 'USASTAF'
    elif 'AMERICAN' in u or 'ALASKA' in u or 'CARIBBEAN' in u or 'ASW' in u or 'ZONE OF INTERIOR' in u:
        return 'ATO'
    return 'OTHER'

def parse_corpus():
    files = sorted(glob.glob(os.path.join(RAW_HTML_DIR, '*.html')))
    files = [f for f in files if 'index.html' not in f]
    print(f"Ingesting {len(files)} monthly HTML files from {RAW_HTML_DIR}...")
    
    days_list = []
    events_list = []
    missions_list = []
    combat_list = []
    casualties_list = []
    movements_list = []
    
    event_idx = 0
    mission_idx = 0
    combat_idx = 0
    casualty_idx = 0
    movement_idx = 0
    
    for fpath in files:
        with open(fpath, encoding='utf-8', errors='ignore') as fp:
            content = fp.read()
            
        pre_match = re.search(r'<pre>(.*?)</pre>', content, re.S)
        text = pre_match.group(1) if pre_match else content
        
        date_matches = list(DATE_RE.finditer(text))
        for d_i, dm in enumerate(date_matches):
            day_name, day_num, month_name, year_str = dm.groups()
            mo = MONTH_MAP.get(month_name.upper(), 1)
            # Correct transcription typos in the year (e.g. 1993 -> 1943, or 1942
            # printed inside the 1943 page) using the page's year and the weekday.
            parsed_year = int(year_str)
            fname_yr = re.search(r'\.(\d{2})\.html', fpath)
            file_year = int("19" + fname_yr.group(1)) if fname_yr else None
            if parsed_year > 1945 and file_year:
                parsed_year = file_year
            parsed_year = repair_year(parsed_year, mo, int(day_num), day_name, [file_year])
            iso_date = f"{parsed_year:04d}-{mo:02d}-{int(day_num):02d}"
            
            start_pos = dm.end()
            end_pos = date_matches[d_i + 1].start() if d_i + 1 < len(date_matches) else len(text)
            day_text = text[start_pos:end_pos].strip()
            
            # Check for aircraft mentioned section
            ac_mentioned = ""
            ac_m = re.search(r'AIRCRAFT MENTIONED IN THIS REPORT:\s*(.*?)(?=\n\s*\n|[A-Z\s]{4,}:)', day_text, re.S)
            if ac_m:
                ac_mentioned = "; ".join([line.strip() for line in ac_m.group(1).split('\n') if line.strip()])
                day_text = day_text[ac_m.end():].strip()
            
            # Split day text into sections based on theater headers or double newlines
            lines = day_text.split('\n')
            current_theater = "GENERAL"
            current_air_force = ""
            current_command = ""
            current_block_lines = []
            
            day_theaters = set()
            day_events_count = 0
            
            def flush_block(lines_buf, theater_hdr, cur_af, cur_cmd):
                nonlocal event_idx, mission_idx, combat_idx, casualty_idx, movement_idx, day_events_count
                raw_block = " ".join([l.strip() for l in lines_buf if l.strip()])
                if len(raw_block) < 25 or FOOTER_RE.match(raw_block):
                    return
                
                event_idx += 1
                day_events_count += 1
                evt_id = f"EVT_{iso_date.replace('-', '')}_{event_idx:05d}"
                
                std_theater = standardize_theater(theater_hdr)
                day_theaters.add(std_theater)
                
                # Check for Air Force in block or header
                af_match = AIR_FORCE_RE.search(theater_hdr) or AIR_FORCE_RE.search(raw_block[:150])
                af_val = af_match.group(0).replace('\n', ' ') if af_match else cur_af
                
                # Command
                cmd_match = COMMAND_RE.search(theater_hdr) or COMMAND_RE.search(raw_block[:150])
                cmd_val = cmd_match.group(0).replace('\n', ' ') if cmd_match else cur_cmd
                
                # Sub-region
                reg_match = SUB_REGION_RE.search(raw_block[:200])
                sub_reg = reg_match.group(1) if reg_match else ""
                
                # Aircraft extracted
                ac_extracted = list(set([m.group(1).upper() for m in AC_MODEL_RE.finditer(raw_block)]))
                
                # Check flags
                claims_dpd = list(CLAIM_DPD_RE.finditer(raw_block))
                claims_single = list(CLAIM_SINGLE_RE.finditer(raw_block))
                has_claims = bool(claims_dpd or claims_single)
                
                cas_matches = list(CASUALTY_RE.finditer(raw_block))
                has_cas = bool(cas_matches)
                
                lost_matches = list(LOST_RE.finditer(raw_block))
                dmg_rep_matches = list(DMG_REP_RE.finditer(raw_block))
                dmg_matches = list(DMG_RE.finditer(raw_block))
                has_losses = bool(lost_matches or dmg_rep_matches or dmg_matches)
                
                # Mission numbers
                msn_nums = MISSION_NUM_RE.findall(raw_block)
                msn_num_str = msn_nums[0] if msn_nums else ""
                
                # Store Event
                events_list.append({
                    'event_id': evt_id,
                    'date': iso_date,
                    'year': parsed_year,
                    'month': mo,
                    'theater_standard': std_theater,
                    'theater_raw': theater_hdr,
                    'air_force': af_val,
                    'command_or_task_force': cmd_val,
                    'sub_region': sub_reg,
                    'mission_number': msn_num_str,
                    'aircraft_models': ", ".join(ac_extracted),
                    'has_claims': int(has_claims),
                    'has_losses': int(has_losses),
                    'has_casualties': int(has_cas),
                    'event_text': raw_block,
                    '_day_seq': len(days_list)
                })
                
                # 1. Extract Aerial Combat Claims & Attrition
                if has_claims or has_losses:
                    combat_idx += 1
                    cid = f"ACM_{iso_date.replace('-', '')}_{combat_idx:05d}"
                    c_dest, c_prob, c_dmg = 0, 0, 0
                    enemy_type = "Axis"
                    
                    if claims_dpd:
                        for cm in claims_dpd:
                            c_dest += int(cm.group(1))
                            c_prob += int(cm.group(2))
                            c_dmg += int(cm.group(3))
                            if cm.group(4) and cm.group(4).strip():
                                enemy_type = cm.group(4).strip()
                    elif claims_single:
                        for cm in claims_single:
                            c_dest += int(cm.group(1))
                            if cm.group(2) and cm.group(2).strip():
                                enemy_type = cm.group(2).strip()
                                
                    f_lost = sum([int(m.group(1)) for m in lost_matches if m.group(1) and m.group(1).isdigit()]) if lost_matches else 0
                    f_dmg_rep = sum([int(m.group(1)) for m in dmg_rep_matches if m.group(1) and m.group(1).isdigit()]) if dmg_rep_matches else 0
                    f_dmg = sum([int(m.group(1)) for m in dmg_matches if m.group(1) and m.group(1).isdigit()]) if dmg_matches else 0
                    
                    combat_list.append({
                        'combat_id': cid,
                        'event_id': evt_id,
                        'date': iso_date,
                        'theater': std_theater,
                        'air_force': af_val,
                        'enemy_aircraft_type': enemy_type,
                        'claims_destroyed': c_dest,
                        'claims_probable': c_prob,
                        'claims_damaged': c_dmg,
                        'friendly_lost': f_lost,
                        'friendly_damaged_beyond_repair': f_dmg_rep,
                        'friendly_damaged': f_dmg,
                        'context_snippet': raw_block[:250]
                    })
                    
                # 2. Extract Casualties
                if has_cas:
                    casualty_idx += 1
                    cas_id = f"CAS_{iso_date.replace('-', '')}_{casualty_idx:05d}"
                    kia, wia, mia = 0, 0, 0
                    for cm in cas_matches:
                        cnt, c_type = int(cm.group(1)), cm.group(2).upper()
                        if c_type == 'KIA':
                            kia += cnt
                        elif c_type == 'WIA':
                            wia += cnt
                        elif c_type == 'MIA':
                            mia += cnt
                    
                    # Named personnel check
                    named_p = ""
                    p_match = re.search(r'(?:Colonel|General|Major|Captain|Lieutenant)\s+[A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+', raw_block)
                    if p_match:
                        named_p = p_match.group(0)
                        
                    casualties_list.append({
                        'casualty_id': cas_id,
                        'event_id': evt_id,
                        'date': iso_date,
                        'theater': std_theater,
                        'air_force': af_val,
                        'kia_count': kia,
                        'wia_count': wia,
                        'mia_count': mia,
                        'named_personnel': named_p,
                        'context_snippet': raw_block[:250]
                    })
                    
                # 3. Extract Unit Movements
                for mm in UNIT_MOVE_RE.finditer(raw_block):
                    movement_idx += 1
                    mid = f"MOV_{iso_date.replace('-', '')}_{movement_idx:05d}"
                    u_name = mm.group(1).strip()
                    m_type = mm.group(2).strip()
                    from_loc = mm.group(3) or mm.group(6) or mm.group(8) or ""
                    to_loc = mm.group(4) or mm.group(5) or mm.group(7) or ""
                    
                    # Unit level
                    u_lvl = "Squadron" if "Squadron" in u_name else ("Group" if "Group" in u_name else ("Wing" if "Wing" in u_name else "HQ"))
                    
                    # Aircraft type in movement
                    ac_in_move = ""
                    ac_m = AC_MODEL_RE.search(raw_block[mm.start():min(len(raw_block), mm.end()+80)])
                    if ac_m:
                        ac_in_move = ac_m.group(0)
                        
                    movements_list.append({
                        'movement_id': mid,
                        'event_id': evt_id,
                        'date': iso_date,
                        'theater': std_theater,
                        'air_force': af_val,
                        'unit_name': u_name,
                        'unit_level': u_lvl,
                        'movement_type': m_type,
                        'from_location': from_loc.strip(),
                        'to_location': to_loc.strip(),
                        'aircraft_type': ac_in_move,
                        'context_snippet': raw_block[max(0, mm.start()-20):min(len(raw_block), mm.end()+80)]
                    })
                    
                # 4. Extract Missions
                # Sorties "X of Y AC bomb Z"
                for sm in SORTIE_OF_RE.finditer(raw_block):
                    mission_idx += 1
                    ms_id = f"MSN_{iso_date.replace('-', '')}_{mission_idx:05d}"
                    att_cnt = int(sm.group(1))
                    disp_cnt = int(sm.group(2))
                    ac_t = sm.group(3)
                    tgt_desc = sm.group(4).strip()
                    
                    missions_list.append({
                        'mission_id': ms_id,
                        'event_id': evt_id,
                        'date': iso_date,
                        'theater': std_theater,
                        'air_force': af_val,
                        'official_mission_number': msn_num_str,
                        'aircraft_model': ac_t,
                        'aircraft_dispatched': disp_cnt,
                        'aircraft_attacking': att_cnt,
                        'aircraft_aborted': max(0, disp_cnt - att_cnt),
                        'target_description': tgt_desc[:120],
                        'sub_region': sub_reg
                    })
                    
                # Direct sorties "X AC bomb Z" if not already captured
                if not SORTIE_OF_RE.search(raw_block):
                    for sm in SORTIE_DIRECT_RE.finditer(raw_block):
                        # Filter out dates or irrelevant numbers
                        cnt_val = int(sm.group(1))
                        if cnt_val > 1000 or cnt_val == 0:
                            continue
                        mission_idx += 1
                        ms_id = f"MSN_{iso_date.replace('-', '')}_{mission_idx:05d}"
                        missions_list.append({
                            'mission_id': ms_id,
                            'event_id': evt_id,
                            'date': iso_date,
                            'theater': std_theater,
                            'air_force': af_val,
                            'official_mission_number': msn_num_str,
                            'aircraft_model': sm.group(2),
                            'aircraft_dispatched': cnt_val,
                            'aircraft_attacking': cnt_val,
                            'aircraft_aborted': 0,
                            'target_description': sm.group(3).strip()[:120],
                            'sub_region': sub_reg
                        })

            for line in lines:
                sline = line.strip()
                if THEATER_HEADER_RE.match(sline):
                    if current_block_lines:
                        flush_block(current_block_lines, current_theater, current_air_force, current_command)
                        current_block_lines = []
                    current_theater = sline
                    af_m = AIR_FORCE_RE.search(sline)
                    if af_m:
                        current_air_force = af_m.group(0).replace('\n', ' ')
                    cmd_m = COMMAND_RE.search(sline)
                    if cmd_m:
                        current_command = cmd_m.group(0).replace('\n', ' ')
                else:
                    if sline:
                        current_block_lines.append(sline)
                    elif len(current_block_lines) >= 3:
                        flush_block(current_block_lines, current_theater, current_air_force, current_command)
                        current_block_lines = []
                        
            if current_block_lines:
                flush_block(current_block_lines, current_theater, current_air_force, current_command)
                
            days_list.append({
                'date': iso_date,
                'day_of_week': day_name.capitalize(),
                'year': parsed_year,
                'month': mo,
                'day': int(day_num),
                'aircraft_mentioned': ac_mentioned,
                'events_count': day_events_count,
                'theaters_active': ", ".join(sorted(day_theaters))
            })

    print(f"Parsing complete!")
    print(f"  Total Days: {len(days_list):,}")
    print(f"  Total Events: {len(events_list):,}")
    print(f"  Total Extracted Missions: {len(missions_list):,}")
    print(f"  Total Aerial Combat Reports: {len(combat_list):,}")
    print(f"  Total Casualty Reports: {len(casualties_list):,}")
    print(f"  Total Unit Movements: {len(movements_list):,}")
    
    return (
        pd.DataFrame(days_list),
        pd.DataFrame(events_list),
        pd.DataFrame(missions_list),
        pd.DataFrame(combat_list),
        pd.DataFrame(casualties_list),
        pd.DataFrame(movements_list)
    )

def apply_corrections(df_days, df_events, df_missions, df_combat, df_casualties, df_movements):
    """Clean the parsed tables. df_events must carry `_day_seq` (row position of its day in df_days).

    1. Drop page-footer blocks (source list, signature box) that were parsed as events.
    2. Drop repeated day blocks: when a date appears more than once, keep the last copy
       (the source repeats 28 Feb 1945, the second copy with typos fixed).
    3. Set day_of_week from the calendar date (the source has a few weekday typos)
       and recompute events_count / theaters_active.
    """
    df_days = df_days.reset_index(drop=True).copy()
    df_events = df_events.copy()

    drop_events = set(df_events.loc[df_events['event_text'].str.match(FOOTER_RE), 'event_id'])

    last_seq = df_days.reset_index().groupby('date')['index'].max()
    dup_seqs = set(df_days.index[df_days.index != df_days['date'].map(last_seq)])
    drop_events |= set(df_events.loc[df_events['_day_seq'].isin(dup_seqs), 'event_id'])
    df_days = df_days.drop(index=list(dup_seqs))

    df_events = df_events[~df_events['event_id'].isin(drop_events)]
    children = [t[~t['event_id'].isin(drop_events)] if len(t) else t
                for t in (df_missions, df_combat, df_casualties, df_movements)]

    df_days['day_of_week'] = df_days['date'].map(weekday_of)
    per_day = df_events.groupby('_day_seq')
    df_days['events_count'] = per_day.size().reindex(df_days.index, fill_value=0).astype(int).values
    df_days['theaters_active'] = (per_day['theater_standard']
                                  .agg(lambda s: ", ".join(sorted(set(s))))
                                  .reindex(df_days.index, fill_value="").values)

    print(f"Corrections: dropped {len(drop_events):,} footer/duplicate events and "
          f"{len(dup_seqs)} repeated day block(s).")
    return (df_days.reset_index(drop=True), df_events.drop(columns=['_day_seq']).reset_index(drop=True), *children)

def build_database(df_days, df_events, df_missions, df_combat, df_casualties, df_movements):
    db_path = os.path.join(PROCESSED_DIR, "usaaf_combat_chronology.sqlite")
    print(f"\nBuilding SQLite database: {db_path}...")
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Store DataFrames
    df_days.to_sql("chronology_days", conn, if_exists="replace", index=False)
    df_events.to_sql("chronology_events", conn, if_exists="replace", index=False)
    df_missions.to_sql("chronology_missions", conn, if_exists="replace", index=False)
    df_combat.to_sql("chronology_aerial_combat", conn, if_exists="replace", index=False)
    df_casualties.to_sql("chronology_casualties", conn, if_exists="replace", index=False)
    df_movements.to_sql("chronology_unit_movements", conn, if_exists="replace", index=False)
    
    # Create indexes for high-speed queries
    print("Creating relational indexes...")
    cur.execute("CREATE INDEX idx_days_date ON chronology_days(date);")
    cur.execute("CREATE INDEX idx_days_year_month ON chronology_days(year, month);")
    
    cur.execute("CREATE INDEX idx_events_date ON chronology_events(date);")
    cur.execute("CREATE INDEX idx_events_theater ON chronology_events(theater_standard);")
    cur.execute("CREATE INDEX idx_events_af ON chronology_events(air_force);")
    cur.execute("CREATE INDEX idx_events_subreg ON chronology_events(sub_region);")
    cur.execute("CREATE INDEX idx_events_msn ON chronology_events(mission_number);")
    
    cur.execute("CREATE INDEX idx_missions_date ON chronology_missions(date);")
    cur.execute("CREATE INDEX idx_missions_theater ON chronology_missions(theater);")
    cur.execute("CREATE INDEX idx_missions_ac ON chronology_missions(aircraft_model);")
    
    cur.execute("CREATE INDEX idx_combat_date ON chronology_aerial_combat(date);")
    cur.execute("CREATE INDEX idx_combat_theater ON chronology_aerial_combat(theater);")
    
    cur.execute("CREATE INDEX idx_casualties_date ON chronology_casualties(date);")
    cur.execute("CREATE INDEX idx_movements_date ON chronology_unit_movements(date);")
    cur.execute("CREATE INDEX idx_movements_unit ON chronology_unit_movements(unit_name);")
    
    # Create crosswalk table linking to THOR database if present
    thor_db_path = os.path.join(PROCESSED_DIR, "thor_wwii.sqlite")
    if not os.path.exists(thor_db_path) and os.path.exists(thor_db_path + ".gz"):
        print("Decompressing thor_wwii.sqlite.gz for cross-referencing...")
        with gzip.open(thor_db_path + ".gz", "rb") as f_in:
            with open(thor_db_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

    if os.path.exists(thor_db_path):
        print("Integrating THOR WWII daily summary for cross-referencing...")
        cur.execute(f"ATTACH DATABASE '{thor_db_path}' AS thor;")
        cur.execute("""
            CREATE TABLE thor_daily_summary AS
            SELECT 
                mission_date_iso as date,
                COUNT(WWII_ID) as thor_missions_count,
                ROUND(SUM(total_tons_clean), 1) as thor_total_tons,
                GROUP_CONCAT(DISTINCT THEATER) as thor_theaters
            FROM thor.missions
            WHERE mission_date_iso IS NOT NULL
            GROUP BY mission_date_iso;
        """)
        cur.execute("CREATE INDEX idx_thor_daily_date ON thor_daily_summary(date);")
        cur.execute("DETACH DATABASE thor;")
        
        cur.execute("""
            CREATE VIEW v_daily_operational_crosswalk AS
            SELECT 
                d.date,
                d.day_of_week,
                d.theaters_active,
                d.events_count as usaaf_events_count,
                COALESCE(t.thor_missions_count, 0) as thor_bombing_missions,
                COALESCE(t.thor_total_tons, 0.0) as thor_tons_dropped,
                t.thor_theaters
            FROM chronology_days d
            LEFT JOIN thor_daily_summary t ON d.date = t.date
            ORDER BY d.date;
        """)
        conn.commit()
    
    conn.commit()
    conn.close()
    
    # Compress SQLite archive
    print("Compressing SQLite database to .sqlite.gz...")
    with open(db_path, 'rb') as f_in:
        with gzip.open(db_path + '.gz', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
            
    # Export Parquet & CSVs
    print("Exporting Parquet and compressed CSVs...")
    try:
        df_events.to_parquet(os.path.join(PROCESSED_DIR, "usaaf_chronology_events.parquet"), compression="snappy", index=False)
        print("Exported usaaf_chronology_events.parquet successfully.")
    except Exception as e:
        print(f"Parquet export skipped: {e}")
    df_days.to_csv(os.path.join(PROCESSED_DIR, "usaaf_chronology_days.csv.gz"), compression="gzip", index=False)
    df_events.to_csv(os.path.join(PROCESSED_DIR, "usaaf_chronology_events.csv.gz"), compression="gzip", index=False)
    df_missions.to_csv(os.path.join(PROCESSED_DIR, "usaaf_chronology_missions.csv.gz"), compression="gzip", index=False)
    df_combat.to_csv(os.path.join(PROCESSED_DIR, "usaaf_chronology_combat.csv.gz"), compression="gzip", index=False)
    df_casualties.to_csv(os.path.join(PROCESSED_DIR, "usaaf_chronology_casualties.csv.gz"), compression="gzip", index=False)
    df_movements.to_csv(os.path.join(PROCESSED_DIR, "usaaf_chronology_movements.csv.gz"), compression="gzip", index=False)

def export_explorer_js(conn_path=None):
    """Write docs/chronology_data.js for docs/chronology_explorer.html."""
    conn = sqlite3.connect(conn_path or os.path.join(PROCESSED_DIR, "usaaf_combat_chronology.sqlite"))
    e = pd.read_sql("SELECT event_id, date, theater_standard, air_force, sub_region, has_claims, has_losses, "
                    "has_casualties, mission_number, aircraft_models, event_text FROM chronology_events", conn)
    cb = pd.read_sql("SELECT event_id, claims_destroyed, claims_probable, claims_damaged, friendly_lost "
                     "FROM chronology_aerial_combat", conn)
    ca = pd.read_sql("SELECT event_id, kia_count, wia_count, mia_count FROM chronology_casualties", conn)
    mv = pd.read_sql("SELECT event_id, unit_name, from_location, to_location FROM chronology_unit_movements", conn)
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    out = (e.merge(cb, on='event_id', how='left')
            .merge(ca, on='event_id', how='left')
            .merge(mv, on='event_id', how='left'))
    if 'thor_daily_summary' in tables:
        t = pd.read_sql("SELECT date, thor_missions_count, thor_total_tons FROM thor_daily_summary", conn)
        out = out.merge(t, on='date', how='left')
    conn.close()
    out = out.sort_values('date', kind='stable')
    count_cols = ['claims_destroyed', 'claims_probable', 'claims_damaged', 'friendly_lost',
                  'kia_count', 'wia_count', 'mia_count', 'thor_missions_count']
    for col in count_cols:
        if col in out:
            out[col] = out[col].astype('Int64')
    out = out.astype(object).where(out.notna(), None)
    records = out.to_dict(orient='records')
    js_path = os.path.join(DOCS_DIR, "chronology_data.js")
    with open(js_path, "w", encoding="utf-8") as f:
        f.write("window.CHRONOLOGY_DATA = " + json.dumps(records, ensure_ascii=False) + ";\n")
    print(f"Saved: {js_path} ({len(records):,} rows)")

def export_tunisia_subset(df_events, df_missions, df_movements):
    print("\nFiltering and exporting Tunisia Campaign (1942–1943) subset...")
    tunisia_events = df_events[
        (df_events['sub_region'].str.upper() == 'TUNISIA') |
        (df_events['event_text'].str.contains(r'\b(?:Tunis|Bizerte|Sousse|Sfax|Kairouan|Gabes|Gabès|Mareth|Kasserine|Enfidha|Medjez|Tebourba|Cap Bon)\b', case=False, regex=True))
    ].copy()
    
    print(f"Identified {len(tunisia_events):,} operational narrative events in Tunisia.")
    
    # Export to wwii-thor-dataset
    out_tn_csv = os.path.join(GIS_DIR, "tunisia_wwii_combat_chronology.csv")
    tunisia_events.to_csv(out_tn_csv, index=False)
    print(f"Saved: {out_tn_csv}")
    
    # Copy to MapsTN if repository exists
    if os.path.exists(MAPSTN_DIR):
        mapstn_tn_csv = os.path.join(MAPSTN_DIR, "data", "wwii_bombing", "tunisia_wwii_combat_chronology.csv")
        tunisia_events.to_csv(mapstn_tn_csv, index=False)
        print(f"Synced to MapsTN: {mapstn_tn_csv}")

if __name__ == "__main__":
    t0 = datetime.now()
    if len(sys.argv) > 1:
        RAW_HTML_DIR = sys.argv[1]
    df_days, df_events, df_missions, df_combat, df_casualties, df_movements = apply_corrections(*parse_corpus())
    build_database(df_days, df_events, df_missions, df_combat, df_casualties, df_movements)
    export_tunisia_subset(df_events, df_missions, df_movements)
    export_explorer_js()
    print(f"\nAll pipelines completed successfully in {(datetime.now() - t0).total_seconds():.1f}s.")

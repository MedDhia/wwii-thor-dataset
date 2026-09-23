# USAAF Worldwide Combat Chronology (1941–1945) — Data Dictionary & Schema

This document details the relational schemas, data types, and field definitions of the **USAAF Combat Chronology** dataset.

**Source.** The text is Jack McKillop's day-by-day *USAAF Combat Operations in WWII*, which is based on Kit C. Carter and Robert Mueller, *The Army Air Forces in World War II: Combat Chronology, 1941–1945* (Office of Air Force History), as published at [aircrewremembered.com/USAAFCombatOperations](https://aircrewremembered.com/USAAFCombatOperations/). It was parsed from a local mirror of those pages by `scripts/build_chronology_dataset.py`; the mirror is not included in this repository.

**How the fields are produced.** Every structured field below (theater, air force, claims, losses, casualties, sorties, unit moves) is extracted with regular expressions from the narrative text. The extraction is approximate: treat the tables as an index into `event_text`, not as a verified count.

**Corrections applied** (`scripts/apply_chronology_corrections.py`):
- Two January 1943 day entries whose header was misprinted as 1942 (2 Jan, 12 Jan) are re-dated to 1943, confirmed by the printed weekday.
- The source repeats 28 Feb 1945; the first (uncorrected) copy is dropped.
- 147 page-footer blocks (source list, compiler's signature box) that were parsed as events are dropped.
- `day_of_week` is taken from the calendar date; six headers print the wrong weekday.

---

## 🗄️ Relational Database Overview

- **Database File**: [`data/processed/usaaf_combat_chronology.sqlite`](data/processed/usaaf_combat_chronology.sqlite) (Compressed: `usaaf_combat_chronology.sqlite.gz`)
- **Parquet Table**: [`data/processed/usaaf_chronology_events.parquet`](data/processed/usaaf_chronology_events.parquet)
- **Primary Tables**:
  1. `chronology_days`: One row per dated entry (1,328 days). The first row, 6 Dec 1941, is the pre-war order of battle; 39 calendar days between 7 Dec 1941 and 2 Sep 1945 have no entry.
  2. `chronology_events`: Narrative blocks tagged with theater and air force (8,585 records).
  3. `chronology_missions`: Sortie phrases such as "X of Y B-17s bomb Z" (2,562 records).
  4. `chronology_aerial_combat`: Events mentioning claims or friendly losses (798 records). Only 537 contain an enemy-aircraft claim and 349 a probable or damaged figure; the rest record friendly losses only.
  5. `chronology_casualties`: Events with KIA / WIA / MIA counts (435 records).
  6. `chronology_unit_movements`: Unit move / transfer / arrival phrases (1,367 records).
  7. `thor_daily_summary`: Daily aggregate table of THOR quantitative bombing missions and total tonnage.
- **Analytical View**:
  - `v_daily_operational_crosswalk`: Relational bridge connecting chronological narratives to quantitative THOR bombing operations.

---

## 📋 Table Definitions

### 1. `chronology_days`
| Column | Type | Description |
|---|---|---|
| `date` | `TEXT` | ISO 8601 calendar date (`YYYY-MM-DD`); unique per row (no database constraint). |
| `day_of_week` | `TEXT` | Day of week of `date` (`Sunday`, `Monday`, etc.). |
| `year` | `INTEGER` | Calendar year (1941–1945). |
| `month` | `INTEGER` | Calendar month (1–12). |
| `day` | `INTEGER` | Day of month (1–31). |
| `aircraft_mentioned` | `TEXT` | Semicolon-separated "aircraft mentioned in this report" list, when the day has one. |
| `events_count` | `INTEGER` | Total operational event blocks recorded for this day. |
| `theaters_active` | `TEXT` | Comma-separated active theaters (e.g. `ETO, MTO, SWPA`). |

### 2. `chronology_events`
| Column | Type | Description |
|---|---|---|
| `event_id` | `TEXT` (PK) | Unique event identifier (e.g. `EVT_19421117_00052`). |
| `date` | `TEXT` (FK) | Reference date (`YYYY-MM-DD`). |
| `year` | `INTEGER` | Year. |
| `month` | `INTEGER` | Month. |
| `theater_standard` | `TEXT` | Theater code from the nearest recognised header: `ETO`, `MTO`, `SWPA`, `POA`, `SOPAC`, `CBI`, `USASTAF`, `ATO`, or `OTHER` when no header matched (2,663 events, 31%). Most Eighth, Ninth and Fifteenth Air Force events fall under `OTHER`, so filter on `air_force` for theater work. |
| `theater_raw` | `TEXT` | Verbatim theater header string from historical report. |
| `air_force` | `TEXT` | Operating numbered air force (e.g. `Eighth Air Force`, `Twelfth Air Force`). |
| `command_or_task_force`| `TEXT` | Sub-command (e.g. `VIII Bomber Command`, `India Air Task Force`). |
| `sub_region` | `TEXT` | Country or tactical region (e.g. `Tunisia`, `France`, `Burma`, `Germany`). |
| `mission_number` | `TEXT` | Official USAAF mission number if stated (e.g. `20`, `84`). |
| `aircraft_models` | `TEXT` | Comma-separated list of aircraft models identified in narrative. |
| `has_claims` | `INTEGER` | 1 if the text matches a claim pattern ("claim 12-3-5", "claims 4 … shot down"). |
| `has_losses` | `INTEGER` | Boolean flag (1 if friendly aircraft losses/damage recorded). |
| `has_casualties` | `INTEGER` | Boolean flag (1 if KIA/WIA/MIA recorded). |
| `event_text` | `TEXT` | Narrative text of the block, verbatim from the source (including its typos). |

### 3. `chronology_missions`
| Column | Type | Description |
|---|---|---|
| `mission_id` | `TEXT` (PK) | Unique mission identifier (e.g. `MSN_19421117_00012`). |
| `event_id` | `TEXT` (FK) | Link to parent `chronology_events` record. |
| `date` | `TEXT` | Mission date (`YYYY-MM-DD`). |
| `theater` | `TEXT` | Standardized theater code. |
| `air_force` | `TEXT` | Operating air force. |
| `official_mission_number`| `TEXT` | Numbered mission ID. |
| `aircraft_model` | `TEXT` | Aircraft model (e.g. `B-17`, `B-24`, `B-25`, `P-38`). |
| `aircraft_dispatched` | `INTEGER` | Number of aircraft that took off. |
| `aircraft_attacking` | `INTEGER` | Number of aircraft that dropped ordnance on target. |
| `aircraft_aborted` | `INTEGER` | Number of aircraft forced to abort. |
| `target_description` | `TEXT` | Tactical target objective or facility. |
| `sub_region` | `TEXT` | Geographic sub-region. |

### 4. `chronology_aerial_combat`
| Column | Type | Description |
|---|---|---|
| `combat_id` | `TEXT` (PK) | Unique aerial combat record identifier. |
| `event_id` | `TEXT` (FK) | Link to parent `chronology_events` record. |
| `date` | `TEXT` | Engagement date (`YYYY-MM-DD`). |
| `theater` | `TEXT` | Standardized theater code. |
| `air_force` | `TEXT` | Operating air force. |
| `enemy_aircraft_type` | `TEXT` | Words following the claim (`Luftwaffe`, `Japanese`, `fighters`, …); `Axis` is a default filled in when none was found (329 rows). |
| `claims_destroyed` | `INTEGER` | Enemy aircraft claimed destroyed (first number in D-P-D). Claims, not confirmed kills. |
| `claims_probable` | `INTEGER` | Probable enemy aircraft destroyed (the second digit in D-P-D). |
| `claims_damaged` | `INTEGER` | Enemy aircraft damaged in combat (the third digit in D-P-D). |
| `friendly_lost` | `INTEGER` | Allied aircraft lost in engagement or to flak. |
| `friendly_damaged_beyond_repair` | `INTEGER` | Aircraft scrapped or written off upon recovery. |
| `friendly_damaged` | `INTEGER` | Battle-damaged aircraft repairable. |
| `context_snippet` | `TEXT` | Excerpt from historical narrative detailing combat. |

### 5. `chronology_casualties`
| Column | Type | Description |
|---|---|---|
| `casualty_id` | `TEXT` (PK) | Unique casualty record identifier. |
| `event_id` | `TEXT` (FK) | Link to parent `chronology_events` record. |
| `date` | `TEXT` | Incident date (`YYYY-MM-DD`). |
| `theater` | `TEXT` | Standardized theater code. |
| `air_force` | `TEXT` | Operating air force. |
| `kia_count` | `INTEGER` | Aircrew Killed in Action. |
| `wia_count` | `INTEGER` | Aircrew Wounded in Action. |
| `mia_count` | `INTEGER` | Aircrew Missing in Action (baled out over enemy territory, POW, lost at sea). |
| `named_personnel` | `TEXT` | Named commanders, pilots, or crewmen mentioned. |
| `context_snippet` | `TEXT` | Excerpt from historical narrative detailing casualties. |

### 6. `chronology_unit_movements`
| Column | Type | Description |
|---|---|---|
| `movement_id` | `TEXT` (PK) | Unique movement identifier. |
| `event_id` | `TEXT` (FK) | Link to parent `chronology_events` record. |
| `date` | `TEXT` | Relocation date (`YYYY-MM-DD`). |
| `theater` | `TEXT` | Standardized theater code. |
| `air_force` | `TEXT` | Operating air force. |
| `unit_name` | `TEXT` | Military unit (e.g. `80th Bombardment Squadron (Medium)`). |
| `unit_level` | `TEXT` | Echelon: `HQ`, `Wing`, `Group`, `Squadron`. |
| `movement_type` | `TEXT` | Action: `moves`, `transfers`, `arrives`, `begins operating`. |
| `from_location` | `TEXT` | Departure airfield or base. |
| `to_location` | `TEXT` | Arrival airfield or base. |
| `aircraft_type` | `TEXT` | Aircraft airframe operated by unit during movement. |
| `context_snippet` | `TEXT` | Excerpt from historical narrative. |

---

## 🔗 Cross-Referencing View (`v_daily_operational_crosswalk`)

This SQL view bridges narrative history with the quantitative THOR bombing database:

```sql
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
```

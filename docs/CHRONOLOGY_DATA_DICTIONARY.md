# USAAF Worldwide Combat Chronology (1941–1945) — Data Dictionary & Schema

This document details the relational schemas, data types, and field definitions of the **USAAF Worldwide Combat Chronology** dataset, constructed from the official United States Air Force historical daily combat logs compiled by Kit C. Carter and Robert Mueller (Office of Air Force History / AFHRA).

---

## 🗄️ Relational Database Overview

- **Database File**: [`data/processed/usaaf_combat_chronology.sqlite`](data/processed/usaaf_combat_chronology.sqlite) (Compressed: `usaaf_combat_chronology.sqlite.gz`)
- **Parquet Table**: [`data/processed/usaaf_chronology_events.parquet`](data/processed/usaaf_chronology_events.parquet)
- **Primary Tables**:
  1. `chronology_days`: Daily calendar level (1,329 days, Dec 1941 – Sep 1945).
  2. `chronology_events`: Operational event narratives partitioned by theater and air force (8,742 records).
  3. `chronology_missions`: Granular mission strikes with dispatched/attacking aircraft counts and targets (2,565 records).
  4. `chronology_aerial_combat`: Air-to-air dogfight scorecards with Destroyed-Probable-Damaged (D-P-D) claims and friendly losses (799 records).
  5. `chronology_casualties`: Daily personnel casualties categorized into KIA, WIA, and MIA (436 records).
  6. `chronology_unit_movements`: Order of Battle airfield relocations (1,368 records).
  7. `thor_daily_summary`: Daily aggregate table of THOR quantitative bombing missions and total tonnage.
- **Analytical View**:
  - `v_daily_operational_crosswalk`: Relational bridge connecting chronological narratives to quantitative THOR bombing operations.

---

## 📋 Table Definitions

### 1. `chronology_days`
| Column | Type | Description |
|---|---|---|
| `date` | `TEXT` (PK) | ISO 8601 calendar date (`YYYY-MM-DD`). |
| `day_of_week` | `TEXT` | Day of week (`Sunday`, `Monday`, etc.). |
| `year` | `INTEGER` | Calendar year (1941–1945). |
| `month` | `INTEGER` | Calendar month (1–12). |
| `day` | `INTEGER` | Day of month (1–31). |
| `aircraft_mentioned` | `TEXT` | Semicolon-separated list of aircraft models active in official daily report. |
| `events_count` | `INTEGER` | Total operational event blocks recorded for this day. |
| `theaters_active` | `TEXT` | Comma-separated active theaters (e.g. `ETO, MTO, SWPA`). |

### 2. `chronology_events`
| Column | Type | Description |
|---|---|---|
| `event_id` | `TEXT` (PK) | Unique event identifier (e.g. `EVT_19421117_00052`). |
| `date` | `TEXT` (FK) | Reference date (`YYYY-MM-DD`). |
| `year` | `INTEGER` | Year. |
| `month` | `INTEGER` | Month. |
| `theater_standard` | `TEXT` | Standardized theater code: `ETO`, `MTO`, `SWPA`, `POA`, `SOPAC`, `CBI`, `USASTAF`, `ATO`. |
| `theater_raw` | `TEXT` | Verbatim theater header string from historical report. |
| `air_force` | `TEXT` | Operating numbered air force (e.g. `Eighth Air Force`, `Twelfth Air Force`). |
| `command_or_task_force`| `TEXT` | Sub-command (e.g. `VIII Bomber Command`, `India Air Task Force`). |
| `sub_region` | `TEXT` | Country or tactical region (e.g. `Tunisia`, `France`, `Burma`, `Germany`). |
| `mission_number` | `TEXT` | Official USAAF mission number if stated (e.g. `20`, `84`). |
| `aircraft_models` | `TEXT` | Comma-separated list of aircraft models identified in narrative. |
| `has_claims` | `INTEGER` | Boolean flag (1 if dogfight claims are recorded). |
| `has_losses` | `INTEGER` | Boolean flag (1 if friendly aircraft losses/damage recorded). |
| `has_casualties` | `INTEGER` | Boolean flag (1 if KIA/WIA/MIA recorded). |
| `event_text` | `TEXT` | Full verbatim historical combat log narrative. |

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
| `enemy_aircraft_type` | `TEXT` | Enemy aircraft model or force (`Luftwaffe`, `Japanese`, `Zeke`, etc.). |
| `claims_destroyed` | `INTEGER` | Confirmed enemy aircraft destroyed (the first digit in D-P-D). |
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

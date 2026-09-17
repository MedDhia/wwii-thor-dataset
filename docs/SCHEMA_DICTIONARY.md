# WWII THOR Dataset Schema & Field Dictionary

The enriched WWII THOR dataset contains **78 columns**: 62 original DoD/AFRI operational attributes plus 16 computed and enriched attributes for temporal, geospatial, ordnance, and aircraft analysis.

---

## 🌟 Enriched & Standardized Attributes (16 Columns)

| Field Name | Type | Description |
|---|---|---|
| `mission_date_iso` | String (`YYYY-MM-DD`) | Standardized ISO-8601 mission date. |
| `year` | Integer | Mission year (`1939` - `1945`). |
| `month` | Integer | Mission month (`1` - `12`). |
| `year_month` | String (`YYYY-MM`) | Year and month for grouping time series. |
| `target_lat` | Float | Cleaned target latitude in decimal degrees `[-90, 90]`. |
| `target_lon` | Float | Cleaned target longitude in decimal degrees `[-180, 180]`. |
| `has_valid_target_coords` | Boolean | True if target coordinates are present, within bounds, and non-zero. |
| `takeoff_lat` | Float | Cleaned takeoff base latitude in decimal degrees. |
| `takeoff_lon` | Float | Cleaned takeoff base longitude in decimal degrees. |
| `has_valid_takeoff_coords` | Boolean | True if takeoff coordinates are present, within bounds, and non-zero. |
| `has_flight_path` | Boolean | True if both takeoff and target coordinates are valid. |
| `aircraft_full_name` | String | Standardized aircraft name joined from AFRI aircraft glossary (e.g. `B-17 Flying Fortress`, `Avro Lancaster`). |
| `aircraft_category` | String | Functional aircraft role (e.g. `Heavy Bomber`, `Medium Bomber`, `Fighter / Fighter-Bomber`). |
| `aircraft_glossary_link` | String | Reference URL to military factory / historical archive for the aircraft model. |
| `country_flying_mission_clean`| String | Standardized nationality of the attacking air force (`USA`, `GREAT BRITAIN`, `NEW ZEALAND`, `AUSTRALIA`, `SOUTH AFRICA`). |
| `total_tons_clean` | Float | Reconciled bomb tonnage (greater of recorded `TOTAL_TONS` or sum of HE + IC + Frag). |

---

## 📋 Core Original Mission Attributes (62 Columns)

### Identification & Command
1. `WWII_ID`: Unique integer identifier for each bombing mission record.
2. `MASTER_INDEX_NUMBER`: Original master AFRI archive index.
3. `MSNDATE`: Raw recorded mission date (`M/D/YYYY`).
4. `THEATER`: Theater of operations code (`ETO`, `PTO`, `MTO`, `CBI`, `EAST AFRICA`, `MADAGASCAR`).
5. `NAF`: Numbered Air Force (e.g., `8 AF`, `9 AF`, `12 AF`, `15 AF`, `5 AF`, `13 AF`, `20 AF`, `RAF BOMBER COMMAND`).
6. `COUNTRY_FLYING_MISSION`: Nation operating the aircraft (`USA`, `GREAT BRITAIN`, etc.).
7. `UNIT_ID`: Squadron or Bomb Group (e.g., `305 BG`, `306 BG`, `27 FBG`, `89 S`).
8. `CALLSIGN`: Tactical radio callsign.

### Aircraft & Formations
9. `MDS`: Mission Design Series aircraft code (e.g., `B17`, `B24`, `LAN`, `A20`).
10. `AIRCRAFT_NAME`: Raw aircraft model or series text.
11. `MSN_TYPE`: Tactical mission type code.
12. `AC_AIRBORNE`: Number of aircraft taking off.
13. `AC_ATTACKING`: Number of aircraft releasing bombs over target.
14. `AC_DROPPING`: Number of aircraft dropping ordnance.
15. `AC_LOST`: Aircraft lost to enemy action or accidents.
16. `AC_DAMAGED`: Aircraft sustaining combat damage.
17. `SPARES_RETURN_AC`: Spare aircraft returning before target.
18. `WX_FAIL_AC`: Aircraft aborting due to adverse weather.
19. `MECH_FAIL_AC`: Aircraft aborting due to mechanical issues.
20. `MISC_FAIL_AC`: Aircraft aborting due to miscellaneous reasons.

### Target & Mission Objectives
21. `TGT_COUNTRY_CODE`: Numerical country code of target.
22. `TGT_COUNTRY`: Sovereign nation or territory targeted (e.g., `GERMANY`, `FRANCE`, `JAPAN`, `ITALY`).
23. `TGT_LOCATION`: Target city, town, harbor, or geographic feature.
24. `TGT_TYPE`: Target facility type (e.g., `AIRDROME`, `MARSHALLING YARD`, `OIL REFINERY`, `FACTORY`, `BRIDGES`).
25. `TGT_ID`: Unique target facility ID in military targeting manuals.
26. `TGT_INDUSTRY_CODE`: Industry classification code.
27. `TGT_INDUSTRY`: Specific industrial sector targeted.
28. `TGT_PRIORITY`: Target priority ranking (`1` = primary, `2` = secondary, `3` = opportunity).
29. `TGT_PRIORITY_EXPLANATION`: Description of target priority.

### Geolocation & Airfields
30. `SOURCE_LATITUDE`: Raw source coordinates latitude as recorded in paper archives.
31. `SOURCE_LONGITUDE`: Raw source coordinates longitude as recorded in paper archives.
32. `LATITUDE`: Target latitude (decimal degrees).
33. `LONGITUDE`: Target longitude (decimal degrees).
34. `TAKEOFF_BASE`: Name of takeoff airfield or advanced landing ground.
35. `TAKEOFF_COUNTRY`: Country or region where takeoff airfield was located.
36. `TAKEOFF_LATITUDE`: Takeoff airfield latitude.
37. `TAKEOFF_LONGITUDE`: Takeoff airfield longitude.

### Munitions, Bomb Tonnage & Ballistics
38. `ALTITUDE`: Operating bombing altitude.
39. `ALTITUDE_FEET`: Operating altitude in feet.
40. `NUMBER_OF_HE`: Count of High Explosive bombs dropped.
41. `TYPE_OF_HE`: Nomenclature of HE bombs (e.g., `500 LB GP`, `1000 LB GP`, `4000 LB COOKIE`).
42. `LBS_HE`: Total weight of HE munitions in pounds.
43. `TONS_OF_HE`: Total weight of HE munitions in tons.
44. `NUMBER_OF_IC`: Count of Incendiary clusters or canisters dropped.
45. `TYPE_OF_IC`: Nomenclature of Incendiary bombs (e.g., `M17`, `AN-M50`, `M69 Napalm`).
46. `LBS_IC`: Total weight of Incendiary munitions in pounds.
47. `TONS_OF_IC`: Total weight of Incendiary munitions in tons.
48. `NUMBER_OF_FRAG`: Count of Fragmentation bombs dropped.
49. `TYPE_OF_FRAG`: Nomenclature of Fragmentation bombs (e.g., `20 LB FRAG`, `M83 Butterfly`).
50. `LBS_FRAG`: Total weight of Fragmentation munitions in pounds.
51. `TONS_OF_FRAG`: Total weight of Fragmentation munitions in tons.
52. `TOTAL_LBS`: Total recorded bomb weight in pounds.
53. `TOTAL_TONS`: Total recorded bomb weight in tons.
54. `ROUNDS_AMMO`: Rounds of aircraft machine gun / cannon ammunition expended.

### Execution & Results
55. `TIME_OVER_TARGET`: Time aircraft appeared over target (GMT or local military time).
56. `SIGHTING_METHOD_CODE`: Sighting method code (`1` = Visual, `2` = Radar / H2X / Gee / Oboe).
57. `SIGHTING_EXPLANATION`: Plain English description of sighting procedure.
58. `BDA`: Bomb Damage Assessment notes and aerial photo reconnaissance summary.
59. `TARGET_COMMENT`: Operational targeting remarks.
60. `MISSION_COMMENTS`: Post-mission debriefing notes and enemy resistance comments.
61. `SOURCE`: Original military document or paper file citation.
62. `DATABASE_EDIT_COMMENTS`: Curatorial notes added during DoD digitization.

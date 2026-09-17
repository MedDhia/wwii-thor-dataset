#!/usr/bin/env Rscript
# scripts/generate_theater_global_maps.R
# Minimalist, publication-grade white background maps of WWII aerial bombing operations across global theaters.
# Generates 5 maps: Global Footprint, European Theater (ETO), Mediterranean (MTO), Pacific/CBI (PTO/CBI), and Germany/Austria closeup.

suppressPackageStartupMessages({
  library(sf)
  library(rnaturalearth)
  library(DBI)
  library(RSQLite)
  library(dplyr)
  library(ggplot2)
  library(scales)
  library(ggspatial)
})

base_dir <- "/Users/mohameddhiahammami/.gemini/antigravity/scratch/wwii-thor-dataset"
maps_dir <- file.path(base_dir, "maps")
dir.create(maps_dir, showWarnings = FALSE, recursive = TRUE)
sqlite_path <- file.path(base_dir, "data", "processed", "thor_wwii.sqlite")

cat("Loading Natural Earth landmasses and countries...\n")
world_countries <- ne_countries(scale = "medium", returnclass = "sf")

cat("Connecting to SQLite database...\n")
con <- dbConnect(RSQLite::SQLite(), sqlite_path)

# Common minimalist theme
theme_theater_white <- function(title_size = 14, subtitle_size = 9.5) {
  theme_void() +
    theme(
      plot.background = element_rect(fill = "#ffffff", color = NA),
      panel.background = element_rect(fill = "#ffffff", color = NA),
      plot.title = element_text(color = "#0f172a", size = title_size, face = "bold", margin = margin(t = 14, b = 4, l = 16)),
      plot.subtitle = element_text(color = "#64748b", size = subtitle_size, margin = margin(b = 10, l = 16)),
      plot.caption = element_text(color = "#94a3b8", size = 8, margin = margin(t = 8, b = 12, r = 16), hjust = 1),
      legend.background = element_rect(fill = "#ffffff", color = "#e2e8f0", linewidth = 0.3),
      legend.title = element_text(color = "#0f172a", size = 8.5, face = "bold"),
      legend.text = element_text(color = "#475569", size = 7.5),
      legend.margin = margin(6, 10, 6, 10)
    )
}

# ==============================================================================
# 1. GLOBAL WWII BOMBING FOOTPRINT
# ==============================================================================
cat("\n[1/5] Querying Global WWII Bombing Missions...\n")
global_df <- dbGetQuery(con, "
  SELECT target_lat, target_lon, total_tons_clean, THEATER
  FROM missions
  WHERE has_valid_target_coords = 1
")
cat(sprintf("Loaded %d global missions with valid coordinates.\n", nrow(global_df)))

p_global <- ggplot() +
  geom_sf(data = world_countries, fill = "#ffffff", color = "#cbd5e1", linewidth = 0.15) +
  geom_point(data = global_df, 
             aes(x = target_lon, y = target_lat, size = total_tons_clean),
             shape = 21,
             fill = "#dc2626",
             color = "#991b1b",
             stroke = 0.1,
             alpha = 0.35) +
  scale_size_area(
    name = "Bomb Tonnage",
    max_size = 6.5,
    breaks = c(10, 50, 200, 500),
    labels = c("10 t", "50 t", "200 t", "500 t")
  ) +
  coord_sf(xlim = c(-140, 160), ylim = c(-25, 68), expand = FALSE) +
  labs(
    title = "Global Footprint of Allied Aerial Bombardment in WWII (1939–1945)",
    subtitle = "170,000+ combat missions across European, Mediterranean, African, Asian, and Pacific Theaters",
    caption = "Source: USAF Theater History of Operations (THOR) Database • 2.76M Tons of Ordnance"
  ) +
  theme_theater_white(title_size = 15, subtitle_size = 10) +
  theme(
    legend.position = c(0.12, 0.25)
  ) +
  guides(size = guide_legend(override.aes = list(alpha = 0.7, fill = "#dc2626", color = "#991b1b")))

global_png <- file.path(maps_dir, "wwii_global_bombing_footprint.png")
global_pdf <- file.path(maps_dir, "wwii_global_bombing_footprint.pdf")
ggsave(global_png, p_global, width = 14, height = 7.5, dpi = 300)
ggsave(global_pdf, p_global, width = 14, height = 7.5, device = cairo_pdf)
cat("Saved global bombing footprint map.\n")

# ==============================================================================
# 2. EUROPEAN THEATER OF OPERATIONS (ETO) STRATEGIC BOMBING
# ==============================================================================
cat("\n[2/5] Querying European Theater (ETO) Missions...\n")
eto_df <- dbGetQuery(con, "
  SELECT target_lat, target_lon, total_tons_clean
  FROM missions
  WHERE THEATER = 'ETO' AND has_valid_target_coords = 1
")
cat(sprintf("Loaded %d ETO missions.\n", nrow(eto_df)))

eto_cities <- data.frame(
  name = c("London", "Paris", "Berlin", "Hamburg", "Munich", "Cologne", "Essen", "Dresden", "Frankfurt", "Vienna", "Brussels", "Amsterdam"),
  lon = c(-0.1278, 2.3522, 13.4050, 9.9937, 11.5820, 6.9603, 7.0116, 13.7373, 8.6821, 16.3738, 4.3517, 4.9041),
  lat = c(51.5074, 48.8566, 52.5200, 53.5511, 48.1351, 50.9375, 51.4556, 51.0504, 50.1109, 48.2082, 50.8503, 52.3676)
) %>% st_as_sf(coords = c("lon", "lat"), crs = 4326, remove = FALSE)

p_eto <- ggplot() +
  geom_sf(data = world_countries, fill = "#ffffff", color = "#cbd5e1", linewidth = 0.25) +
  geom_point(data = eto_df, 
             aes(x = target_lon, y = target_lat, size = total_tons_clean),
             shape = 21,
             fill = "#dc2626",
             color = "#7f1d1d",
             stroke = 0.12,
             alpha = 0.35) +
  geom_sf(data = eto_cities, color = "#0f172a", size = 1.8, shape = 19) +
  geom_sf_text(data = eto_cities, aes(label = name), 
               color = "#0f172a", size = 3.0, fontface = "bold", 
               nudge_x = 0.35, nudge_y = 0.15, check_overlap = TRUE) +
  scale_size_area(
    name = "Bomb Weight",
    max_size = 9.0,
    breaks = c(10, 50, 100, 250, 500),
    labels = c("10 t", "50 t", "100 t", "250 t", "500 t")
  ) +
  coord_sf(xlim = c(-6.5, 20.0), ylim = c(43.5, 55.8), expand = FALSE) +
  annotation_scale(location = "bl", width_hint = 0.2, style = "ticks",
                   text_col = "#64748b", line_col = "#64748b") +
  labs(
    title = "The Strategic Bombing Campaign in Europe (ETO, 1942–1945)",
    subtitle = "Combined Bomber Offensive (USAAF 8th/9th Air Forces & RAF) • Over 3.15 Million Tons Dropped",
    caption = "Source: USAF WWII THOR Database • Germany (1.99M t), France (783k t), Austria (149k t)"
  ) +
  theme_theater_white(title_size = 14, subtitle_size = 9.5) +
  theme(
    legend.position = c(0.10, 0.25)
  ) +
  guides(size = guide_legend(override.aes = list(alpha = 0.75, fill = "#dc2626", color = "#7f1d1d")))

eto_png <- file.path(maps_dir, "wwii_eto_strategic_bombing.png")
eto_pdf <- file.path(maps_dir, "wwii_eto_strategic_bombing.pdf")
ggsave(eto_png, p_eto, width = 11, height = 8.5, dpi = 300)
ggsave(eto_pdf, p_eto, width = 11, height = 8.5, device = cairo_pdf)
cat("Saved ETO strategic bombing map.\n")

# ==============================================================================
# 3. MEDITERRANEAN THEATER OF OPERATIONS (MTO)
# ==============================================================================
cat("\n[3/5] Querying Mediterranean Theater (MTO) Missions...\n")
mto_df <- dbGetQuery(con, "
  SELECT target_lat, target_lon, total_tons_clean
  FROM missions
  WHERE THEATER = 'MTO' AND has_valid_target_coords = 1
")
cat(sprintf("Loaded %d MTO missions.\n", nrow(mto_df)))

mto_cities <- data.frame(
  name = c("Rome", "Naples", "Foggia", "Palermo", "Tunis", "Tripoli", "Athens", "Belgrade", "Ploesti", "Budapest"),
  lon = c(12.4964, 14.2681, 15.5532, 13.3614, 10.1817, 13.1913, 23.7275, 20.4489, 26.0129, 19.0402),
  lat = c(41.9028, 40.8518, 41.4622, 38.1157, 36.8064, 32.8872, 37.9838, 44.7866, 44.9367, 47.4979)
) %>% st_as_sf(coords = c("lon", "lat"), crs = 4326, remove = FALSE)

p_mto <- ggplot() +
  geom_sf(data = world_countries, fill = "#ffffff", color = "#cbd5e1", linewidth = 0.25) +
  geom_point(data = mto_df, 
             aes(x = target_lon, y = target_lat, size = total_tons_clean),
             shape = 21,
             fill = "#dc2626",
             color = "#7f1d1d",
             stroke = 0.15,
             alpha = 0.4) +
  geom_sf(data = mto_cities, color = "#0f172a", size = 1.8, shape = 19) +
  geom_sf_text(data = mto_cities, aes(label = name), 
               color = "#0f172a", size = 3.0, fontface = "bold", 
               nudge_x = 0.4, nudge_y = 0.18, check_overlap = TRUE) +
  scale_size_area(
    name = "Bomb Weight",
    max_size = 9.0,
    breaks = c(5, 20, 50, 100),
    labels = c("5 t", "20 t", "50 t", "100 t")
  ) +
  coord_sf(xlim = c(6.0, 28.5), ylim = c(31.0, 48.5), expand = FALSE) +
  annotation_scale(location = "bl", width_hint = 0.2, style = "ticks",
                   text_col = "#64748b", line_col = "#64748b") +
  labs(
    title = "The Mediterranean Air Campaign (MTO, 1942–1945)",
    subtitle = "North Africa (Tunisia, Libya), Italian Peninsula, Balkans & Ploesti Oil Fields (12th & 15th Air Forces)",
    caption = "Source: USAF WWII THOR Database • Italy (409k t), Romania/Ploesti (43k t), Hungary (39k t), Yugoslavia (36k t)"
  ) +
  theme_theater_white(title_size = 14, subtitle_size = 9.5) +
  theme(
    legend.position = c(0.12, 0.25)
  ) +
  guides(size = guide_legend(override.aes = list(alpha = 0.75, fill = "#dc2626", color = "#7f1d1d")))

mto_png <- file.path(maps_dir, "wwii_mto_mediterranean_campaign.png")
mto_pdf <- file.path(maps_dir, "wwii_mto_mediterranean_campaign.pdf")
ggsave(mto_png, p_mto, width = 11, height = 8.5, dpi = 300)
ggsave(mto_pdf, p_mto, width = 11, height = 8.5, device = cairo_pdf)
cat("Saved MTO Mediterranean map.\n")

# ==============================================================================
# 4. PACIFIC & CHINA-BURMA-INDIA THEATERS (PTO / CBI)
# ==============================================================================
cat("\n[4/5] Querying Pacific & CBI Missions...\n")
pto_df <- dbGetQuery(con, "
  SELECT target_lat, target_lon, total_tons_clean
  FROM missions
  WHERE THEATER IN ('PTO', 'CBI') AND has_valid_target_coords = 1
")
cat(sprintf("Loaded %d PTO/CBI missions.\n", nrow(pto_df)))

pto_cities <- data.frame(
  name = c("Tokyo", "Osaka", "Hiroshima", "Nagasaki", "Manila", "Rangoon", "Calcutta", "Kunming", "Rabaul", "Saipan"),
  lon = c(139.6917, 135.5023, 132.4553, 129.8737, 120.9842, 96.1951, 88.3639, 102.7123, 152.1764, 145.7545),
  lat = c(35.6895, 34.6937, 34.3853, 32.7503, 14.5995, 16.8661, 22.5726, 25.0406, -4.1967, 15.1778)
) %>% st_as_sf(coords = c("lon", "lat"), crs = 4326, remove = FALSE)

p_pto <- ggplot() +
  geom_sf(data = world_countries, fill = "#ffffff", color = "#cbd5e1", linewidth = 0.25) +
  geom_point(data = pto_df, 
             aes(x = target_lon, y = target_lat, size = total_tons_clean),
             shape = 21,
             fill = "#dc2626",
             color = "#7f1d1d",
             stroke = 0.15,
             alpha = 0.4) +
  geom_sf(data = pto_cities, color = "#0f172a", size = 1.8, shape = 19) +
  geom_sf_text(data = pto_cities, aes(label = name), 
               color = "#0f172a", size = 3.0, fontface = "bold", 
               nudge_x = 1.2, nudge_y = 0.8, check_overlap = TRUE) +
  scale_size_area(
    name = "Bomb Weight",
    max_size = 8.5,
    breaks = c(5, 20, 50, 150),
    labels = c("5 t", "20 t", "50 t", "150 t")
  ) +
  coord_sf(xlim = c(85.0, 160.0), ylim = c(-10.0, 42.0), expand = FALSE) +
  annotation_scale(location = "bl", width_hint = 0.2, style = "ticks",
                   text_col = "#64748b", line_col = "#64748b") +
  labs(
    title = "The Pacific War & China-Burma-India Theater (PTO / CBI, 1942–1945)",
    subtitle = "Island-hopping campaign, Burma Road, Philippines liberation, and the B-29 strategic offensive on Japan",
    caption = "Source: USAF WWII THOR Database • Japan (188k t), Philippines (63k t), New Guinea (47k t), Burma (37k t)"
  ) +
  theme_theater_white(title_size = 14, subtitle_size = 9.5) +
  theme(
    legend.position = c(0.12, 0.30)
  ) +
  guides(size = guide_legend(override.aes = list(alpha = 0.75, fill = "#dc2626", color = "#7f1d1d")))

pto_png <- file.path(maps_dir, "wwii_pto_cbi_pacific_war.png")
pto_pdf <- file.path(maps_dir, "wwii_pto_cbi_pacific_war.pdf")
ggsave(pto_png, p_pto, width = 12, height = 8.5, dpi = 300)
ggsave(pto_pdf, p_pto, width = 12, height = 8.5, device = cairo_pdf)
cat("Saved PTO/CBI Pacific map.\n")

# ==============================================================================
# 5. GERMANY & AUSTRIA STRATEGIC CLOSEUP
# ==============================================================================
cat("\n[5/5] Querying Germany & Austria Bombing Missions...\n")
de_df <- dbGetQuery(con, "
  SELECT target_lat, target_lon, total_tons_clean
  FROM missions
  WHERE UPPER(TGT_COUNTRY) IN ('GERMANY', 'AUSTRIA') AND has_valid_target_coords = 1
")
cat(sprintf("Loaded %d Germany/Austria missions.\n", nrow(de_df)))

de_cities <- data.frame(
  name = c("Berlin", "Hamburg", "Essen (Ruhr)", "Cologne", "Frankfurt", "Munich", "Dresden", "Nuremberg", "Schweinfurt", "Leipzig", "Vienna"),
  lon = c(13.4050, 9.9937, 7.0116, 6.9603, 8.6821, 11.5820, 13.7373, 11.0767, 10.2333, 12.3731, 16.3738),
  lat = c(52.5200, 53.5511, 51.4556, 50.9375, 50.1109, 48.1351, 51.0504, 49.4521, 50.0500, 51.3397, 48.2082)
) %>% st_as_sf(coords = c("lon", "lat"), crs = 4326, remove = FALSE)

p_germany <- ggplot() +
  geom_sf(data = world_countries, fill = "#ffffff", color = "#cbd5e1", linewidth = 0.35) +
  geom_point(data = de_df, 
             aes(x = target_lon, y = target_lat, size = total_tons_clean),
             shape = 21,
             fill = "#dc2626",
             color = "#7f1d1d",
             stroke = 0.15,
             alpha = 0.35) +
  geom_sf(data = de_cities, color = "#0f172a", size = 2.0, shape = 19) +
  geom_sf_text(data = de_cities, aes(label = name), 
               color = "#0f172a", size = 3.2, fontface = "bold", 
               nudge_x = 0.28, nudge_y = 0.12, check_overlap = TRUE) +
  scale_size_area(
    name = "Bomb Weight",
    max_size = 9.5,
    breaks = c(10, 50, 100, 250, 500),
    labels = c("10 t", "50 t", "100 t", "250 t", "500 t")
  ) +
  coord_sf(xlim = c(5.5, 17.5), ylim = c(47.2, 55.0), expand = FALSE) +
  annotation_scale(location = "bl", width_hint = 0.2, style = "ticks",
                   text_col = "#64748b", line_col = "#64748b") +
  labs(
    title = "Strategic Bombing of the Third Reich: Germany & Austria (1942–1945)",
    subtitle = "The Ruhr industrial heartland ('Happy Valley'), synthetic oil plants, transportation grid, and major cities",
    caption = "Source: USAF WWII THOR Database • 2.14 Million Tons Dropped across 63,230 Missions"
  ) +
  theme_theater_white(title_size = 14, subtitle_size = 9.5) +
  theme(
    legend.position = c(0.88, 0.35)
  ) +
  guides(size = guide_legend(override.aes = list(alpha = 0.75, fill = "#dc2626", color = "#7f1d1d")))

germany_png <- file.path(maps_dir, "wwii_germany_strategic_bombing_closeup.png")
germany_pdf <- file.path(maps_dir, "wwii_germany_strategic_bombing_closeup.pdf")
ggsave(germany_png, p_germany, width = 10.5, height = 9, dpi = 300)
ggsave(germany_pdf, p_germany, width = 10.5, height = 9, device = cairo_pdf)
cat("Saved Germany & Austria strategic bombing map.\n")

dbDisconnect(con)
cat("\nALL 5 GLOBAL & THEATER MAPS RENDERED SUCCESSFULLY!\n")

#!/usr/bin/env Rscript
# generate_minimalist_maps.R - Minimalist, publication-grade white background maps of WWII bombings in Tunisia at Imada level

suppressPackageStartupMessages({
  library(sf)
  library(DBI)
  library(RSQLite)
  library(dplyr)
  library(ggplot2)
  library(scales)
  library(ggspatial)
})

script_arg <- grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE)
base_dir <- if (length(script_arg)) normalizePath(file.path(dirname(sub("^--file=", "", script_arg)), "..")) else getwd()
gis_dir <- file.path(base_dir, "data", "gis")
imada_shp <- file.path(gis_dir, "tunisia_imadas", "TN_sectors.shp")
gov_shp <- file.path(gis_dir, "tunisia_imadas", "TN_governorates.shp")
sqlite_path <- file.path(base_dir, "data", "processed", "thor_wwii.sqlite")
if (!file.exists(sqlite_path) && file.exists(paste0(sqlite_path, ".gz"))) {
  cat("Decompressing thor_wwii.sqlite.gz...\n")
  system(paste("gunzip -k", shQuote(paste0(sqlite_path, ".gz"))))
}

cat("Loading spatial boundaries...\n")
imadas <- st_read(imada_shp, quiet = TRUE) %>% st_transform(4326)
govs <- st_read(gov_shp, quiet = TRUE) %>% st_transform(4326)

cat("Fetching Tunisia missions...\n")
con <- dbConnect(RSQLite::SQLite(), sqlite_path)
bombs_df <- dbGetQuery(con, "
  SELECT WWII_ID, target_lat, target_lon, total_tons_clean, TGT_LOCATION, mission_date_iso
  FROM missions
  WHERE UPPER(TGT_COUNTRY) = 'TUNISIA' AND has_valid_target_coords = 1
")
dbDisconnect(con)

bombs_sf <- st_as_sf(bombs_df, coords = c("target_lon", "target_lat"), crs = 4326, remove = FALSE)

# Reference cities
cities <- data.frame(
  name = c("Tunis", "Bizerte", "Sousse", "Sfax", "Kairouan", "Gabès", "Kasserine", "Gafsa"),
  lon = c(10.1817, 9.8639, 10.6084, 10.7600, 10.1008, 10.0975, 8.7424, 8.7840),
  lat = c(36.8064, 37.2778, 35.8256, 34.7400, 35.6772, 33.8881, 35.2596, 34.4250)
)
cities_sf <- st_as_sf(cities, coords = c("lon", "lat"), crs = 4326, remove = FALSE)

# ==============================================================================
# 1. MINIMALIST NATIONAL MAP (CRIMSON ON WHITE)
# ==============================================================================
cat("Rendering Minimalist National Map (Crimson on White)...\n")

p_nat_crimson <- ggplot() +
  # 2,084 Imadas: super delicate light grey outlines
  geom_sf(data = imadas, fill = "#ffffff", color = "#e2e8f0", linewidth = 0.08) +
  # Governorates: subtle boundary guide
  geom_sf(data = govs, fill = NA, color = "#94a3b8", linewidth = 0.35) +
  # Bomb dots proportional to weight
  geom_sf(data = bombs_sf, 
          aes(size = total_tons_clean), 
          shape = 21,
          fill = "#dc2626",
          color = "#991b1b",
          stroke = 0.25,
          alpha = 0.55) +
  # City labels
  geom_sf(data = cities_sf, color = "#1e293b", size = 1.4, shape = 19) +
  geom_sf_text(data = cities_sf, aes(label = name), 
               color = "#0f172a", size = 2.7, fontface = "plain", 
               nudge_x = 0.16, nudge_y = 0.06, check_overlap = TRUE) +
  scale_size_area(
    name = "Bomb Weight",
    max_size = 8.5,
    breaks = c(1, 5, 10, 25, 50),
    labels = c("1 t", "5 t", "10 t", "25 t", "50 t")
  ) +
  coord_sf(xlim = c(7.8, 11.8), ylim = c(31.5, 37.6), expand = FALSE) +
  annotation_scale(location = "bl", width_hint = 0.2, style = "ticks",
                   text_col = "#64748b", line_col = "#64748b", text_cex = 0.65) +
  labs(
    title = "WWII Aerial Bombing Missions in Tunisia (1942–1943)",
    subtitle = "Imada (عمادة) administrative boundaries with individual strikes sized by bomb weight",
    caption = "Source: Theater History of Operations (THOR) Database"
  ) +
  theme_void() +
  theme(
    plot.background = element_rect(fill = "#ffffff", color = NA),
    panel.background = element_rect(fill = "#ffffff", color = NA),
    plot.title = element_text(color = "#0f172a", size = 13, face = "bold", margin = margin(t = 16, b = 4, l = 20)),
    plot.subtitle = element_text(color = "#64748b", size = 9, margin = margin(b = 10, l = 20)),
    plot.caption = element_text(color = "#94a3b8", size = 7.5, margin = margin(t = 8, b = 12, r = 20), hjust = 1),
    legend.position = c(0.85, 0.45),
    legend.background = element_rect(fill = "#ffffff", color = "#e2e8f0", linewidth = 0.4),
    legend.title = element_text(color = "#0f172a", size = 8.5, face = "bold"),
    legend.text = element_text(color = "#475569", size = 7.5),
    legend.margin = margin(6, 10, 6, 10)
  ) +
  guides(size = guide_legend(override.aes = list(alpha = 0.75, fill = "#dc2626", color = "#991b1b")))

nat_crimson_png <- file.path(gis_dir, "tunisia_minimalist_national_crimson.png")
nat_crimson_pdf <- file.path(gis_dir, "tunisia_minimalist_national_crimson.pdf")
ggsave(nat_crimson_png, p_nat_crimson, width = 8.5, height = 11, dpi = 300)
ggsave(nat_crimson_pdf, p_nat_crimson, width = 8.5, height = 11, device = cairo_pdf)
cat("Saved crimson national map.\n")

# ==============================================================================
# 2. MINIMALIST NATIONAL MAP (MONOCHROME / CHARCOAL ON WHITE)
# ==============================================================================
cat("Rendering Minimalist National Map (Monochrome Charcoal)...\n")

p_nat_mono <- ggplot() +
  geom_sf(data = imadas, fill = "#ffffff", color = "#e5e7eb", linewidth = 0.08) +
  geom_sf(data = govs, fill = NA, color = "#6b7280", linewidth = 0.35) +
  geom_sf(data = bombs_sf, 
          aes(size = total_tons_clean), 
          shape = 21,
          fill = "#18181b",
          color = "#09090b",
          stroke = 0.2,
          alpha = 0.5) +
  geom_sf(data = cities_sf, color = "#000000", size = 1.4, shape = 19) +
  geom_sf_text(data = cities_sf, aes(label = name), 
               color = "#000000", size = 2.7, fontface = "plain", 
               nudge_x = 0.16, nudge_y = 0.06, check_overlap = TRUE) +
  scale_size_area(
    name = "Bomb Weight",
    max_size = 8.5,
    breaks = c(1, 5, 10, 25, 50),
    labels = c("1 t", "5 t", "10 t", "25 t", "50 t")
  ) +
  coord_sf(xlim = c(7.8, 11.8), ylim = c(31.5, 37.6), expand = FALSE) +
  annotation_scale(location = "bl", width_hint = 0.2, style = "ticks",
                   text_col = "#6b7280", line_col = "#6b7280", text_cex = 0.65) +
  labs(
    title = "WWII Aerial Bombing Missions in Tunisia (1942–1943)",
    subtitle = "Imada (عمادة) administrative boundaries with individual strikes sized by bomb weight",
    caption = "Source: Theater History of Operations (THOR) Database"
  ) +
  theme_void() +
  theme(
    plot.background = element_rect(fill = "#ffffff", color = NA),
    panel.background = element_rect(fill = "#ffffff", color = NA),
    plot.title = element_text(color = "#18181b", size = 13, face = "bold", margin = margin(t = 16, b = 4, l = 20)),
    plot.subtitle = element_text(color = "#71717a", size = 9, margin = margin(b = 10, l = 20)),
    plot.caption = element_text(color = "#a1a1aa", size = 7.5, margin = margin(t = 8, b = 12, r = 20), hjust = 1),
    legend.position = c(0.85, 0.45),
    legend.background = element_rect(fill = "#ffffff", color = "#e5e7eb", linewidth = 0.4),
    legend.title = element_text(color = "#18181b", size = 8.5, face = "bold"),
    legend.text = element_text(color = "#52525b", size = 7.5),
    legend.margin = margin(6, 10, 6, 10)
  ) +
  guides(size = guide_legend(override.aes = list(alpha = 0.75, fill = "#18181b", color = "#09090b")))

nat_mono_png <- file.path(gis_dir, "tunisia_minimalist_national_monochrome.png")
nat_mono_pdf <- file.path(gis_dir, "tunisia_minimalist_national_monochrome.pdf")
ggsave(nat_mono_png, p_nat_mono, width = 8.5, height = 11, dpi = 300)
ggsave(nat_mono_pdf, p_nat_mono, width = 8.5, height = 11, device = cairo_pdf)
cat("Saved monochrome national map.\n")

# ==============================================================================
# 3. MINIMALIST NORTHERN REGIONAL FOCUS (TUNIS, BIZERTE, CAP BON)
# ==============================================================================
cat("Rendering Minimalist Northern Regional Map...\n")

p_north_mini <- ggplot() +
  geom_sf(data = imadas, fill = "#ffffff", color = "#e2e8f0", linewidth = 0.12) +
  geom_sf(data = govs, fill = NA, color = "#64748b", linewidth = 0.4) +
  geom_sf(data = bombs_sf, 
          aes(size = total_tons_clean), 
          shape = 21,
          fill = "#dc2626",
          color = "#991b1b",
          stroke = 0.25,
          alpha = 0.55) +
  geom_sf(data = filter(cities_sf, lat >= 35.8), color = "#0f172a", size = 1.8, shape = 19) +
  geom_sf_text(data = filter(cities_sf, lat >= 35.8), aes(label = name), 
               color = "#0f172a", size = 3.2, fontface = "plain", 
               nudge_x = 0.12, nudge_y = 0.05, check_overlap = TRUE) +
  scale_size_area(
    name = "Bomb Weight",
    max_size = 10,
    breaks = c(1, 5, 10, 25, 50),
    labels = c("1 t", "5 t", "10 t", "25 t", "50 t")
  ) +
  coord_sf(xlim = c(8.5, 11.2), ylim = c(35.6, 37.5), expand = FALSE) +
  annotation_scale(location = "bl", width_hint = 0.2, style = "ticks",
                   text_col = "#64748b", line_col = "#64748b") +
  labs(
    title = "Northern Tunisia & Cap Bon (1942–1943)",
    subtitle = "Imada sectors with strikes on Tunis, Bizerte, airfields, and Cap Bon",
    caption = "Source: USAF WWII THOR Database"
  ) +
  theme_void() +
  theme(
    plot.background = element_rect(fill = "#ffffff", color = NA),
    panel.background = element_rect(fill = "#ffffff", color = NA),
    plot.title = element_text(color = "#0f172a", size = 13, face = "bold", margin = margin(t = 14, b = 4, l = 16)),
    plot.subtitle = element_text(color = "#64748b", size = 8.5, margin = margin(b = 10, l = 16)),
    plot.caption = element_text(color = "#94a3b8", size = 7.5, margin = margin(t = 6, b = 8, r = 16), hjust = 1),
    legend.position = "right",
    legend.background = element_rect(fill = "#ffffff", color = "#e2e8f0", linewidth = 0.4),
    legend.title = element_text(color = "#0f172a", size = 8.5, face = "bold"),
    legend.text = element_text(color = "#475569", size = 7.5),
    legend.margin = margin(6, 10, 6, 10)
  ) +
  guides(size = guide_legend(override.aes = list(alpha = 0.75, fill = "#dc2626", color = "#991b1b")))

north_mini_png <- file.path(gis_dir, "tunisia_minimalist_north.png")
ggsave(north_mini_png, p_north_mini, width = 9.5, height = 8, dpi = 300)
cat("Saved minimalist north map.\n")

# ==============================================================================
# 4. MINIMALIST CENTRAL & SOUTHERN FOCUS (KASSERINE, SFAX, GABES, MARETH)
# ==============================================================================
cat("Rendering Minimalist Central & Southern Regional Map...\n")

p_south_mini <- ggplot() +
  geom_sf(data = imadas, fill = "#ffffff", color = "#e2e8f0", linewidth = 0.12) +
  geom_sf(data = govs, fill = NA, color = "#64748b", linewidth = 0.4) +
  geom_sf(data = bombs_sf, 
          aes(size = total_tons_clean), 
          shape = 21,
          fill = "#dc2626",
          color = "#991b1b",
          stroke = 0.25,
          alpha = 0.55) +
  geom_sf(data = filter(cities_sf, lat < 36.0), color = "#0f172a", size = 1.8, shape = 19) +
  geom_sf_text(data = filter(cities_sf, lat < 36.0), aes(label = name), 
               color = "#0f172a", size = 3.2, fontface = "plain", 
               nudge_x = 0.14, nudge_y = 0.05, check_overlap = TRUE) +
  scale_size_area(
    name = "Bomb Weight",
    max_size = 10,
    breaks = c(1, 5, 10, 25, 50),
    labels = c("1 t", "5 t", "10 t", "25 t", "50 t")
  ) +
  coord_sf(xlim = c(8.0, 11.5), ylim = c(33.0, 36.0), expand = FALSE) +
  annotation_scale(location = "bl", width_hint = 0.2, style = "ticks",
                   text_col = "#64748b", line_col = "#64748b") +
  labs(
    title = "Central & Southern Tunisia: Kasserine Pass & Mareth Line",
    subtitle = "Imada sectors with tactical strikes on Axis supply nodes and fortifications",
    caption = "Source: USAF WWII THOR Database"
  ) +
  theme_void() +
  theme(
    plot.background = element_rect(fill = "#ffffff", color = NA),
    panel.background = element_rect(fill = "#ffffff", color = NA),
    plot.title = element_text(color = "#0f172a", size = 13, face = "bold", margin = margin(t = 14, b = 4, l = 16)),
    plot.subtitle = element_text(color = "#64748b", size = 8.5, margin = margin(b = 10, l = 16)),
    plot.caption = element_text(color = "#94a3b8", size = 7.5, margin = margin(t = 6, b = 8, r = 16), hjust = 1),
    legend.position = "right",
    legend.background = element_rect(fill = "#ffffff", color = "#e2e8f0", linewidth = 0.4),
    legend.title = element_text(color = "#0f172a", size = 8.5, face = "bold"),
    legend.text = element_text(color = "#475569", size = 7.5),
    legend.margin = margin(6, 10, 6, 10)
  ) +
  guides(size = guide_legend(override.aes = list(alpha = 0.75, fill = "#dc2626", color = "#991b1b")))

south_mini_png <- file.path(gis_dir, "tunisia_minimalist_south_central.png")
ggsave(south_mini_png, p_south_mini, width = 9.5, height = 8, dpi = 300)
cat("Saved minimalist south-central map.\n")

cat("\nALL MINIMALIST MAPS COMPLETED SUCCESSFULLY!\n")

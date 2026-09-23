#!/usr/bin/env Rscript
# scripts/generate_tunisia_expanded_maps.R
# Minimalist, publication-grade white background maps of WWII bombings in Tunisia at Imada level.
# Generates 11 maps: 4-phase campaign progression (grid + standalones), density choropleth, target taxonomy, and tactical battle closeups.

suppressPackageStartupMessages({
  library(sf)
  library(DBI)
  library(RSQLite)
  library(dplyr)
  library(ggplot2)
  library(scales)
  library(ggspatial)
  library(patchwork)
})

script_arg <- grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE)
base_dir <- if (length(script_arg)) normalizePath(file.path(dirname(sub("^--file=", "", script_arg)), "..")) else getwd()
gis_dir <- file.path(base_dir, "data", "gis")
maps_dir <- file.path(base_dir, "maps")
dir.create(maps_dir, showWarnings = FALSE, recursive = TRUE)

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

cat("Fetching Tunisia missions from SQLite...\n")
con <- dbConnect(RSQLite::SQLite(), sqlite_path)
bombs_df <- dbGetQuery(con, "
  SELECT WWII_ID, target_lat, target_lon, total_tons_clean, TGT_LOCATION, 
         mission_date_iso, TGT_TYPE, TGT_INDUSTRY, TONS_OF_HE, TONS_OF_FRAG, TONS_OF_IC
  FROM missions
  WHERE UPPER(TGT_COUNTRY) = 'TUNISIA' AND has_valid_target_coords = 1
")
dbDisconnect(con)

cat(sprintf("Loaded %d Tunisia bombing missions.\n", nrow(bombs_df)))

# Enrich missions with historical campaign phases and target categories
bombs_df <- bombs_df %>%
  mutate(
    combo = paste(coalesce(TGT_TYPE, ""), coalesce(TGT_INDUSTRY, ""), coalesce(TGT_LOCATION, "")),
    target_category = case_when(
      grepl("AIR|AERODROME|AIRFIELD|HANGAR", combo, ignore.case = TRUE) ~ "Airfields & Airdromes",
      grepl("PORT|HARBOR|DOCK|SHIP|CONVOY|VESSEL", combo, ignore.case = TRUE) ~ "Ports, Harbors & Shipping",
      grepl("ROAD|HIGHWAY|BRIDGE|RAIL|R R|MARSHALLING|TRAIN|DEPOT|SUPPLY|OIL", combo, ignore.case = TRUE) ~ "Rail, Roads & Logistics",
      grepl("TROOP|GUN|TANK|FORT|POSITION|DEFENSE|BUNKER", combo, ignore.case = TRUE) ~ "Troops & Fortifications",
      TRUE ~ "Urban Centers & Tactical Targets"
    ),
    # Records dated before Nov 1942 or after May 1943 fall outside every phase.
    phase_id = case_when(
      mission_date_iso < "1942-11-01" ~ NA_character_,
      mission_date_iso < "1943-01-01" ~ "Phase 1: Torch & Buildup (Nov-Dec 1942)",
      mission_date_iso < "1943-03-01" ~ "Phase 2: Kasserine Pass (Jan-Feb 1943)",
      mission_date_iso < "1943-05-01" ~ "Phase 3: Mareth Line (Mar-Apr 1943)",
      mission_date_iso < "1943-06-01" ~ "Phase 4: Vulcan & Surrender (May 1943)",
      TRUE                            ~ NA_character_
    )
  )

cat(sprintf("Records outside the Nov 1942 - May 1943 phases: %d\n", sum(is.na(bombs_df$phase_id))))

# "N strikes (T t)" summary computed from the data for a set of records
strike_summary <- function(df) {
  sprintf("%s strikes (%s t)", comma(nrow(df)), comma(round(sum(df$total_tons_clean, na.rm = TRUE))))
}
phase_summary <- function(phase_str) strike_summary(filter(bombs_df, phase_id == phase_str))

bombs_sf <- st_as_sf(bombs_df, coords = c("target_lon", "target_lat"), crs = 4326, remove = FALSE)

# Reference cities
cities <- data.frame(
  name = c("Tunis", "Bizerte", "Sousse", "Sfax", "Kairouan", "Gabès", "Kasserine", "Gafsa", "Medenine", "Béja"),
  lon = c(10.1817, 9.8639, 10.6084, 10.7600, 10.1008, 10.0975, 8.7424, 8.7840, 10.4938, 9.1844),
  lat = c(36.8064, 37.2778, 35.8256, 34.7400, 35.6772, 33.8881, 35.2596, 34.4250, 33.3549, 36.7256)
)
cities_sf <- st_as_sf(cities, coords = c("lon", "lat"), crs = 4326, remove = FALSE)

# Reusable minimalist theme function
theme_minimalist_white <- function(title_size = 12, subtitle_size = 8.5) {
  theme_void() +
    theme(
      plot.background = element_rect(fill = "#ffffff", color = NA),
      panel.background = element_rect(fill = "#ffffff", color = NA),
      plot.title = element_text(color = "#0f172a", size = title_size, face = "bold", margin = margin(t = 12, b = 3, l = 12)),
      plot.subtitle = element_text(color = "#64748b", size = subtitle_size, margin = margin(b = 8, l = 12)),
      plot.caption = element_text(color = "#94a3b8", size = 7, margin = margin(t = 6, b = 10, r = 12), hjust = 1),
      legend.background = element_rect(fill = "#ffffff", color = "#e2e8f0", linewidth = 0.3),
      legend.title = element_text(color = "#0f172a", size = 8, face = "bold"),
      legend.text = element_text(color = "#475569", size = 7),
      legend.margin = margin(5, 8, 5, 8)
    )
}

# ==============================================================================
# MAP 1: 4-PHASE CAMPAIGN PROGRESSION (GRID)
# ==============================================================================
cat("\n[1/11] Rendering 4-Phase Campaign Progression Grid...\n")

make_phase_plot <- function(phase_str, title_label, subtitle_label, point_col = "#dc2626") {
  sub_bombs <- filter(bombs_sf, phase_id == phase_str)
  
  ggplot() +
    geom_sf(data = imadas, fill = "#ffffff", color = "#f1f5f9", linewidth = 0.05) +
    geom_sf(data = govs, fill = NA, color = "#cbd5e1", linewidth = 0.25) +
    geom_sf(data = sub_bombs, 
            aes(size = total_tons_clean), 
            shape = 21,
            fill = point_col,
            color = "#7f1d1d",
            stroke = 0.2,
            alpha = 0.6) +
    geom_sf(data = cities_sf, color = "#334155", size = 1.0, shape = 19) +
    geom_sf_text(data = cities_sf, aes(label = name), 
                 color = "#1e293b", size = 2.1, fontface = "plain", 
                 nudge_x = 0.16, nudge_y = 0.05, check_overlap = TRUE) +
    scale_size_area(
      name = "Bomb Tons",
      max_size = 6.5,
      breaks = c(5, 15, 30, 50),
      labels = c("5 t", "15 t", "30 t", "50 t")
    ) +
    coord_sf(xlim = c(7.8, 11.8), ylim = c(31.5, 37.6), expand = FALSE) +
    labs(title = title_label, subtitle = subtitle_label) +
    theme_void() +
    theme(
      plot.background = element_rect(fill = "#ffffff", color = "#f1f5f9", linewidth = 0.4),
      panel.background = element_rect(fill = "#ffffff", color = NA),
      plot.title = element_text(color = "#0f172a", size = 9.5, face = "bold", margin = margin(t = 8, b = 2, l = 8)),
      plot.subtitle = element_text(color = "#64748b", size = 7.2, margin = margin(b = 6, l = 8)),
      legend.position = "none"
    )
}

p1 <- make_phase_plot("Phase 1: Torch & Buildup (Nov-Dec 1942)", 
                      "Phase 1: Torch & Buildup (Nov–Dec 1942)", 
                      paste(phase_summary("Phase 1: Torch & Buildup (Nov-Dec 1942)"), "• Neutralizing coastal airfields & ports"))

p2 <- make_phase_plot("Phase 2: Kasserine Pass (Jan-Feb 1943)", 
                      "Phase 2: Kasserine Pass & Central Steppes (Jan–Feb 1943)", 
                      paste(phase_summary("Phase 2: Kasserine Pass (Jan-Feb 1943)"), "• Tactical support during Rommel's offensive"))

p3 <- make_phase_plot("Phase 3: Mareth Line (Mar-Apr 1943)", 
                      "Phase 3: Mareth Line & Coastal Breakthrough (Mar–Apr 1943)", 
                      paste(phase_summary("Phase 3: Mareth Line (Mar-Apr 1943)"), "• Massive interdiction & 8th Army breakthrough"))

p4 <- make_phase_plot("Phase 4: Vulcan & Surrender (May 1943)", 
                      "Phase 4: Operation Vulcan & Final Surrender (May 1943)", 
                      paste(phase_summary("Phase 4: Vulcan & Surrender (May 1943)"), "• Final encirclement at Tunis, Bizerte & Cap Bon"))

p_grid <- (p1 | p2) / (p3 | p4) +
  plot_annotation(
    title = "WWII Aerial Bombing Campaign Progression in Tunisia (1942–1943)",
    subtitle = "Chronological shift of Allied aerial bombardment across Tunisia's 2,084 Imadas (sectors)",
    caption = "Source: USAF WWII THOR Database • Unified Analysis & Cartography",
    theme = theme(
      plot.background = element_rect(fill = "#ffffff", color = NA),
      plot.title = element_text(color = "#0f172a", size = 14, face = "bold", margin = margin(t = 10, b = 4, l = 10)),
      plot.subtitle = element_text(color = "#64748b", size = 9.5, margin = margin(b = 10, l = 10)),
      plot.caption = element_text(color = "#94a3b8", size = 8, margin = margin(t = 8, b = 8, r = 10), hjust = 1)
    )
  )

grid_png <- file.path(maps_dir, "tunisia_campaign_phases_grid.png")
grid_pdf <- file.path(maps_dir, "tunisia_campaign_phases_grid.pdf")
ggsave(grid_png, p_grid, width = 11, height = 13, dpi = 300)
ggsave(grid_pdf, p_grid, width = 11, height = 13, device = cairo_pdf)
cat("Saved 4-phase campaign grid map.\n")

# ==============================================================================
# MAPS 2-5: STANDALONE HIGH-RES CAMPAIGN PHASE MAPS
# ==============================================================================
cat("\n[2-5/11] Rendering Standalone High-Resolution Campaign Phase Maps...\n")

make_standalone_phase <- function(phase_str, title_label, subtitle_label, out_prefix) {
  sub_bombs <- filter(bombs_sf, phase_id == phase_str)
  
  p <- ggplot() +
    geom_sf(data = imadas, fill = "#ffffff", color = "#e2e8f0", linewidth = 0.08) +
    geom_sf(data = govs, fill = NA, color = "#94a3b8", linewidth = 0.35) +
    geom_sf(data = sub_bombs, 
            aes(size = total_tons_clean), 
            shape = 21,
            fill = "#dc2626",
            color = "#7f1d1d",
            stroke = 0.25,
            alpha = 0.6) +
    geom_sf(data = cities_sf, color = "#0f172a", size = 1.4, shape = 19) +
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
      title = title_label,
      subtitle = subtitle_label,
      caption = "Source: USAF WWII THOR Database • Imada-Level Boundaries"
    ) +
    theme_minimalist_white(title_size = 13, subtitle_size = 9) +
    theme(
      legend.position = c(0.85, 0.45),
      legend.margin = margin(6, 10, 6, 10)
    ) +
    guides(size = guide_legend(override.aes = list(alpha = 0.75, fill = "#dc2626", color = "#7f1d1d")))
  
  png_path <- file.path(maps_dir, paste0(out_prefix, ".png"))
  pdf_path <- file.path(maps_dir, paste0(out_prefix, ".pdf"))
  ggsave(png_path, p, width = 8.5, height = 11, dpi = 300)
  ggsave(pdf_path, p, width = 8.5, height = 11, device = cairo_pdf)
  cat(sprintf("Saved %s\n", out_prefix))
}

make_standalone_phase(
  "Phase 1: Torch & Buildup (Nov-Dec 1942)",
  "Tunisia Campaign Phase 1: Torch & Airfield Neutralization (Nov–Dec 1942)",
  paste(phase_summary("Phase 1: Torch & Buildup (Nov-Dec 1942)"), "• Early Allied strikes against Axis airfields and coastal ports"),
  "tunisia_phase1_torch_airfields"
)

make_standalone_phase(
  "Phase 2: Kasserine Pass (Jan-Feb 1943)",
  "Tunisia Campaign Phase 2: Battle of Kasserine Pass (Jan–Feb 1943)",
  paste(phase_summary("Phase 2: Kasserine Pass (Jan-Feb 1943)"), "• Close air support and tactical interdiction during Axis winter counter-offensives"),
  "tunisia_phase2_kasserine_pass"
)

make_standalone_phase(
  "Phase 3: Mareth Line (Mar-Apr 1943)",
  "Tunisia Campaign Phase 3: Mareth Line & Coastal Breakthrough (Mar–Apr 1943)",
  paste(phase_summary("Phase 3: Mareth Line (Mar-Apr 1943)"), "• Intense bombardment supporting 8th Army breakthrough and retreat north"),
  "tunisia_phase3_mareth_line"
)

make_standalone_phase(
  "Phase 4: Vulcan & Surrender (May 1943)",
  "Tunisia Campaign Phase 4: Operation Vulcan & Axis Surrender (May 1943)",
  paste(phase_summary("Phase 4: Vulcan & Surrender (May 1943)"), "• Final destruction of Axis bridgehead in Tunis, Bizerte, and Cap Bon"),
  "tunisia_phase4_vulcan_surrender"
)

# ==============================================================================
# MAP 6: IMADA-LEVEL BOMBING DENSITY (CHOROPLETH + STRIKES)
# ==============================================================================
cat("\n[6/11] Rendering Imada-Level Bombing Density Choropleth...\n")

imada_csv_path <- file.path(gis_dir, "tunisia_bombing_by_imada.csv")
imada_stats <- read.csv(imada_csv_path, fileEncoding = "UTF-8")

imadas_density <- imadas %>%
  left_join(imada_stats, by = c("sec_uid" = "imada_uid"))

p_density <- ggplot() +
  # Choropleth of all 2,084 Imadas
  geom_sf(data = imadas_density, 
          aes(fill = total_bomb_tons), 
          color = "#e2e8f0", 
          linewidth = 0.08) +
  scale_fill_gradientn(
    name = "Total Tons / Imada",
    colors = c("#fef2f2", "#fca5a5", "#ef4444", "#b91c1c", "#450a0a"),
    na.value = "#ffffff",
    trans = "pseudo_log",
    breaks = c(1, 10, 50, 200, 800),
    labels = c("1 t", "10 t", "50 t", "200 t", "800 t")
  ) +
  geom_sf(data = govs, fill = NA, color = "#475569", linewidth = 0.4) +
  # Subtle strike dots overlay
  geom_sf(data = bombs_sf, 
          aes(size = total_tons_clean), 
          shape = 21,
          fill = "#991b1b",
          color = "#450a0a",
          stroke = 0.2,
          alpha = 0.45) +
  scale_size_area(
    name = "Strike Weight",
    max_size = 7.5,
    breaks = c(5, 20, 50),
    labels = c("5 t", "20 t", "50 t")
  ) +
  geom_sf(data = cities_sf, color = "#0f172a", size = 1.4, shape = 19) +
  geom_sf_text(data = cities_sf, aes(label = name), 
               color = "#0f172a", size = 2.7, fontface = "plain", 
               nudge_x = 0.16, nudge_y = 0.06, check_overlap = TRUE) +
  coord_sf(xlim = c(7.8, 11.8), ylim = c(31.5, 37.6), expand = FALSE) +
  annotation_scale(location = "bl", width_hint = 0.2, style = "ticks",
                   text_col = "#64748b", line_col = "#64748b", text_cex = 0.65) +
  labs(
    title = "WWII Bombing Density per Imada (عمادة) Sector in Tunisia",
    subtitle = "Cumulative ordnance tonnage per administrative sector across 2,084 Imadas",
    caption = sprintf("Source: USAF WWII THOR Database • Spatial aggregation across %d bombed Imadas", sum(imada_stats$bomb_strikes > 0))
  ) +
  theme_minimalist_white(title_size = 13, subtitle_size = 9) +
  theme(
    legend.position = c(0.85, 0.42),
    legend.box = "vertical"
  )

density_png <- file.path(maps_dir, "tunisia_imada_bombing_density.png")
density_pdf <- file.path(maps_dir, "tunisia_imada_bombing_density.pdf")
ggsave(density_png, p_density, width = 8.5, height = 11, dpi = 300)
ggsave(density_pdf, p_density, width = 8.5, height = 11, device = cairo_pdf)
cat("Saved Imada density choropleth.\n")

# ==============================================================================
# MAP 7: TARGET TYPE TAXONOMY MAP
# ==============================================================================
cat("\n[7/11] Rendering Target Type Taxonomy Map...\n")

target_palette <- c(
  "Airfields & Airdromes"             = "#0284c7", # Sky Blue
  "Ports, Harbors & Shipping"         = "#1e3a8a", # Deep Navy
  "Rail, Roads & Logistics"           = "#059669", # Emerald Green
  "Troops & Fortifications"           = "#dc2626", # Crimson Red
  "Urban Centers & Tactical Targets"  = "#d97706"  # Amber Orange
)

p_targets <- ggplot() +
  geom_sf(data = imadas, fill = "#ffffff", color = "#e2e8f0", linewidth = 0.08) +
  geom_sf(data = govs, fill = NA, color = "#94a3b8", linewidth = 0.35) +
  geom_sf(data = bombs_sf, 
          aes(size = total_tons_clean, fill = target_category, color = target_category), 
          shape = 21,
          stroke = 0.2,
          alpha = 0.6) +
  scale_fill_manual(name = "Target Category", values = target_palette) +
  scale_color_manual(name = "Target Category", values = target_palette) +
  scale_size_area(
    name = "Bomb Weight",
    max_size = 8.0,
    breaks = c(1, 5, 10, 25, 50),
    labels = c("1 t", "5 t", "10 t", "25 t", "50 t")
  ) +
  geom_sf(data = cities_sf, color = "#0f172a", size = 1.4, shape = 19) +
  geom_sf_text(data = cities_sf, aes(label = name), 
               color = "#0f172a", size = 2.7, fontface = "plain", 
               nudge_x = 0.16, nudge_y = 0.06, check_overlap = TRUE) +
  coord_sf(xlim = c(7.8, 11.8), ylim = c(31.5, 37.6), expand = FALSE) +
  annotation_scale(location = "bl", width_hint = 0.2, style = "ticks",
                   text_col = "#64748b", line_col = "#64748b", text_cex = 0.65) +
  labs(
    title = "Target Functional Taxonomy: WWII Aerial Bombing in Tunisia",
    subtitle = {
      n_cat <- table(bombs_df$target_category)
      sprintf("Airfields (%d strikes), Harbors (%d), Rail/Roads (%d), Troops/Forts (%d), Urban/Tactical (%d)",
              n_cat[["Airfields & Airdromes"]], n_cat[["Ports, Harbors & Shipping"]], n_cat[["Rail, Roads & Logistics"]],
              n_cat[["Troops & Fortifications"]], n_cat[["Urban Centers & Tactical Targets"]])
    },
    caption = "Source: USAF WWII THOR Database • Classified by target types and industrial codes"
  ) +
  theme_minimalist_white(title_size = 13, subtitle_size = 8.8) +
  theme(
    legend.position = c(0.82, 0.42),
    legend.box = "vertical"
  ) +
  guides(
    fill = guide_legend(override.aes = list(size = 4.5, alpha = 0.85)),
    color = guide_legend(override.aes = list(size = 4.5, alpha = 0.85)),
    size = guide_legend(override.aes = list(fill = "#475569", color = "#1e293b"))
  )

target_png <- file.path(maps_dir, "tunisia_target_types_distribution.png")
target_pdf <- file.path(maps_dir, "tunisia_target_types_distribution.pdf")
ggsave(target_png, p_targets, width = 9.0, height = 11, dpi = 300)
ggsave(target_pdf, p_targets, width = 9.0, height = 11, device = cairo_pdf)
cat("Saved target taxonomy map.\n")

# ==============================================================================
# MAPS 8-11: HIGH-RESOLUTION TACTICAL BATTLEFIELD CLOSEUPS (IMADA LEVEL)
# ==============================================================================
cat("\n[8-11/11] Rendering Tactical Battlefield Micro-Regional Closeups...\n")

make_tactical_closeup <- function(xlims, ylims, title_str, subtitle_str, out_prefix, cities_in_view) {
  in_view <- filter(bombs_df, between(target_lon, xlims[1], xlims[2]), between(target_lat, ylims[1], ylims[2]))
  subtitle_str <- paste(strike_summary(in_view), "•", subtitle_str)
  p <- ggplot() +
    geom_sf(data = imadas, fill = "#ffffff", color = "#cbd5e1", linewidth = 0.15) +
    geom_sf(data = govs, fill = NA, color = "#475569", linewidth = 0.5) +
    geom_sf(data = bombs_sf, 
            aes(size = total_tons_clean), 
            shape = 21,
            fill = "#dc2626",
            color = "#7f1d1d",
            stroke = 0.3,
            alpha = 0.6) +
    geom_sf(data = cities_in_view, color = "#0f172a", size = 2.0, shape = 19) +
    geom_sf_text(data = cities_in_view, aes(label = name), 
                 color = "#0f172a", size = 3.6, fontface = "bold", 
                 nudge_x = 0.05, nudge_y = 0.03, check_overlap = TRUE) +
    scale_size_area(
      name = "Bomb Weight",
      max_size = 11,
      breaks = c(1, 5, 10, 25, 50),
      labels = c("1 t", "5 t", "10 t", "25 t", "50 t")
    ) +
    coord_sf(xlim = xlims, ylim = ylims, expand = FALSE) +
    annotation_scale(location = "bl", width_hint = 0.25, style = "ticks",
                     text_col = "#475569", line_col = "#475569") +
    labs(
      title = title_str,
      subtitle = subtitle_str,
      caption = "Source: USAF WWII THOR Database • Detailed Imada (عمادة) boundaries"
    ) +
    theme_minimalist_white(title_size = 13.5, subtitle_size = 9) +
    theme(
      legend.position = "right",
      legend.margin = margin(8, 12, 8, 12)
    ) +
    guides(size = guide_legend(override.aes = list(alpha = 0.8, fill = "#dc2626", color = "#7f1d1d")))
  
  png_path <- file.path(maps_dir, paste0(out_prefix, ".png"))
  pdf_path <- file.path(maps_dir, paste0(out_prefix, ".pdf"))
  ggsave(png_path, p, width = 10, height = 7.5, dpi = 300)
  ggsave(pdf_path, p, width = 10, height = 7.5, device = cairo_pdf)
  cat(sprintf("Saved %s\n", out_prefix))
}

# 8. Northern Naval Hub (Tunis, Bizerte, Mateur)
tunis_bizerte_cities <- data.frame(
  name = c("Tunis", "Bizerte", "La Goulette", "Mateur", "Ferryville (Menzel Bourguiba)", "Medjez el Bab"),
  lon = c(10.1817, 9.8639, 10.3060, 9.6644, 9.7911, 9.6108),
  lat = c(36.8064, 37.2778, 36.8181, 37.0400, 37.1539, 36.6497)
) %>% st_as_sf(coords = c("lon", "lat"), crs = 4326, remove = FALSE)

make_tactical_closeup(
  xlims = c(9.3, 10.6), 
  ylims = c(36.4, 37.4),
  title_str = "Tactical Closeup: Greater Tunis & Bizerte Naval Complex",
  subtitle_str = "Airfields, gun positions and towns around Bizerte, Mateur, Medjez el Bab and the Tunis plain",
  out_prefix = "tunisia_tactical_tunis_bizerte",
  cities_in_view = tunis_bizerte_cities
)

# 9. Mareth Line & Gulf of Gabès
mareth_cities <- data.frame(
  name = c("Gabès", "Mareth", "Medenine", "Teboulbou", "Matmata", "El Hamma"),
  lon = c(10.0975, 10.2922, 10.4938, 10.1800, 9.9722, 9.7967),
  lat = c(33.8881, 33.6133, 33.3549, 33.7800, 33.5456, 33.8864)
) %>% st_as_sf(coords = c("lon", "lat"), crs = 4326, remove = FALSE)

make_tactical_closeup(
  xlims = c(9.5, 10.7), 
  ylims = c(33.2, 34.15),
  title_str = "Tactical Closeup: The Mareth Line & Gulf of Gabès",
  subtitle_str = "Airfields, roads and troop targets at Gabès, Zarat, Mareth, El Hamma and Medenine",
  out_prefix = "tunisia_tactical_mareth_gabes",
  cities_in_view = mareth_cities
)

# 10. Kasserine Pass & Central Steppes
kasserine_cities <- data.frame(
  name = c("Kasserine", "Sbeitla", "Fériana", "Thélepte Airfield", "Faïd Pass", "Gafsa", "Sidi Bouzid"),
  lon = c(8.7424, 9.1292, 8.5714, 8.5958, 9.5333, 8.7840, 9.4847),
  lat = c(35.2596, 35.3047, 34.9542, 35.0119, 35.0667, 34.4250, 35.0381)
) %>% st_as_sf(coords = c("lon", "lat"), crs = 4326, remove = FALSE)

make_tactical_closeup(
  xlims = c(8.2, 9.8), 
  ylims = c(34.2, 35.6),
  title_str = "Tactical Closeup: Kasserine, Gafsa & Central Front",
  subtitle_str = "Troops, vehicles and roads at Kasserine, Faïd Pass, El Guettar, Sened, Gafsa and Maknassy",
  out_prefix = "tunisia_tactical_kasserine_gafsa",
  cities_in_view = kasserine_cities
)

# 11. Sahel Ports & Coastal Rail Line
sahel_cities <- data.frame(
  name = c("Sousse", "Sfax", "Monastir", "Mahdia", "El Djem", "Enfidha"),
  lon = c(10.6084, 10.7600, 10.8261, 11.0622, 10.7167, 10.3808),
  lat = c(35.8256, 34.7400, 35.7780, 35.5047, 35.3000, 36.1350)
) %>% st_as_sf(coords = c("lon", "lat"), crs = 4326, remove = FALSE)

make_tactical_closeup(
  xlims = c(10.1, 11.2), 
  ylims = c(34.5, 36.3),
  title_str = "Tactical Closeup: Eastern Sahel Ports & Rail Corridors",
  subtitle_str = "Airfields, harbors, vehicles and rail targets at Sousse, Sfax, La Fauconnerie, Enfidaville and El Djem",
  out_prefix = "tunisia_tactical_sahel_ports",
  cities_in_view = sahel_cities
)

cat("\nALL 11 EXPANDED TUNISIA MAPS RENDERED SUCCESSFULLY!\n")

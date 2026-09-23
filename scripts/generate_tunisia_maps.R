#!/usr/bin/env Rscript
# generate_tunisia_maps.R - High-resolution cartographic maps of WWII bombing missions in Tunisia at Imada level

# Use the bundled Quarto pandoc on macOS when present; otherwise pandoc on PATH.
if (dir.exists("/Applications/quarto/bin/tools/aarch64")) Sys.setenv(RSTUDIO_PANDOC = "/Applications/quarto/bin/tools/aarch64")

suppressPackageStartupMessages({
  library(sf)
  library(DBI)
  library(RSQLite)
  library(dplyr)
  library(ggplot2)
  library(viridis)
  library(scales)
  library(ggspatial)
  library(leaflet)
  library(htmlwidgets)
})

script_arg <- grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE)
base_dir <- if (length(script_arg)) normalizePath(file.path(dirname(sub("^--file=", "", script_arg)), "..")) else getwd()
gis_dir <- file.path(base_dir, "data", "gis")
docs_dir <- file.path(base_dir, "docs")
imada_shp <- file.path(gis_dir, "tunisia_imadas", "TN_sectors.shp")
gov_shp <- file.path(gis_dir, "tunisia_imadas", "TN_governorates.shp")
sqlite_path <- file.path(base_dir, "data", "processed", "thor_wwii.sqlite")
if (!file.exists(sqlite_path) && file.exists(paste0(sqlite_path, ".gz"))) {
  cat("Decompressing thor_wwii.sqlite.gz...\n")
  system(paste("gunzip -k", shQuote(paste0(sqlite_path, ".gz"))))
}

cat("Loading Imada and Governorate boundary shapefiles...\n")
imadas <- st_read(imada_shp, quiet = TRUE)
imadas <- st_transform(imadas, 4326)

govs <- st_read(gov_shp, quiet = TRUE)
govs <- st_transform(govs, 4326)

cat("Reading Tunisia bombing missions from database...\n")
con <- dbConnect(RSQLite::SQLite(), sqlite_path)
bombs_df <- dbGetQuery(con, "
  SELECT 
    WWII_ID, 
    mission_date_iso, 
    target_lat, 
    target_lon, 
    TGT_LOCATION, 
    total_tons_clean, 
    TONS_OF_HE, 
    TONS_OF_IC, 
    TONS_OF_FRAG, 
    aircraft_full_name, 
    country_flying_mission_clean,
    UNIT_ID,
    NAF
  FROM missions
  WHERE UPPER(TGT_COUNTRY) = 'TUNISIA' AND has_valid_target_coords = 1
")
dbDisconnect(con)
cat(sprintf("Loaded %d THOR records in Tunisia.\n", nrow(bombs_df)))

bombs_sf <- st_as_sf(bombs_df, coords = c("target_lon", "target_lat"), crs = 4326, remove = FALSE)

# Key historical city reference coordinates for labeling
cities <- data.frame(
  name = c("Tunis", "Bizerte", "Sousse", "Sfax", "Kairouan", "Gabès", "Kasserine", "Gafsa", "Mareth", "Enfidha"),
  lon = c(10.1817, 9.8639, 10.6084, 10.7600, 10.1008, 10.0975, 8.7424, 8.7840, 10.2922, 10.3786),
  lat = c(36.8064, 37.2778, 35.8256, 34.7400, 35.6772, 33.8881, 35.2596, 34.4250, 33.6125, 36.1347)
)
cities_sf <- st_as_sf(cities, coords = c("lon", "lat"), crs = 4326, remove = FALSE)

# ==============================================================================
# 1. NATIONAL MAP (DARK THEME)
# ==============================================================================
cat("\nGenerating National Map (Dark Theme)...\n")
p_dark <- ggplot() +
  # Imada level polygon boundaries
  geom_sf(data = imadas, fill = "#131c2e", color = "#2a3b5c", linewidth = 0.12) +
  # Governorate level outline boundaries
  geom_sf(data = govs, fill = NA, color = "#60a5fa", linewidth = 0.45, alpha = 0.7) +
  # Individual bomb strike dots proportional to bomb weight
  geom_sf(data = bombs_sf, 
          aes(size = total_tons_clean, color = total_tons_clean), 
          alpha = 0.65) +
  # Reference city points
  geom_sf(data = cities_sf, color = "#ffffff", size = 1.6, shape = 18) +
  geom_sf_text(data = cities_sf, aes(label = name), 
               color = "#ffffff", size = 2.8, fontface = "bold", 
               nudge_x = 0.18, nudge_y = 0.08, check_overlap = TRUE) +
  scale_size_area(name = "Bomb Weight (Tons)", max_size = 9,
                  breaks = c(1, 5, 10, 20, 50),
                  labels = c("1 t", "5 t", "10 t", "20 t", "50 t")) +
  scale_color_viridis_c(name = "Bomb Weight (Tons)", option = "inferno",
                        breaks = c(1, 5, 10, 20, 50),
                        labels = c("1 t", "5 t", "10 t", "20 t", "50 t"),
                        direction = 1) +
  coord_sf(xlim = c(7.8, 11.8), ylim = c(31.5, 37.6), expand = FALSE) +
  annotation_scale(location = "bl", width_hint = 0.25, style = "ticks",
                   text_col = "#94a3b8", line_col = "#94a3b8") +
  annotation_north_arrow(location = "tr", which_north = "true",
                         pad_x = unit(0.3, "in"), pad_y = unit(0.3, "in"),
                         style = north_arrow_minimal(text_col = "#94a3b8", line_col = "#94a3b8")) +
  labs(
    title = "World War II Aerial Bombing Operations in Tunisia (1942–1943)",
    subtitle = "Allied air strikes across 2,084 Imada (عمادة) administrative sectors\nCircle dimensions proportional to total bomb weight dropped per mission",
    caption = "Data Source: Theater History of Operations (THOR) Database (USAAF/RAF) | Boundaries: Tunisia Imada / Sector Shapefile"
  ) +
  theme_void() +
  theme(
    plot.background = element_rect(fill = "#090d16", color = NA),
    panel.background = element_rect(fill = "#090d16", color = NA),
    plot.title = element_text(color = "#38bdf8", size = 15, face = "bold", margin = margin(t = 12, b = 4, l = 16)),
    plot.subtitle = element_text(color = "#cbd5e1", size = 10, lineheight = 1.2, margin = margin(b = 10, l = 16)),
    plot.caption = element_text(color = "#64748b", size = 8, margin = margin(t = 10, b = 10, r = 16), hjust = 1),
    legend.position = "right",
    legend.background = element_rect(fill = "#131c2e", color = "#2a3b5c"),
    legend.title = element_text(color = "#f8fafc", size = 9, face = "bold"),
    legend.text = element_text(color = "#cbd5e1", size = 8),
    legend.box.margin = margin(r = 16),
    legend.margin = margin(8, 12, 8, 12)
  ) +
  guides(
    size = guide_legend(override.aes = list(alpha = 0.85, color = "#f97316")),
    color = "none"
  )

dark_png <- file.path(gis_dir, "tunisia_bombing_imadas_national_dark.png")
ggsave(dark_png, p_dark, width = 9.5, height = 12, dpi = 300)
cat(sprintf("Saved dark national map: %s\n", dark_png))

# ==============================================================================
# 2. NATIONAL MAP (LIGHT / PUBLICATION PRINT THEME)
# ==============================================================================
cat("\nGenerating National Map (Light Publication Theme)...\n")
p_light <- ggplot() +
  # Imada level polygon boundaries
  geom_sf(data = imadas, fill = "#f8fafc", color = "#cbd5e1", linewidth = 0.12) +
  # Governorate level boundaries
  geom_sf(data = govs, fill = NA, color = "#475569", linewidth = 0.45) +
  # Individual bomb strike dots proportional to bomb weight
  geom_sf(data = bombs_sf, 
          aes(size = total_tons_clean, color = total_tons_clean), 
          alpha = 0.6) +
  # Reference city points
  geom_sf(data = cities_sf, color = "#0f172a", size = 1.8, shape = 18) +
  geom_sf_text(data = cities_sf, aes(label = name), 
               color = "#0f172a", size = 3.0, fontface = "bold", 
               nudge_x = 0.18, nudge_y = 0.08, check_overlap = TRUE) +
  scale_size_area(name = "Bomb Weight (Tons)", max_size = 9,
                  breaks = c(1, 5, 10, 20, 50),
                  labels = c("1 t", "5 t", "10 t", "20 t", "50 t")) +
  scale_color_gradient(name = "Bomb Weight (Tons)",
                       low = "#ea580c", high = "#7f1d1d",
                       breaks = c(1, 5, 10, 20, 50),
                       labels = c("1 t", "5 t", "10 t", "20 t", "50 t")) +
  coord_sf(xlim = c(7.8, 11.8), ylim = c(31.5, 37.6), expand = FALSE) +
  annotation_scale(location = "bl", width_hint = 0.25, style = "ticks",
                   text_col = "#1e293b", line_col = "#1e293b") +
  annotation_north_arrow(location = "tr", which_north = "true",
                         pad_x = unit(0.3, "in"), pad_y = unit(0.3, "in"),
                         style = north_arrow_minimal(text_col = "#1e293b", line_col = "#1e293b")) +
  labs(
    title = "World War II Aerial Bombing Operations in Tunisia (1942–1943)",
    subtitle = "Allied air missions plotted across 2,084 Imada (عمادة) administrative boundaries\nEach circle dimension is proportional to total bomb tonnage dropped",
    caption = "Data Source: Theater History of Operations (THOR) Database | Boundary data: Tunisia Imada / Sector Shapefile"
  ) +
  theme_void() +
  theme(
    plot.background = element_rect(fill = "#ffffff", color = NA),
    panel.background = element_rect(fill = "#ffffff", color = NA),
    plot.title = element_text(color = "#0f172a", size = 15, face = "bold", margin = margin(t = 12, b = 4, l = 16)),
    plot.subtitle = element_text(color = "#475569", size = 10, lineheight = 1.2, margin = margin(b = 10, l = 16)),
    plot.caption = element_text(color = "#64748b", size = 8, margin = margin(t = 10, b = 10, r = 16), hjust = 1),
    legend.position = "right",
    legend.background = element_rect(fill = "#f1f5f9", color = "#cbd5e1"),
    legend.title = element_text(color = "#0f172a", size = 9, face = "bold"),
    legend.text = element_text(color = "#334155", size = 8),
    legend.box.margin = margin(r = 16),
    legend.margin = margin(8, 12, 8, 12)
  ) +
  guides(
    size = guide_legend(override.aes = list(alpha = 0.85, color = "#ea580c")),
    color = "none"
  )

light_png <- file.path(gis_dir, "tunisia_bombing_imadas_national_light.png")
light_pdf <- file.path(gis_dir, "tunisia_bombing_imadas_national_light.pdf")
ggsave(light_png, p_light, width = 9.5, height = 12, dpi = 300)
ggsave(light_pdf, p_light, width = 9.5, height = 12, device = cairo_pdf)
cat(sprintf("Saved light national map: %s and %s\n", light_png, light_pdf))

# ==============================================================================
# 3. NORTHERN TUNISIA REGIONAL FOCUS (TUNIS, BIZERTE, CAP BON)
# ==============================================================================
cat("\nGenerating Northern Tunisia Regional Focus Map...\n")
p_north <- ggplot() +
  geom_sf(data = imadas, fill = "#1e293b", color = "#334155", linewidth = 0.18) +
  geom_sf(data = govs, fill = NA, color = "#93c5fd", linewidth = 0.5) +
  geom_sf(data = bombs_sf, 
          aes(size = total_tons_clean, color = total_tons_clean), 
          alpha = 0.7) +
  geom_sf(data = filter(cities_sf, lat >= 35.8), color = "#ffffff", size = 2.0, shape = 18) +
  geom_sf_text(data = filter(cities_sf, lat >= 35.8), aes(label = name), 
               color = "#ffffff", size = 3.4, fontface = "bold", 
               nudge_x = 0.12, nudge_y = 0.05, check_overlap = TRUE) +
  scale_size_area(name = "Bomb Weight (Tons)", max_size = 11,
                  breaks = c(1, 5, 10, 20, 50),
                  labels = c("1 t", "5 t", "10 t", "20 t", "50 t")) +
  scale_color_viridis_c(name = "Bomb Weight (Tons)", option = "plasma",
                        breaks = c(1, 5, 10, 20, 50),
                        labels = c("1 t", "5 t", "10 t", "20 t", "50 t")) +
  coord_sf(xlim = c(8.5, 11.2), ylim = c(35.6, 37.5), expand = FALSE) +
  annotation_scale(location = "bl", width_hint = 0.25, style = "ticks",
                   text_col = "#94a3b8", line_col = "#94a3b8") +
  labs(
    title = "Northern Tunisia & Cap Bon Aerial Interdiction (1942–1943)",
    subtitle = "Concentrated strikes on Tunis, Bizerte naval base, airfields, and Cap Bon evacuation corridor\nOverlay on Sector / Imada boundaries",
    caption = "Source: USAF WWII THOR Database"
  ) +
  theme_void() +
  theme(
    plot.background = element_rect(fill = "#0f172a", color = NA),
    panel.background = element_rect(fill = "#0f172a", color = NA),
    plot.title = element_text(color = "#38bdf8", size = 14, face = "bold", margin = margin(t = 12, b = 4, l = 16)),
    plot.subtitle = element_text(color = "#cbd5e1", size = 9.5, margin = margin(b = 10, l = 16)),
    plot.caption = element_text(color = "#64748b", size = 8, margin = margin(t = 8, b = 8, r = 16), hjust = 1),
    legend.position = "right",
    legend.background = element_rect(fill = "#1e293b", color = "#334155"),
    legend.title = element_text(color = "#f8fafc", size = 9, face = "bold"),
    legend.text = element_text(color = "#cbd5e1", size = 8),
    legend.box.margin = margin(r = 16),
    legend.margin = margin(8, 12, 8, 12)
  ) +
  guides(
    size = guide_legend(override.aes = list(alpha = 0.85, color = "#f43f5e")),
    color = "none"
  )

north_png <- file.path(gis_dir, "tunisia_bombing_north.png")
ggsave(north_png, p_north, width = 10, height = 8.5, dpi = 300)
cat(sprintf("Saved north focus map: %s\n", north_png))

# ==============================================================================
# 4. CENTRAL & SOUTHERN TUNISIA FOCUS (KASSERINE PASS, SFAX, GABES, MARETH)
# ==============================================================================
cat("\nGenerating Central & Southern Tunisia Regional Focus Map...\n")
p_south <- ggplot() +
  geom_sf(data = imadas, fill = "#1e293b", color = "#334155", linewidth = 0.18) +
  geom_sf(data = govs, fill = NA, color = "#93c5fd", linewidth = 0.5) +
  geom_sf(data = bombs_sf, 
          aes(size = total_tons_clean, color = total_tons_clean), 
          alpha = 0.7) +
  geom_sf(data = filter(cities_sf, lat < 36.0), color = "#ffffff", size = 2.0, shape = 18) +
  geom_sf_text(data = filter(cities_sf, lat < 36.0), aes(label = name), 
               color = "#ffffff", size = 3.4, fontface = "bold", 
               nudge_x = 0.14, nudge_y = 0.05, check_overlap = TRUE) +
  scale_size_area(name = "Bomb Weight (Tons)", max_size = 11,
                  breaks = c(1, 5, 10, 20, 50),
                  labels = c("1 t", "5 t", "10 t", "20 t", "50 t")) +
  scale_color_viridis_c(name = "Bomb Weight (Tons)", option = "magma",
                        breaks = c(1, 5, 10, 20, 50),
                        labels = c("1 t", "5 t", "10 t", "20 t", "50 t")) +
  coord_sf(xlim = c(8.0, 11.5), ylim = c(33.0, 36.0), expand = FALSE) +
  annotation_scale(location = "bl", width_hint = 0.25, style = "ticks",
                   text_col = "#94a3b8", line_col = "#94a3b8") +
  labs(
    title = "Central & Southern Tunisia: Kasserine Pass & Mareth Line Strikes",
    subtitle = "Tactical strikes supporting ground offensives against Rommel's forces, supply lines at Sfax & Gabès\nOverlay on Sector / Imada boundaries",
    caption = "Source: USAF WWII THOR Database"
  ) +
  theme_void() +
  theme(
    plot.background = element_rect(fill = "#0f172a", color = NA),
    panel.background = element_rect(fill = "#0f172a", color = NA),
    plot.title = element_text(color = "#38bdf8", size = 14, face = "bold", margin = margin(t = 12, b = 4, l = 16)),
    plot.subtitle = element_text(color = "#cbd5e1", size = 9.5, margin = margin(b = 10, l = 16)),
    plot.caption = element_text(color = "#64748b", size = 8, margin = margin(t = 8, b = 8, r = 16), hjust = 1),
    legend.position = "right",
    legend.background = element_rect(fill = "#1e293b", color = "#334155"),
    legend.title = element_text(color = "#f8fafc", size = 9, face = "bold"),
    legend.text = element_text(color = "#cbd5e1", size = 8),
    legend.box.margin = margin(r = 16),
    legend.margin = margin(8, 12, 8, 12)
  ) +
  guides(
    size = guide_legend(override.aes = list(alpha = 0.85, color = "#fbbf24")),
    color = "none"
  )

south_png <- file.path(gis_dir, "tunisia_bombing_south_central.png")
ggsave(south_png, p_south, width = 10, height = 8.5, dpi = 300)
cat(sprintf("Saved south-central focus map: %s\n", south_png))

# ==============================================================================
# 5. INTERACTIVE LEAFLET MAP WITH IMADA POLYGONS & INDIVIDUAL BOMBS
# ==============================================================================
cat("\nGenerating Interactive Leaflet HTML Map with Imadas & Individual Bombs...\n")

# Simplify imada geometries slightly for super-smooth web rendering
imadas_web <- st_simplify(imadas, preserveTopology = TRUE, dTolerance = 0.001)

# Format bomb properties for interactive popups
bombs_web <- bombs_df %>%
  mutate(
    radius = pmax(3, pmin(28, sqrt(total_tons_clean) * 2.8)),
    popup_txt = paste0(
      "<div style='font-family:sans-serif;font-size:12px;line-height:1.4;'>",
      "<b style='font-size:13px;color:#0284c7;'>", ifelse(is.na(TGT_LOCATION) | TGT_LOCATION == "", "Tunisia Target", TGT_LOCATION), "</b><br>",
      "<b>Date:</b> ", mission_date_iso, "<br>",
      "<b>Bomb Weight:</b> <span style='color:#ea580c;font-weight:bold;'>", round(total_tons_clean, 2), " tons</span><br>",
      "<b>HE Munitions:</b> ", round(TONS_OF_HE, 2), " t | <b>Frag:</b> ", round(TONS_OF_FRAG, 2), " t<br>",
      "<b>Aircraft:</b> ", ifelse(is.na(aircraft_full_name), "Unknown", aircraft_full_name), "<br>",
      "<b>Air Force / Nation:</b> ", ifelse(is.na(country_flying_mission_clean), "Unknown", country_flying_mission_clean),
      " (", ifelse(is.na(NAF), "air force not recorded", NAF), ")<br>",
      "<b>THOR record ID:</b> ", WWII_ID,
      "</div>"
    )
  )

# Calculate bomb count and tonnage per imada polygon for polygon hover/popup
bombs_in_imadas <- st_join(bombs_sf, imadas)
imada_stats <- bombs_in_imadas %>%
  st_drop_geometry() %>%
  filter(!is.na(sec_uid)) %>%
  group_by(sec_uid) %>%
  summarise(
    total_bombs = n(),
    tons_dropped = sum(total_tons_clean),
    .groups = "drop"
  )

imadas_web <- imadas_web %>%
  left_join(imada_stats, by = "sec_uid") %>%
  mutate(
    total_bombs = ifelse(is.na(total_bombs), 0, total_bombs),
    tons_dropped = ifelse(is.na(tons_dropped), 0, round(tons_dropped, 1)),
    poly_label = paste0(
      "<b>Imada (عمادة):</b> ", sec_en, " (", sec_ar, ")<br>",
      "<b>Delegation (معتمدية):</b> ", dl_n_2018, "<br>",
      "<b>Governorate (ولاية):</b> ", gov_en, "<br>",
      "<b>Bombs Dropped Inside:</b> ", total_bombs, "<br>",
      "<b>Total Tonnage:</b> ", tons_dropped, " tons"
    )
  )

m <- leaflet() %>%
  setView(lng = 9.8, lat = 35.2, zoom = 7) %>%
  addProviderTiles("CartoDB.DarkMatter", group = "Dark Matter (Default)") %>%
  addProviderTiles("OpenStreetMap", group = "OpenStreetMap") %>%
  addProviderTiles("Esri.WorldImagery", group = "Satellite") %>%
  # Imada level boundary layer
  addPolygons(
    data = imadas_web,
    group = "Imada Boundaries (عمادات)",
    fillColor = ~ifelse(total_bombs > 0, "#f97316", "#1e293b"),
    fillOpacity = ~ifelse(total_bombs > 0, 0.35, 0.08),
    color = "#38bdf8",
    weight = 0.6,
    opacity = 0.5,
    highlightOptions = highlightOptions(
      weight = 2,
      color = "#ffffff",
      fillOpacity = 0.5,
      bringToFront = FALSE
    ),
    popup = ~poly_label
  ) %>%
  # Governorate outlines
  addPolylines(
    data = govs,
    group = "Governorate Borders (ولايات)",
    color = "#93c5fd",
    weight = 1.8,
    opacity = 0.8
  ) %>%
  # Individual bomb markers proportional to weight
  addCircleMarkers(
    data = bombs_web,
    lng = ~target_lon,
    lat = ~target_lat,
    group = "Individual Bomb Strikes",
    radius = ~radius,
    fillColor = "#ef4444",
    fillOpacity = 0.65,
    color = "#fef08a",
    weight = 0.8,
    popup = ~popup_txt
  ) %>%
  addLayersControl(
    baseGroups = c("Dark Matter (Default)", "OpenStreetMap", "Satellite"),
    overlayGroups = c("Individual Bomb Strikes", "Imada Boundaries (عمادات)", "Governorate Borders (ولايات)"),
    options = layersControlOptions(collapsed = FALSE)
  )

html_out <- file.path(docs_dir, "tunisia_bombing_imadas_interactive.html")
saveWidget(m, file = html_out, selfcontained = TRUE)
cat(sprintf("Saved interactive Leaflet map: %s\n", html_out))

cat("\nALL TUNISIA MAPS PRODUCED SUCCESSFULLY!\n")

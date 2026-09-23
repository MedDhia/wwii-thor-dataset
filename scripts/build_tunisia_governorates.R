#!/usr/bin/env Rscript
# scripts/build_tunisia_governorates.R
# Dissolves the 2,084 Imada (sector) polygons in TN_sectors.shp into the 24
# governorates (gov_id / gov_en / gov_ar) and writes TN_governorates.shp.
# TN_municipalities.shp (350 municipalities) is a separate, finer layer.

suppressPackageStartupMessages({
  library(sf)
  library(dplyr)
})

script_arg <- grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE)
base_dir <- if (length(script_arg)) normalizePath(file.path(dirname(sub("^--file=", "", script_arg)), "..")) else getwd()
shp_dir <- file.path(base_dir, "data", "gis", "tunisia_imadas")

sf_use_s2(FALSE)
sectors <- st_read(file.path(shp_dir, "TN_sectors.shp"), quiet = TRUE)
govs <- sectors %>%
  st_make_valid() %>%
  group_by(gov_id, gov_en, gov_ar, reg, reg_en, reg_ar) %>%
  summarise(km2 = sum(km2), n_imadas = n(), .groups = "drop") %>%
  arrange(gov_id)

out <- file.path(shp_dir, "TN_governorates.shp")
st_write(govs, out, delete_dsn = file.exists(out), quiet = TRUE, layer_options = "ENCODING=UTF-8")
cat(sprintf("Saved %d governorates to %s\n", nrow(govs), out))

#!/usr/bin/env Rscript

options(stringsAsFactors = FALSE)

local_lib <- file.path("analysis_r", "Rlib")
if (dir.exists(local_lib)) .libPaths(c(normalizePath(local_lib), .libPaths()))

data_root <- Sys.getenv("ANCHOVETA_DATA_ROOT", unset = "../data_treatment")
raw_dir <- file.path("analysis_r", "data", "raw")
dir.create(raw_dir, recursive = TRUE, showWarnings = FALSE)

if (!requireNamespace("ramlegacy", quietly = TRUE)) {
  stop("Falta ramlegacy. Ejecuta primero analysis_r/00_install_packages.R")
}

ram_dir <- file.path(raw_dir, "ramlegacy")
dir.create(ram_dir, recursive = TRUE, showWarnings = FALSE)
rds_path <- file.path(
  ram_dir, "4.44", "RLSADB v4.44", "DB Files With Assessment Data", "v4.44.rds"
)

# La versión queda fijada deliberadamente. No usar el valor por defecto en
# publicaciones, porque el paquete puede cambiar qué considera latest.
if (!file.exists(rds_path)) {
  ramlegacy::download_ramlegacy(
    version = "4.44",
    ram_path = ram_dir,
    overwrite = FALSE,
    quiet = FALSE
  )
} else {
  message("RAM Legacy v4.44 ya está cacheado: ", rds_path)
}

# El archivo local de NSIDC ya está versionado en data_treatment. Se copia a
# la carpeta del análisis para que el panel sea portable y no dependa de una
# ruta externa.
nsidc_source <- file.path(data_root, "data/raw/nsidc/S_seaice_extent_daily_v4.0.csv")
nsidc_target <- file.path(raw_dir, "S_seaice_extent_daily_v4.0.csv")
if (file.exists(nsidc_source) && !file.exists(nsidc_target)) {
  file.copy(nsidc_source, nsidc_target, overwrite = FALSE)
}

# NOAA PSL publica el índice AAO/SAM mensual. El endpoint se puede sustituir
# con SAM_URL si NOAA cambia su ruta; no se rellena la serie si falla.
sam_target <- file.path(raw_dir, "aao_cpc_monthly.csv")
sam_url <- Sys.getenv(
  "SAM_URL",
  unset = "https://www.cpc.ncep.noaa.gov/products/precip/CWlink/daily_ao_index/aao/monthly.aao.index.b79.current.ascii.table"
)
if (!file.exists(sam_target)) {
  tryCatch(
    utils::download.file(sam_url, sam_target, mode = "wb", quiet = FALSE),
    error = function(e) warning("No se descargó SAM/AAO: ", conditionMessage(e))
  )
}

manifest <- data.frame(
  dataset = c("RAM Legacy", "NSIDC G02135", "NOAA PSL AAO/SAM"),
  version = c("4.44", "v4.0", "CPC monthly"),
  path = c(ram_dir, nsidc_target, sam_target),
  available = file.exists(c(ram_dir, nsidc_target, sam_target)),
  stringsAsFactors = FALSE
)
utils::write.csv(manifest, file.path(raw_dir, "download_manifest.csv"), row.names = FALSE)
print(manifest)

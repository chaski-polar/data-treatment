#!/usr/bin/env Rscript

local_lib <- file.path("analysis_r", "Rlib")
dir.create(local_lib, recursive = TRUE, showWarnings = FALSE)
.libPaths(c(normalizePath(local_lib, mustWork = FALSE), .libPaths()))

required <- c("ramlegacy")
cran <- character()

missing <- required[!vapply(required, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing) == 0L) {
  message("Paquetes R requeridos ya están disponibles.")
  quit(save = "no", status = 0)
}

options(repos = c(CRAN = "https://cloud.r-project.org"))
cran_missing <- intersect(missing, cran)
if (length(cran_missing)) {
  install.packages(cran_missing, lib = local_lib, dependencies = TRUE)
}

if (!requireNamespace("ramlegacy", quietly = TRUE)) {
  if (!requireNamespace("remotes", quietly = TRUE)) {
    install.packages("remotes", lib = local_lib, dependencies = c("Depends", "Imports", "LinkingTo"))
  }
  remotes::install_github(
    "ropensci/ramlegacy",
    lib = local_lib,
    dependencies = c("Depends", "Imports", "LinkingTo"),
    upgrade = "never"
  )
}

missing_after <- required[!vapply(required, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing_after)) {
  stop("No se pudieron instalar: ", paste(missing_after, collapse = ", "))
}
message("Instalación completada.")

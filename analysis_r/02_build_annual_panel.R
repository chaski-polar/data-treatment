#!/usr/bin/env Rscript

options(stringsAsFactors = FALSE)

local_lib <- file.path("analysis_r", "Rlib")
if (dir.exists(local_lib)) .libPaths(c(normalizePath(local_lib), .libPaths()))

data_root <- Sys.getenv("ANCHOVETA_DATA_ROOT", unset = ".")
analysis_root <- file.path("analysis_r", "data")
raw_dir <- file.path(analysis_root, "raw")
out_dir <- file.path(analysis_root, "processed")
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

read_csv_safe <- function(path, ...) {
  if (!file.exists(path)) stop("No existe el archivo requerido: ", path)
  utils::read.csv(path, check.names = FALSE, ...)
}

find_col <- function(x, candidates) {
  hit <- candidates[candidates %in% names(x)]
  if (!length(hit)) return(NA_character_)
  hit[[1L]]
}

z <- function(x) {
  ok <- is.finite(x)
  if (sum(ok) < 2L || stats::sd(x[ok]) == 0) return(rep(NA_real_, length(x)))
  out <- rep(NA_real_, length(x))
  out[ok] <- as.numeric(scale(x[ok]))
  out
}

read_ram_tables <- function() {
  if (!requireNamespace("ramlegacy", quietly = TRUE)) {
    stop("Falta ramlegacy. Ejecuta 00_install_packages.R")
  }
  ram_path <- file.path(
    raw_dir, "ramlegacy", "4.44", "RLSADB v4.44",
    "DB Files With Assessment Data", "v4.44.rds"
  )
  ramlegacy::load_ramlegacy(version = "4.44", ram_path = ram_path, tables = NULL)
}

extract_ram_candidates <- function(ram) {
  stock <- ram$stock
  sci <- find_col(stock, c("scientificname", "scientific_name", "scientific"))
  if (is.na(sci)) stop("No se encontró la columna de nombre científico en RAM.")
  text <- apply(stock, 1, paste, collapse = " ")
  candidates <- stock[grepl("engraulis ringens", tolower(stock[[sci]]), fixed = TRUE), , drop = FALSE]
  if (!nrow(candidates)) {
    candidates <- stock[grepl("anchoveta|anchovy", tolower(text)), , drop = FALSE]
  }
  if (!nrow(candidates)) stop("RAM 4.44 no encontró Engraulis ringens/anchoveta.")
  candidates
}

choose_stock <- function(candidates) {
  id_col <- find_col(candidates, c("stockid", "stock_id", "stock", "id"))
  if (is.na(id_col)) stop("No se identificó stockid en la tabla stock de RAM.")

  requested <- Sys.getenv("RAM_STOCK_ID", unset = "")
  if (nzchar(requested) && requested %in% as.character(candidates[[id_col]])) {
    return(list(id_col = id_col, stock_id = requested, method = "RAM_STOCK_ID"))
  }

  text <- tolower(apply(candidates, 1, paste, collapse = " "))
  area_col <- find_col(candidates, c("areaid", "area_id"))
  preferred <- if (!is.na(area_col)) grepl("peru-imarpe-nc", tolower(candidates[[area_col]]), fixed = TRUE) else rep(FALSE, nrow(candidates))
  if (sum(preferred) == 1L) {
    selected <- candidates[preferred, , drop = FALSE]
    return(list(id_col = id_col, stock_id = as.character(selected[[id_col]][[1L]]), method = "areaid_peru_imarpe_nc"))
  }
  score <- grepl("north-central peru|peru|humboldt|pacific", text)
  selected <- candidates[score, , drop = FALSE]
  if (nrow(selected) != 1L) {
    stop(
      "Hay ", nrow(candidates), " candidatos de Engraulis ringens y no se puede elegir uno de forma segura. ",
      "Revisa ram_engraulis_candidates.csv y define RAM_STOCK_ID."
    )
  }
  list(id_col = id_col, stock_id = as.character(selected[[id_col]][[1L]]), method = "heuristic_single")
}

extract_series <- function(ram, table_name, stock_id, stock_id_col) {
  x <- if (table_name %in% names(ram)) ram[[table_name]] else NULL
  if (is.null(x) && "most.used.time.series" %in% names(ram)) {
    x <- ram[["most.used.time.series"]][[table_name]]
  }
  if (is.null(x)) return(NULL)

  # En RAM 4.44 las series más usadas son matrices anuales anchas: filas =
  # años y columnas = stockid. La versión larga se conserva como alternativa
  # para otras ediciones.
  if (!is.null(dim(x)) && stock_id %in% colnames(x) && !is.null(rownames(x))) {
    values <- as.numeric(x[, stock_id])
    years <- suppressWarnings(as.integer(rownames(x)))
    return(data.frame(
      year = years,
      value = values,
      value_column = stock_id,
      source_table = table_name,
      stringsAsFactors = FALSE
    ))
  }
  id_col <- find_col(x, c(stock_id_col, "stockid", "stock_id", "stock"))
  year_col <- find_col(x, c("year", "yr", "assessment_year"))
  if (is.na(id_col) || is.na(year_col)) return(NULL)
  x <- x[as.character(x[[id_col]]) == as.character(stock_id), , drop = FALSE]
  if (!nrow(x)) return(NULL)
  numeric_cols <- names(x)[vapply(x, is.numeric, logical(1))]
  numeric_cols <- setdiff(numeric_cols, c(id_col, year_col))
  if (!length(numeric_cols)) return(NULL)
  value_col <- numeric_cols[[1L]]
  data.frame(
    year = as.integer(x[[year_col]]),
    value = as.numeric(x[[value_col]]),
    value_column = value_col,
    source_table = table_name,
    stringsAsFactors = FALSE
  )
}

build_response <- function(ram, candidates) {
  utils::write.csv(candidates, file.path(out_dir, "ram_engraulis_candidates.csv"), row.names = FALSE)
  choice <- choose_stock(candidates)

  series <- NULL
  for (table_name in c("tb.data", "ssb.data", "tbbest.data")) {
    series <- extract_series(ram, table_name, choice$stock_id, choice$id_col)
    if (!is.null(series)) break
  }
  if (is.null(series)) stop("No se encontró una serie TB/SSB usable para el stock seleccionado.")
  series$stock_id <- choice$stock_id
  series$selection_method <- choice$method
  series$log_biomass <- ifelse(series$value > 0, log10(series$value), NA_real_)
  series <- series[is.finite(series$log_biomass), , drop = FALSE]
  if (anyDuplicated(series$year)) stop("La serie RAM seleccionada tiene años duplicados.")
  series
}

read_local_environment <- function() {
  # monitoring_series_ab contiene el mismo entorno mensual extraído de CMEMS
  # pero conserva ICEN, Niño 1+2 y PDO; no se usa su biomasa interpolada.
  path <- file.path(data_root, "data/processed/tables/monitoring_series_ab.csv")
  x <- read_csv_safe(path)
  x$date <- as.Date(x$date)
  x$year <- as.integer(format(x$date, "%Y"))
  needed <- c("sst", "sss", "oxygen", "chlorophyll_a", "nitrate", "pdo", "icen", "nino12")
  for (nm in needed) if (!nm %in% names(x)) x[[nm]] <- NA_real_
  result <- aggregate(x[needed], by = list(year = x$year), FUN = function(v) mean(v, na.rm = TRUE))
  result[] <- lapply(result, function(v) { v[is.nan(v)] <- NA_real_; v })
  result
}

read_antarctic_ice <- function() {
  path <- file.path(raw_dir, "S_seaice_extent_daily_v4.0.csv")
  if (!file.exists(path)) return(data.frame(year = integer(), extent_million_km2 = numeric()))
  x <- utils::read.csv(path, skip = 1, check.names = FALSE)
  names(x)[1:4] <- c("year", "month", "day", "extent_million_km2")
  x$year <- suppressWarnings(as.integer(x$year))
  x$extent_million_km2 <- suppressWarnings(as.numeric(x$extent_million_km2))
  x <- x[is.finite(x$year) & is.finite(x$extent_million_km2), , drop = FALSE]
  aggregate(x["extent_million_km2"], by = list(year = x$year), FUN = mean)
}

read_sam <- function() {
  path <- file.path(raw_dir, "aao_cpc_monthly.csv")
  if (!file.exists(path)) return(data.frame(year = integer(), sam = numeric()))
  lines <- readLines(path, warn = FALSE)
  year_lines <- lines[grepl("^\\s*[0-9]{4}\\s", lines)]
  if (length(year_lines)) {
    wide <- utils::read.table(text = paste(year_lines, collapse = "\n"), header = FALSE, fill = TRUE)
    years <- as.integer(wide[[1L]])
    monthly <- as.data.frame(wide[, 2:min(13L, ncol(wide)), drop = FALSE])
    monthly[] <- lapply(monthly, as.numeric)
    out <- data.frame(year = years, sam = rowMeans(monthly, na.rm = TRUE))
    out$sam[is.nan(out$sam)] <- NA_real_
    return(out)
  }
  lines <- lines[!grepl("^#|^$", trimws(lines))]
  tmp <- tryCatch(read.csv(text = paste(lines, collapse = "\n"), header = TRUE), error = function(e) NULL)
  if (is.null(tmp) || ncol(tmp) < 2L) return(data.frame(year = integer(), sam = numeric()))
  year_col <- find_col(tmp, c("year", "Year", "date"))
  if (is.na(year_col)) return(data.frame(year = integer(), sam = numeric()))
  value_col <- setdiff(names(tmp), year_col)[[1L]]
  if (year_col == "date") tmp$year <- as.integer(substr(tmp[[year_col]], 1, 4))
  year_values <- if (year_col == "date") tmp$year else tmp[[year_col]]
  out <- data.frame(year = as.integer(year_values), sam = as.numeric(tmp[[value_col]]))
  aggregate(out["sam"], by = list(year = out$year), FUN = mean, na.rm = TRUE)
}

ram <- read_ram_tables()
candidates <- extract_ram_candidates(ram)
response <- build_response(ram, candidates)
local <- read_local_environment()
ice <- read_antarctic_ice()
sam <- read_sam()

panel <- merge(response, local, by = "year", all = FALSE)
panel <- merge(panel, ice, by = "year", all.x = TRUE)
panel <- merge(panel, sam, by = "year", all.x = TRUE)
panel <- panel[panel$year >= 1998 & panel$year <= 2024, , drop = FALSE]
panel <- panel[order(panel$year), , drop = FALSE]

# Las variables se estandarizan solo después de construir el periodo común.
# El hielo se expresa como anomalía anual; no se interpreta el nivel absoluto
# como causalidad.
for (nm in c("sst", "sss", "oxygen", "chlorophyll_a", "nitrate", "pdo", "icen", "nino12", "extent_million_km2", "sam")) {
  if (nm %in% names(panel)) panel[[paste0(nm, "_z")]] <- z(panel[[nm]])
}
panel$year_z <- z(panel$year)
panel$year_index <- seq_len(nrow(panel))
panel$ice_antarctic_lag1 <- c(NA_real_, head(panel$extent_million_km2_z, -1L))
panel$sam_lag1 <- c(NA_real_, head(panel$sam_z, -1L))

utils::write.csv(panel, file.path(out_dir, "annual_panel_ram44.csv"), row.names = FALSE)
metadata <- data.frame(
  ram_version = "4.44",
  response_table = paste(unique(response$source_table), collapse = ";"),
  stock_id = paste(unique(response$stock_id), collapse = ";"),
  n_response = nrow(response),
  n_common_period = nrow(panel),
  sam_available = any(is.finite(panel$sam)),
  ice_available = any(is.finite(panel$extent_million_km2)),
  stringsAsFactors = FALSE
)
utils::write.csv(metadata, file.path(out_dir, "annual_panel_metadata.csv"), row.names = FALSE)
print(metadata)

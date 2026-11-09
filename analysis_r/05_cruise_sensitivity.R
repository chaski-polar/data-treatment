#!/usr/bin/env Rscript

# Sensibilidad de los modelos A y B de cruceros:
#   1. ampliar de 9 a 12 cruceros "toda_costa" usando fechas aproximadas
#      (data/biomasa_cruceros_fechas_aproximadas.csv);
#   2. repetir los ajustes sin el crucero 9808-09 (1998), que es atipico
#      (1.2 millones de t frente a 7-12 millones del resto).
# El modelo C no se incluye porque el panel de conectividad no esta versionado.
# Los predictores se promedian por intervalo de crucero con la misma regla
# ponderada por dias que scripts/04_build_real_panel.py.

options(stringsAsFactors = FALSE)

parse_option <- function(args, name, default) {
  hit <- which(args == name)
  if (!length(hit) || hit[[1L]] == length(args)) return(default)
  args[[hit[[1L]] + 1L]]
}

cli_args <- commandArgs(trailingOnly = TRUE)
out_dir <- parse_option(cli_args, "--out-dir", file.path("analysis_r", "data", "sensitivity"))
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

env <- utils::read.csv(file.path("data", "entorno_mensual_1998_2026.csv"))
env$date <- as.Date(env$date)

cruises <- utils::read.csv(file.path("data", "biomasa_cruceros.csv"))
cruises <- cruises[cruises$stock == "toda_costa" & nzchar(cruises$fecha_inicio) & nzchar(cruises$fecha_fin), ]
cruises$fecha_aproximada <- FALSE
approx <- utils::read.csv(file.path("data", "biomasa_cruceros_fechas_aproximadas.csv"))
approx$fecha_aproximada <- as.logical(approx$fecha_aproximada)
keep <- c("crucero", "anio", "fecha_inicio", "fecha_fin", "biomasa_t", "fecha_aproximada")
cruises <- rbind(cruises[, keep], approx[, keep])
cruises$fecha_inicio <- as.Date(cruises$fecha_inicio)
cruises$fecha_fin <- as.Date(cruises$fecha_fin)
if (anyDuplicated(cruises$crucero)) stop("Codigos de crucero duplicados")

month_start <- function(d) as.Date(format(d, "%Y-%m-01"))
month_end <- function(m) seq(m, by = "month", length.out = 2L)[2L] - 1L

weighted_interval_mean <- function(start, end, columns) {
  months <- seq(month_start(start), month_start(end), by = "month")
  weights <- vapply(months, function(m) {
    max(0, as.numeric(min(end, month_end(m)) - max(start, m)) + 1)
  }, numeric(1))
  rows <- env[match(months, env$date), columns, drop = FALSE]
  vapply(columns, function(column) {
    values <- rows[[column]]
    ok <- is.finite(values) & weights > 0
    if (!any(ok)) return(NA_real_)
    sum(values[ok] * weights[ok]) / sum(weights[ok])
  }, numeric(1))
}

predictors <- c(ab_sst = "sst_c", ab_nino12 = "nino12_anom_c", ab_chlorophyll_a = "chlorophyll_a_mg_m3")
means <- t(vapply(seq_len(nrow(cruises)), function(i) {
  weighted_interval_mean(cruises$fecha_inicio[i], cruises$fecha_fin[i], unname(predictors))
}, numeric(length(predictors))))
colnames(means) <- names(predictors)
panel <- cbind(cruises, means)
panel$log10_biomass <- log10(panel$biomasa_t)
panel <- panel[order(panel$fecha_inicio), ]

z <- function(x) as.numeric(scale(x))

loocv_rmse <- function(formula, data) {
  errors <- vapply(seq_len(nrow(data)), function(i) {
    fit <- stats::lm(formula, data = data[-i, , drop = FALSE])
    data$log10_biomass[i] - stats::predict(fit, newdata = data[i, , drop = FALSE])
  }, numeric(1))
  sqrt(mean(errors^2))
}

fit_variant <- function(name, data) {
  data$sst_z <- z(data$ab_sst)
  data$nino12_z <- z(data$ab_nino12)
  data$chl_z <- z(data$ab_chlorophyll_a)
  formulas <- list(
    A_local = log10_biomass ~ sst_z + nino12_z,
    B_productivity = log10_biomass ~ sst_z + nino12_z + chl_z
  )
  do.call(rbind, lapply(names(formulas), function(model) {
    fit <- stats::lm(formulas[[model]], data = data)
    s <- summary(fit)
    nino <- s$coefficients["nino12_z", ]
    data.frame(
      variant = name,
      model = model,
      n = stats::nobs(fit),
      r2 = s$r.squared,
      adj_r2 = s$adj.r.squared,
      loocv_rmse = loocv_rmse(formulas[[model]], data),
      nino12_estimate = nino[["Estimate"]],
      nino12_p = nino[["Pr(>|t|)"]]
    )
  }))
}

original <- panel[!panel$fecha_aproximada, ]
variants <- list(
  "9_cruceros_original" = original,
  "8_cruceros_sin_1998" = original[original$crucero != "9808-09", ],
  "12_cruceros_ampliado" = panel,
  "11_cruceros_ampliado_sin_1998" = panel[panel$crucero != "9808-09", ],
  "11_cruceros_ampliado_sin_2102-07" = panel[panel$crucero != "2102-07", ]
)
results <- do.call(rbind, lapply(names(variants), function(name) fit_variant(name, variants[[name]])))

# Control: la variante original debe reproducir analysis_r/data/exploratory_nointerp.
reference <- utils::read.csv(file.path("analysis_r", "data", "exploratory_nointerp", "cruise_model_metrics.csv"))
check <- merge(results[results$variant == "9_cruceros_original", c("model", "r2")], reference[, c("model", "r2")], by = "model")
if (any(abs(check$r2.x - check$r2.y) > 1e-6)) stop("La variante original no reproduce las metricas del analisis exploratorio")

utils::write.csv(panel, file.path(out_dir, "cruise_panel_sensitivity.csv"), row.names = FALSE)
utils::write.csv(results, file.path(out_dir, "cruise_sensitivity_metrics.csv"), row.names = FALSE)

fmt <- function(x, d = 3) formatC(x, format = "f", digits = d)
table_lines <- vapply(seq_len(nrow(results)), function(i) {
  r <- results[i, ]
  paste0("| ", r$variant, " | ", r$model, " | ", r$n, " | ", fmt(r$r2), " | ", fmt(r$adj_r2), " | ",
         fmt(r$loocv_rmse), " | ", fmt(r$nino12_estimate), " | ", fmt(r$nino12_p), " |")
}, character(1))
report <- c(
  "# Sensibilidad de los modelos de cruceros",
  "",
  "Generado por `analysis_r/05_cruise_sensitivity.R`.",
  "",
  "- La variante `9_cruceros_original` reproduce las metricas de `analysis_r/data/exploratory_nointerp/`.",
  "- Las variantes ampliadas suman 2102-07, 2202-04 y 2209-11 con fechas aproximadas (dia 15 de cada mes del codigo).",
  "- 2102-07 abarca de febrero a julio; su promedio ambiental es menos representativo, por eso se incluye una variante sin ese crucero.",
  "- El modelo C no se incluye porque el panel de conectividad no esta versionado.",
  "",
  "| Variante | Modelo | n | R2 | R2 ajustado | RMSE LOOCV | Coef. Nino 1+2 | p Nino 1+2 |",
  "|---|---|---:|---:|---:|---:|---:|---:|",
  table_lines,
  "",
  "Son asociaciones exploratorias con muestras muy pequenas; no prueban causalidad."
)
writeLines(report, file.path(out_dir, "cruise_sensitivity_report.md"))
print(results, digits = 3)

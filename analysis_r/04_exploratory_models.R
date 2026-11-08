#!/usr/bin/env Rscript

options(stringsAsFactors = FALSE)

local_lib <- file.path("analysis_r", "Rlib")
if (dir.exists(local_lib)) .libPaths(c(normalizePath(local_lib), .libPaths()))

parse_option <- function(args, name, default) {
  hit <- which(args == name)
  if (!length(hit) || hit[[1L]] == length(args)) return(default)
  args[[hit[[1L]] + 1L]]
}

cli_args <- commandArgs(trailingOnly = TRUE)
tables <- parse_option(cli_args, "--tables", file.path("data", "processed", "tables"))
out_dir <- parse_option(cli_args, "--out-dir", file.path("analysis_r", "data", "exploratory"))
panel_file <- parse_option(cli_args, "--panel", file.path(tables, "exploratory_cruise_panel.csv"))
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

read_required <- function(path) {
  if (!file.exists(path)) stop("No existe: ", path)
  utils::read.csv(path, check.names = FALSE)
}

z <- function(x) {
  if (!is.numeric(x)) x <- as.numeric(x)
  if (sum(is.finite(x)) < 3L || stats::sd(x, na.rm = TRUE) == 0) return(rep(NA_real_, length(x)))
  as.numeric(scale(x))
}

safe_lm <- function(formula, data) {
  tryCatch(stats::lm(formula, data = data), error = function(e) NULL)
}

loocv_rmse <- function(formula, data) {
  n <- nrow(data)
  if (n < 5L) return(NA_real_)
  errors <- rep(NA_real_, n)
  for (i in seq_len(n)) {
    train <- data[-i, , drop = FALSE]
    test <- data[i, , drop = FALSE]
    fit <- safe_lm(formula, train)
    if (!is.null(fit)) errors[i] <- test$log10_biomass - stats::predict(fit, newdata = test)
  }
  if (!any(is.finite(errors))) return(NA_real_)
  sqrt(mean(errors[is.finite(errors)]^2))
}

bootstrap_ci <- function(formula, data, term, B = 2000L, seed = 360L) {
  set.seed(seed)
  n <- nrow(data)
  estimates <- rep(NA_real_, B)
  for (b in seq_len(B)) {
    sample_rows <- sample(seq_len(n), n, replace = TRUE)
    fit <- safe_lm(formula, data[sample_rows, , drop = FALSE])
    if (!is.null(fit) && term %in% names(stats::coef(fit))) estimates[b] <- stats::coef(fit)[[term]]
  }
  estimates <- estimates[is.finite(estimates)]
  if (length(estimates) < 100L) return(c(low = NA_real_, high = NA_real_, n_boot = length(estimates)))
  c(low = unname(stats::quantile(estimates, 0.025)), high = unname(stats::quantile(estimates, 0.975)), n_boot = length(estimates))
}

panel <- read_required(panel_file)
panel$fecha_inicio <- as.Date(panel$fecha_inicio)
panel$fecha_fin <- as.Date(panel$fecha_fin)
panel$fecha_centro <- as.Date(panel$fecha_centro)
panel$log10_biomass <- as.numeric(panel$log10_biomass)

# One pre-specified variable per conceptual block keeps the nine-cruise model
# estimable enough for exploration. Additional predictors are sensitivity only.
panel$sst_z <- z(panel$ab_sst)
panel$oxygen_z <- z(panel$ab_oxygen)
panel$nino12_z <- z(panel$ab_nino12)
panel$chl_z <- z(panel$ab_chlorophyll_a)
panel$phyc_z <- z(panel$ab_phytoplankton_carbon)
panel$connectivity_z <- z(panel$center_connectivity_index_100_200_lag0)

# Primary cumulative specifications. A/B/C are nested and intentionally small.
fA <- log10_biomass ~ sst_z + nino12_z
fB <- log10_biomass ~ sst_z + nino12_z + chl_z
fC <- log10_biomass ~ sst_z + nino12_z + chl_z + connectivity_z
fits <- list(A_local = safe_lm(fA, panel), B_productivity = safe_lm(fB, panel), C_connectivity = safe_lm(fC, panel))
formulas <- list(A_local = fA, B_productivity = fB, C_connectivity = fC)

metrics <- do.call(rbind, lapply(names(fits), function(name) {
  fit <- fits[[name]]
  if (is.null(fit)) return(data.frame(model = name, n = NA, r2 = NA, adj_r2 = NA, AIC = NA, loocv_rmse = NA))
  data.frame(
    model = name,
    n = stats::nobs(fit),
    r2 = summary(fit)$r.squared,
    adj_r2 = summary(fit)$adj.r.squared,
    AIC = stats::AIC(fit),
    loocv_rmse = loocv_rmse(formulas[[name]], panel)
  )
}))

coefs <- do.call(rbind, lapply(names(fits), function(name) {
  fit <- fits[[name]]
  if (is.null(fit)) return(NULL)
  out <- as.data.frame(summary(fit)$coefficients)
  names(out) <- c("estimate", "std_error", "t_value", "p_value")
  out$term <- rownames(out)
  out$model <- name
  ci <- t(vapply(out$term, function(term) bootstrap_ci(formulas[[name]], panel, term), numeric(3)))
  out$bootstrap_low <- ci[, "low"]
  out$bootstrap_high <- ci[, "high"]
  out$n_boot <- ci[, "n_boot"]
  rownames(out) <- NULL
  out[, c("model", "term", "estimate", "std_error", "t_value", "p_value", "bootstrap_low", "bootstrap_high", "n_boot")]
}))

# Exploratory lag association table. It is descriptive and not a multiple-lag
# confirmatory test; p-values are FDR-adjusted within the tested lag family.
lag_names <- grep("^center_connectivity_index_100_200_lag(0|3|6|12|18|24)$", names(panel), value = TRUE)
lag_rows <- list()
if (length(lag_names)) {
  for (column in lag_names) {
    x <- panel[[column]]
    ok <- is.finite(x) & is.finite(panel$log10_biomass)
    if (sum(ok) >= 5L) {
      test <- suppressWarnings(stats::cor.test(x[ok], panel$log10_biomass[ok], method = "spearman", exact = FALSE))
      lag_rows[[length(lag_rows) + 1L]] <- data.frame(variable = column, n = sum(ok), rho = unname(test$estimate), p_value = test$p.value)
    }
  }
}
lag_results <- if (length(lag_rows)) do.call(rbind, lag_rows) else data.frame(variable = character(), n = integer(), rho = numeric(), p_value = numeric())
if (nrow(lag_results)) lag_results$p_fdr <- stats::p.adjust(lag_results$p_value, method = "BH")

write.csv(panel, file.path(out_dir, "exploratory_cruise_panel_used.csv"), row.names = FALSE)
write.csv(metrics, file.path(out_dir, "cruise_model_metrics.csv"), row.names = FALSE)
write.csv(coefs, file.path(out_dir, "cruise_model_coefficients.csv"), row.names = FALSE)
write.csv(lag_results, file.path(out_dir, "cruise_connectivity_lag_correlations.csv"), row.names = FALSE)

# Corrected annual RAM analysis: both nested models use the same covariance
# specification. The primary comparison is GLS without correlation; AR(1) is
# attempted symmetrically as a sensitivity analysis.
annual <- read_required(file.path("analysis_r", "data", "processed", "annual_panel_ram44.csv"))
required <- c("log_biomass", "sst_z", "chlorophyll_a_z", "oxygen_z", "nino12_z", "pdo_z", "year_z", "ice_antarctic_lag1", "sam_lag1")
annual <- annual[stats::complete.cases(annual[, required]), , drop = FALSE]
f0_ram <- stats::as.formula("log_biomass ~ sst_z + chlorophyll_a_z + oxygen_z + nino12_z + pdo_z + year_z")
f1_ram <- stats::as.formula("log_biomass ~ sst_z + chlorophyll_a_z + oxygen_z + nino12_z + pdo_z + year_z + ice_antarctic_lag1 + sam_lag1")

ram_summary <- data.frame()
ram_lrt <- data.frame()
if (nrow(annual) >= 15L && requireNamespace("nlme", quietly = TRUE)) {
  m0_iid <- nlme::gls(f0_ram, data = annual, method = "ML")
  m1_iid <- nlme::gls(f1_ram, data = annual, method = "ML")
  iid_anova <- as.data.frame(stats::anova(m0_iid, m1_iid))
  iid_anova$comparison_type <- "GLS_ML_same_IID_covariance"
  ram_lrt <- iid_anova
  ram_summary <- data.frame(
    model = c("M0_local_iid", "M1_plus_antarctic_iid"),
    n = c(stats::nobs(m0_iid), stats::nobs(m1_iid)),
    AIC = c(stats::AIC(m0_iid), stats::AIC(m1_iid)),
    logLik = c(as.numeric(stats::logLik(m0_iid)), as.numeric(stats::logLik(m1_iid)))
  )
  try({
    m0_ar1 <- nlme::gls(f0_ram, data = annual, correlation = nlme::corAR1(form = ~ year), method = "ML")
    m1_ar1 <- nlme::gls(f1_ram, data = annual, correlation = nlme::corAR1(form = ~ year), method = "ML")
    ar1_anova <- as.data.frame(stats::anova(m0_ar1, m1_ar1))
    ar1_anova$comparison_type <- "GLS_ML_same_AR1_covariance"
    ram_lrt <- rbind(ram_lrt, ar1_anova)
    ram_summary <- rbind(ram_summary, data.frame(
      model = c("M0_local_AR1", "M1_plus_antarctic_AR1"),
      n = c(stats::nobs(m0_ar1), stats::nobs(m1_ar1)),
      AIC = c(stats::AIC(m0_ar1), stats::AIC(m1_ar1)),
      logLik = c(as.numeric(stats::logLik(m0_ar1)), as.numeric(stats::logLik(m1_ar1)))
    ))
  }, silent = TRUE)
}
write.csv(ram_summary, file.path(out_dir, "ram_model_metrics_corrected.csv"), row.names = FALSE)
write.csv(ram_lrt, file.path(out_dir, "ram_block_lrt_corrected.csv"), row.names = FALSE)

decision <- data.frame(
  scope = c("cruise_panel", "annual_RAM"),
  conclusion = c(
    "Exploratory only: nine observed cruises; no confirmatory rejection is defensible.",
    if (nrow(ram_lrt)) "Use the same-covariance GLS comparison in ram_block_lrt_corrected.csv; the previous mixed-covariance LRT is superseded." else "Annual RAM model could not be refit."
  ),
  stringsAsFactors = FALSE
)
write.csv(decision, file.path(out_dir, "exploratory_decision_scope.csv"), row.names = FALSE)

report <- c(
  "# ANCHOVETA 360 — análisis exploratorio",
  "",
  paste0("Cruceros observados usados: ", nrow(panel)),
  "",
  if (grepl("nointerp", out_dir, fixed = TRUE)) {
    "La biomasa no fue interpolada. Los predictores regionales usan exclusivamente el valor mensual del mes central de cada campaña."
  } else {
    "La biomasa no fue interpolada. La interpolación lineal se aplicó únicamente a predictores ambientales en el punto medio de cada campaña."
  },
  "",
  "Los modelos A/B/C son deliberadamente parsimoniosos por el tamaño muestral. Sus métricas son exploratorias y no prueban causalidad ni transporte directo.",
  "",
  "El análisis RAM corregido compara M0 y M1 con la misma estructura de covarianza; reemplaza el LRT previo donde M0 y M1 tenían estructuras distintas.",
  "",
  "No se debe interpretar un p-valor aislado como evidencia de conectividad oceanográfica."
)
writeLines(report, file.path(out_dir, "exploratory_analysis_report.md"))
print(metrics)
print(ram_lrt)

#!/usr/bin/env Rscript

options(stringsAsFactors = FALSE)
out_dir <- file.path("analysis_r", "data", "processed")
panel_path <- file.path(out_dir, "annual_panel_ram44.csv")
if (!file.exists(panel_path)) stop("Falta el panel. Ejecuta 02_build_annual_panel.R")

x <- utils::read.csv(panel_path, check.names = FALSE)
required <- c("log_biomass", "sst_z", "chlorophyll_a_z", "oxygen_z", "nino12_z", "pdo_z", "year_z", "ice_antarctic_lag1")
missing <- setdiff(required, names(x))
if (length(missing)) stop("Faltan columnas para el modelo: ", paste(missing, collapse = ", "))

if (!"sam_lag1" %in% names(x) || !any(is.finite(x$sam_lag1))) {
  x$sam_lag1 <- NA_real_
  antarctic_terms <- "ice_antarctic_lag1"
} else {
  antarctic_terms <- "ice_antarctic_lag1 + sam_lag1"
}

base_terms <- "sst_z + chlorophyll_a_z + oxygen_z + nino12_z + pdo_z + year_z"
formula0 <- stats::as.formula(paste("log_biomass ~", base_terms))
formula1 <- stats::as.formula(paste("log_biomass ~", base_terms, "+", antarctic_terms))

complete <- stats::complete.cases(x[, unique(c(all.vars(formula0), all.vars(formula1), "year")), drop = FALSE])
dat <- x[complete, , drop = FALSE]
if (nrow(dat) < 15L) stop("Solo hay ", nrow(dat), " años completos; no es defendible ajustar este modelo.")
if (nrow(dat) <= length(attr(stats::terms(formula1), "term.labels")) + 3L) {
  stop("Muy pocas observaciones para el número de parámetros del modelo.")
}

fit_gls <- function(formula, data) {
  if (!requireNamespace("nlme", quietly = TRUE)) stop("nlme no está disponible")
  tryCatch(
    nlme::gls(
      formula,
      data = data,
      correlation = nlme::corCAR1(form = ~ year),
      method = "ML",
      na.action = na.omit,
      control = nlme::glsControl(msMaxIter = 200, msVerbose = FALSE)
    ),
    error = function(e) {
      warning("GLS con CAR(1) falló; se ajusta GLS sin correlación: ", conditionMessage(e))
      nlme::gls(formula, data = data, method = "ML", na.action = na.omit)
    }
  )
}

m0 <- fit_gls(formula0, dat)
m1 <- fit_gls(formula1, dat)

lrt <- as.data.frame(stats::anova(m0, m1))
lrt$comparison <- rownames(lrt)
rownames(lrt) <- NULL
block_p <- suppressWarnings(as.numeric(lrt$`p-value`[nrow(lrt)]))

raw_coefs <- as.data.frame(summary(m1)$tTable)
if (ncol(raw_coefs) == 4L) {
  names(raw_coefs) <- c("estimate", "std_error", "t_value", "p_value")
  raw_coefs$df <- Inf
} else if (ncol(raw_coefs) == 5L) {
  names(raw_coefs) <- c("estimate", "std_error", "df", "t_value", "p_value")
} else {
  stop("Formato inesperado de summary(gls)$tTable: ", ncol(raw_coefs), " columnas")
}
coefs <- data.frame(term = rownames(raw_coefs), raw_coefs, row.names = NULL)
coefs$conf_low <- coefs$estimate - stats::qt(0.975, coefs$df) * coefs$std_error
coefs$conf_high <- coefs$estimate + stats::qt(0.975, coefs$df) * coefs$std_error
coefs$p_fdr <- stats::p.adjust(coefs$p_value, method = "BH")

resid <- data.frame(year = dat$year, fitted = fitted(m1), residual = residuals(m1, type = "normalized"))
metrics <- data.frame(
  model = c("M0_local_controls", "M1_plus_antarctic"),
  n = c(stats::nobs(m0), stats::nobs(m1)),
  AIC = c(stats::AIC(m0), stats::AIC(m1)),
  logLik = c(as.numeric(stats::logLik(m0)), as.numeric(stats::logLik(m1))),
  stringsAsFactors = FALSE
)
hypothesis <- data.frame(
  hypothesis = "H1: el bloque antártico se asocia con log biomasa después de controles",
  null = "H0: todos los coeficientes antárticos del bloque son 0",
  n = nrow(dat),
  p_block_lrt = block_p,
  alpha = 0.05,
  decision = ifelse(is.finite(block_p) && block_p < 0.05, "rechazar H0 bajo esta especificación", "no rechazar H0"),
  caveat = "Asociación temporal; no prueba causalidad ni transporte directo ACC-Humboldt",
  stringsAsFactors = FALSE
)

utils::write.csv(coefs, file.path(out_dir, "model_m1_coefficients.csv"), row.names = FALSE)
utils::write.csv(lrt, file.path(out_dir, "model_block_lrt.csv"), row.names = FALSE)
utils::write.csv(metrics, file.path(out_dir, "model_metrics.csv"), row.names = FALSE)
utils::write.csv(hypothesis, file.path(out_dir, "hypothesis_test.csv"), row.names = FALSE)
utils::write.csv(resid, file.path(out_dir, "model_m1_residuals.csv"), row.names = FALSE)
capture.output(summary(m0), file = file.path(out_dir, "model_m0_summary.txt"))
capture.output(summary(m1), file = file.path(out_dir, "model_m1_summary.txt"))

print(hypothesis)
print(coefs[coefs$term %in% c("ice_antarctic_lag1", "sam_lag1"), , drop = FALSE])

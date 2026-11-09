# Sensibilidad de los modelos de cruceros

Generado por `analysis_r/05_cruise_sensitivity.R`.

- La variante `9_cruceros_original` reproduce las metricas de `analysis_r/data/exploratory_nointerp/`.
- Las variantes ampliadas suman 2102-07, 2202-04 y 2209-11 con fechas aproximadas (dia 15 de cada mes del codigo).
- 2102-07 abarca de febrero a julio; su promedio ambiental es menos representativo, por eso se incluye una variante sin ese crucero.
- El modelo C no se incluye porque el panel de conectividad no esta versionado.

| Variante | Modelo | n | R2 | R2 ajustado | RMSE LOOCV | Coef. Nino 1+2 | p Nino 1+2 |
|---|---|---:|---:|---:|---:|---:|---:|
| 9_cruceros_original | A_local | 9 | 0.472 | 0.296 | 0.349 | -0.174 | 0.102 |
| 9_cruceros_original | B_productivity | 9 | 0.650 | 0.440 | 0.369 | -0.164 | 0.099 |
| 8_cruceros_sin_1998 | A_local | 8 | 0.681 | 0.553 | 0.056 | -0.023 | 0.190 |
| 8_cruceros_sin_1998 | B_productivity | 8 | 0.724 | 0.517 | 0.061 | -0.027 | 0.181 |
| 12_cruceros_ampliado | A_local | 12 | 0.460 | 0.340 | 0.302 | -0.148 | 0.051 |
| 12_cruceros_ampliado | B_productivity | 12 | 0.553 | 0.386 | 0.322 | -0.124 | 0.096 |
| 11_cruceros_ampliado_sin_1998 | A_local | 11 | 0.564 | 0.455 | 0.065 | -0.011 | 0.537 |
| 11_cruceros_ampliado_sin_1998 | B_productivity | 11 | 0.566 | 0.380 | 0.067 | -0.011 | 0.564 |
| 11_cruceros_ampliado_sin_2102-07 | A_local | 11 | 0.454 | 0.317 | 0.313 | -0.153 | 0.067 |
| 11_cruceros_ampliado_sin_2102-07 | B_productivity | 11 | 0.547 | 0.353 | 0.336 | -0.129 | 0.120 |

Son asociaciones exploratorias con muestras muy pequenas; no prueban causalidad.

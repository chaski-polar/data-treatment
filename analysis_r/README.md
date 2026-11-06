# Análisis estadístico de la hipótesis antártica

Este directorio contiene un pipeline reproducible en R para probar, con
p-valores e intervalos de confianza, si los indicadores antárticos aportan
información sobre la biomasa de anchoveta después de controlar el ambiente
local del sistema de Humboldt, ENSO, PDO y tendencia temporal.

## Decisión estadística

La respuesta primaria es `log10(total biomass)` de un stock de `Engraulis
ringens` tomado de RAM Legacy **v4.44**. RAM es una compilación de resultados
de evaluaciones de stock, no una serie de cruceros independientes; por eso el
resultado se interpreta como asociación con una serie evaluada, no como una
prueba de causalidad.

Se comparan dos modelos anidados con GLS y correlación temporal continua:

```text
M0: log_biomass ~ ambiente_local + ENSO + PDO + tendencia
M1: M0 + indicadores_antárticos(t - 1 año)
```

El contraste principal es el likelihood-ratio test entre M0 y M1. El informe
también guarda el p-valor de cada coeficiente, su intervalo de confianza del
95 %, AIC, tamaño de muestra y diagnóstico de autocorrelación.

- `p < 0.05`: se rechaza H0 para el bloque antártico bajo esta especificación.
- `p >= 0.05`: no se rechaza H0; no significa demostrar que H0 sea verdadera.

Los rezagos 0 y 2 años, las variables individuales y las respuestas
alternativas son análisis secundarios y se corrigen con FDR. No se debe
seleccionar el rezago con menor p-valor y presentarlo como confirmatorio.

## Ejecución

Desde la raíz de este repositorio:

```bash
Rscript analysis_r/00_install_packages.R
Rscript analysis_r/01_download_datasets.R
Rscript analysis_r/02_build_annual_panel.R
Rscript analysis_r/03_fit_hypothesis.R
```

El pipeline está ubicado dentro de `data_treatment` y, por defecto, lee los
productos desde la raíz del repositorio actual (`.`). Se puede cambiar la raíz
mediante `ANCHOVETA_DATA_ROOT`.

Para fijar manualmente el stock de RAM después de revisar los candidatos:

```bash
RAM_STOCK_ID=<id> Rscript analysis_r/02_build_annual_panel.R
```

El script guarda primero `ram_engraulis_candidates.csv`. Si hay varios stocks
peruanos o del Humboldt, se debe elegir uno explícitamente antes de publicar
el resultado.

## Fuentes y límites

- RAM Legacy v4.44: DOI `10.5281/zenodo.2542919`.
- CMEMS físico/BGC: el panel mensual existente se conserva como reanálisis/modelo.
- NSIDC G02135: extensión de hielo antártico diaria, agregada por año.
- NOAA PSL/CPC AAO/SAM: se descarga si el endpoint está disponible; si falta,
  el análisis se ejecuta con hielo como indicador antártico y lo reporta.
- FAO, Sea Around Us y Global Fishing Watch no son la respuesta primaria:
  aportan captura reconstruida o esfuerzo aparente, no biomasa acústica.

No se usan las columnas `biomass_total_t_interpolated` ni las salidas de
escenarios/EDO como observaciones para este contraste.

Documentación de acceso: [RAM Legacy en Zenodo](https://zenodo.org/records/2542919),
[paquete ramlegacy](https://docs.ropensci.org/ramlegacy/reference/download_ramlegacy.html),
[manual CMEMS BGC](https://documentation.marine.copernicus.eu/PUM/CMEMS-GLO-PUM-001-029.pdf),
[NSIDC Sea Ice Index](https://nsidc.org/sea-ice-today/sea-ice-tools) y
[AAO/SAM NOAA-CPC](https://www.cpc.ncep.noaa.gov/products/precip/CWlink/teleconnections/monthly/).

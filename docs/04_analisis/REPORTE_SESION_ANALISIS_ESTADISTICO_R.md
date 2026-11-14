# Reporte de sesión: primer análisis estadístico de la hipótesis antártica

**Proyecto:** ANCHOVETA 360  
**Fecha:** 6 de noviembre de 2026  
**Alcance:** adquisición de datos, construcción de panel anual y primer contraste estadístico en R.

> **Nota de corrección (8 de noviembre de 2026):** el valor `p = 0.114958` citado en este reporte comparaba M0 con CAR(1) contra M1 sin correlación, por lo que el contraste no era válido. Con la misma estructura en ambos modelos el resultado es `p = 0.289` (IID); la conclusión (no rechazar H0) no cambia. Ver `analysis_r/README.md` y `docs/04_analisis/informe_analisis_exploratorio_h1_h0.md`.

## 1. Resumen ejecutivo

Durante esta sesión se implementó y ejecutó un pipeline reproducible en R para evaluar si los indicadores de variabilidad antártica aportan información estadística sobre la biomasa evaluada de anchoveta peruana después de controlar condiciones locales del sistema de Humboldt, ENSO, PDO y tendencia temporal.

La respuesta primaria fue la serie de biomasa total (`tb.data`) del stock norte-centro peruano `PANCHPERUNC` en RAM Legacy Stock Assessment Database v4.44. Los indicadores antárticos disponibles para esta primera corrida fueron:

- extensión media anual del hielo marino antártico, con un rezago de un año;
- índice anual AAO/SAM de NOAA/CPC, con un rezago de un año.

El contraste conjunto produjo:

```text
p-valor del bloque antártico = 0.114958
alpha = 0.05
decisión = no rechazar H0
```

Por tanto, esta corrida no encuentra evidencia estadísticamente significativa al 5 % para rechazar H0. El resultado es exploratorio: no demuestra que H0 sea verdadera, no refuta la plausibilidad física de H1 y no prueba causalidad.

## 2. Pregunta e hipótesis operacional

La hipótesis general plantea que la variabilidad del océano Austral puede asociarse temporal y espacialmente con las condiciones del Pacífico Sur, el sistema de Humboldt y el hábitat de la anchoveta peruana.

Para esta primera prueba se utilizó una versión operacional más estrecha:

> Después de controlar el ambiente local, ENSO, PDO y tendencia temporal, el bloque formado por hielo antártico y AAO/SAM rezagados un año presenta una asociación estadísticamente significativa con `log10` de la biomasa total evaluada de anchoveta.

El contraste estadístico fue:

- **H0:** todos los coeficientes del bloque antártico son iguales a cero.
- **H1:** al menos un coeficiente del bloque antártico es distinto de cero.

La H1 general todavía no está completamente representada porque esta corrida no incluye SST antártica, transporte del ACC, AAIW, oxígeno subsuperficial ni conectividad espacial.

## 3. Datos obtenidos y versiones

### 3.1 RAM Legacy

Se descargó y se fijó explícitamente RAM Legacy **v4.44** mediante el paquete R `ramlegacy`. La descarga oficial está archivada en [Zenodo](https://zenodo.org/records/2542919) y la interfaz de R está documentada por [rOpenSci](https://docs.ropensci.org/ramlegacy/reference/download_ramlegacy.html).

La tabla de stocks contiene siete registros de `Engraulis ringens`. Se seleccionó:

```text
stock_id: PANCHPERUNC
área: Peru-IMARPE-NC
descripción: Peruvian anchoveta North-Central Peru
serie: tb.data
observaciones RAM: 53 años
```

RAM es una compilación de resultados de evaluaciones de stock. No es una serie de cruceros independientes ni una observación acústica primaria. Por ello, la respuesta debe interpretarse como biomasa evaluada y no como una medición completamente independiente del proceso de evaluación.

### 3.2 Ambiente local del sistema de Humboldt

Se reutilizó el archivo mensual existente:

```text
../data_treatment/data/processed/tables/monitoring_series_ab.csv
```

El archivo contiene campos mensuales derivados del panel físico y biogeoquímico ya procesado desde CMEMS, además de:

- SST;
- salinidad;
- oxígeno;
- clorofila-a;
- nitrato;
- ICEN/ambiente costero;
- Niño 1+2;
- PDO.

Para hacer coincidir la periodicidad de RAM, se calcularon medias anuales de las variables ambientales. No se utilizó la biomasa interpolada contenida en el archivo mensual.

El producto BGC de CMEMS es un hindcast/modelo global con campos mensuales y verticales; su documentación está disponible en el [manual del producto GLOBAL_MULTIYEAR_BGC_001_029](https://documentation.marine.copernicus.eu/PUM/CMEMS-GLO-PUM-001-029.pdf).

### 3.3 Hielo marino antártico

Se copió al área de trabajo la serie diaria de extensión de hielo marino antártico NSIDC G02135 v4.0:

```text
analysis_r/data/raw/S_seaice_extent_daily_v4.0.csv
```

La serie se resumió como media anual y luego se estandarizó en el periodo común. La documentación oficial se encuentra en [NSIDC Sea Ice Index](https://nsidc.org/sea-ice-today/sea-ice-tools).

### 3.4 AAO/SAM

Se descargó la tabla mensual AAO de NOAA/CPC, desde 1979 hasta el periodo disponible:

```text
analysis_r/data/raw/aao_cpc_monthly.csv
```

Se calculó una media anual para el panel. El archivo original se encuentra en la tabla oficial [AAO mensual NOAA/CPC](https://www.cpc.ncep.noaa.gov/products/precip/CWlink/daily_ao_index/aao/monthly.aao.index.b79.current.ascii.table).

## 4. Panel final

El panel ambiental mensual de origen cubre 1998–2026, pero la serie RAM seleccionada termina en 2015. Por tanto, la intersección real utilizada en el panel final fue 1998–2015:

```text
observaciones de biomasa RAM: 53
años comunes con ambiente: 18 (1998–2015)
años completos para el modelo: 17
```

El panel generado se encuentra en:

[annual_panel_ram44.csv](../../analysis_r/data/processed/annual_panel_ram44.csv)

Las variables se estandarizaron después de construir el periodo común. El panel incluye, entre otras:

```text
log_biomass
sst_z
chlorophyll_a_z
oxygen_z
nino12_z
pdo_z
year_z
ice_antarctic_lag1
sam_lag1
```

No se utilizaron:

- biomasa mensual interpolada;
- biomasa sintética generada por el módulo Python antiguo;
- escenarios futuros de ICEN;
- salidas de la EDO F-Z-A como observaciones;
- desembarques como sustituto automático de biomasa.

## 5. Modelo estadístico

La respuesta fue:

\[
Y_t = \log_{10}(TB_t)
\]

Se compararon dos modelos anidados:

### Modelo M0: controles locales

\[
Y_t = \beta_0 + \beta_1 SST_t + \beta_2 Chl_t + \beta_3 O_2{}_t
 + \beta_4 Niño_t + \beta_5 PDO_t + \beta_6 Tendencia_t + \epsilon_t
\]

### Modelo M1: controles más bloque antártico

\[
Y_t = M0 + \gamma_1 Hielo_{t-1} + \gamma_2 AAO_{t-1} + \epsilon_t
\]

El contraste principal fue el likelihood-ratio test entre M0 y M1 usando máxima verosimilitud.

El ajuste intentó utilizar una correlación temporal continua CAR(1). Con solo 17 observaciones completas, la estimación CAR(1) presentó convergencia singular. El script registró la advertencia y ajustó los dos modelos con GLS sin estructura de autocorrelación. Esta contingencia queda registrada en los archivos de resumen del modelo y limita la interpretación de los p-valores.

## 6. Resultados

### 6.1 Contraste conjunto

| Contraste | n | AIC | LogLik | p-valor |
|---|---:|---:|---:|---:|
| M0: controles locales | 17 | -16.600 | 17.300 | — |
| M1: controles + Antártida | 17 | -17.084 | 18.542 | 0.114958 |

El modelo M1 mejora ligeramente el AIC, pero la mejora conjunta no es significativa al 5 %.

### 6.2 Coeficientes antárticos

| Variable | Estimación | Error estándar | IC 95 % | p-valor |
|---|---:|---:|---:|---:|
| Hielo antártico, rezago 1 año | 0.0532 | 0.0692 | [-0.0824, 0.1888] | 0.4639 |
| AAO/SAM, rezago 1 año | -0.0533 | 0.0494 | [-0.1502, 0.0435] | 0.3116 |

Los intervalos incluyen el valor cero en ambos predictores.

El archivo completo de resultados está en [model_m1_coefficients.csv](../../analysis_r/data/processed/model_m1_coefficients.csv) y el contraste conjunto en [model_block_lrt.csv](../../analysis_r/data/processed/model_block_lrt.csv).

## 7. Decisión sobre las hipótesis

Con α = 0.05:

```text
p = 0.114958 > 0.05
```

La decisión de esta corrida es:

> **No rechazar H0.**

La formulación correcta no es “se demostró que no existe relación”. El resultado significa que, con esta respuesta, periodo, resolución anual, conjunto de controles y bloque antártico, no hay evidencia suficiente para rechazar la hipótesis nula.

La H1 general permanece abierta porque todavía faltan variables que representan mecanismos físicos más cercanos a la cadena propuesta:

```text
Antártida → Pacífico Sur subsuperficial → Humboldt local → hábitat de anchoveta
```

## 8. Reproducibilidad

Desde la raíz del repositorio:

```bash
Rscript analysis_r/00_install_packages.R
Rscript analysis_r/01_download_datasets.R
Rscript analysis_r/02_build_annual_panel.R
Rscript analysis_r/03_fit_hypothesis.R
```

El instalador utiliza una biblioteca local en `analysis_r/Rlib/`. Los datos brutos descargados se excluyen del control de versiones mediante `.gitignore`, mientras que los scripts y resultados procesados quedan disponibles en `analysis_r/`.

Archivos de salida principales:

- [annual_panel_metadata.csv](../../analysis_r/data/processed/annual_panel_metadata.csv)
- [annual_panel_ram44.csv](../../analysis_r/data/processed/annual_panel_ram44.csv)
- [hypothesis_test.csv](../../analysis_r/data/processed/hypothesis_test.csv)
- [model_metrics.csv](../../analysis_r/data/processed/model_metrics.csv)
- [model_m0_summary.txt](../../analysis_r/data/processed/model_m0_summary.txt)
- [model_m1_summary.txt](../../analysis_r/data/processed/model_m1_summary.txt)
- [ram_engraulis_candidates.csv](../../analysis_r/data/processed/ram_engraulis_candidates.csv)

Entorno usado durante la sesión:

```text
R 4.6.2
nlme 3.1-171
ramlegacy 0.2.0
```

## 9. Limitaciones principales

1. **Tamaño muestral pequeño.** Solo 17 años tienen respuesta RAM y todos los predictores completos.
2. **Respuesta evaluada.** RAM no sustituye a una serie homogénea de cruceros acústicos IMARPE.
3. **Cobertura ambiental y temporal.** La serie local comienza en 1998 y la respuesta RAM seleccionada termina en 2015; por ello el panel final tiene 18 años, aunque RAM contiene años anteriores.
4. **Representación antártica incompleta.** No se incluyeron SST antártica, ACC, AAIW, oxígeno subsuperficial ni transporte meridional.
5. **Sin componente espacial.** Este modelo prueba una asociación temporal de stock, no una relación espacial con presencia o NASC.
6. **Autocorrelación no estimada en la corrida final.** CAR(1) no convergió y el resultado reportado usa GLS sin correlación.
7. **Producto ambiental modelado.** Las variables CMEMS no deben confundirse con observaciones in situ.
8. **No causalidad.** Un p-valor significativo, si apareciera en una futura especificación, indicaría asociación condicionada, no causalidad.

## 10. Siguiente fase recomendada

Antes de interpretar la hipótesis general como respaldada o refutada, la siguiente fase debería:

1. incorporar un indicador explícito de SST antártica y una proxy independiente de circulación/ACC;
2. construir variables de AAIW usando temperatura, salinidad, oxígeno y densidad subsuperficiales;
3. ampliar la respuesta con biomasa acústica IMARPE verificable y separar stock norte-centro, stock sur y anchoveta chilena;
4. evaluar rezagos preespecificados de 0, 1 y 2 años, sin seleccionar solo por el menor p-valor;
5. repetir el contraste con GLS AR(1), HAC/Newey-West y validación por bloques temporales;
6. ejecutar un modelo de mediación exploratorio para evaluar `Antártida → Pacífico Sur → Humboldt`;
7. usar FAO, Sea Around Us y Global Fishing Watch únicamente como respuestas o controles complementarios de captura/esfuerzo, no como biomasa primaria.

La conclusión científica de esta sesión es, por tanto, **“no se rechaza H0 en la primera prueba operacional”**, con evidencia insuficiente para evaluar todavía la cadena antártica completa.

# Reporte: datos antárticos necesarios para el análisis exploratorio de H1

**Proyecto:** ANCHOVETA 360  
**Fecha:** 6 de noviembre de 2026  
**Decisión metodológica:** limitar el estudio a una evaluación exploratoria de H1.

## 1. Objetivo de esta fase

La investigación no intentará demostrar una conectividad oceanográfica completa entre la Antártida y el sistema de Humboldt. Esa afirmación requeriría una combinación de observaciones subsuperficiales, transporte, trayectorias, biogeoquímica y datos biológicos espacialmente armonizados que actualmente no está disponible en el repositorio.

La fase exploratoria evaluará si los indicadores antárticos presentan asociaciones temporales y espaciales reproducibles con variables del Pacífico Sur y del sistema de Humboldt.

La hipótesis operacional será:

> Las anomalías antárticas de hielo marino, temperatura superficial, circulación y estructura superior del océano se asocian, con posibles rezagos de 0, 3, 6, 12, 18 y 24 meses, con anomalías ambientales del Pacífico Sur y de Humboldt; estas últimas se relacionan con indicadores disponibles de hábitat o biomasa de anchoveta.

Esta formulación es más limitada que H1 general. Permitirá identificar señales compatibles con la hipótesis, pero no probar transporte directo ni causalidad.

## 2. Situación actual del repositorio

La revisión de la documentación y los archivos confirmó que actualmente existen:

- extensión diaria de hielo marino antártico NSIDC;
- índice mensual AAO/SAM de NOAA/CPC;
- climatologías WOA23;
- un panel peruano mensual de aproximadamente 344 meses;
- productos CMEMS de física y biogeoquímica recortados al dominio peruano;
- biomasa evaluada anual RAM Legacy;
- series históricas de biomasa desovante;
- 70 registros hidroacústicos únicos de 1985–2017.

Los archivos CMEMS y ERA5 existentes fueron descargados usando aproximadamente:

```text
longitud: -85 a -70 °O
latitud: -18.35 a -3.38 °S
```

Por ello, los productos actualmente almacenados permiten estudiar principalmente Perú/Humboldt. No contienen una cobertura antártica espacial suficiente para representar SST, corrientes, SSH, temperatura y salinidad subsuperficiales o AAIW fuera de la costa peruana.

La extensión de hielo y el AAO/SAM sí pueden utilizarse de inmediato, pero son indicadores agregados. No sustituyen una observación de la Corriente Circumpolar Antártica.

## 3. Qué se necesita realmente para H1 exploratoria

No es necesario descargar todos los productos antárticos existentes. Para esta fase se recomienda un conjunto mínimo de cinco componentes:

1. **Índice climático:** AAO/SAM.
2. **Hielo marino:** extensión total y, preferiblemente, concentración espacial por sector.
3. **Estado físico 3D:** temperatura, salinidad, velocidad, SSH y capa de mezcla.
4. **Corriente superficial independiente:** velocidad superficial para comprobar si las señales de circulación son coherentes con el producto físico.
5. **Observaciones subsuperficiales:** perfiles Argo para validar la estructura de temperatura y salinidad del producto modelado.

La clorofila y la productividad antárticas no son imprescindibles para la primera prueba de conectividad física. Pueden incorporarse en una segunda etapa si el modelo físico muestra asociaciones razonables.

## 4. Fuentes recomendadas, ordenadas por utilidad para esta fase

### 4.1 Prioridad 1: CMEMS Global Ocean Physics Reanalysis

**Producto recomendado:** Global Ocean Physics Reanalysis  
**Product ID:** `GLOBAL_MULTIYEAR_PHY_001_030`  
**Dataset mensual:** `cmems_mod_glo_phy-all_my_0.25deg_P1M-m`  
**Institución:** Copernicus Marine Service.

En el catálogo oficial se describe como un producto global con temperatura, salinidad, velocidad, altura del nivel del mar, capa de mezcla y variables de hielo. La versión global de 0.25° tiene 75 niveles verticales y comienza en 1993; la versión disponible en el catálogo se actualiza regularmente y debe fijarse en el manifiesto de descarga para asegurar reproducibilidad. [Catálogo oficial CMEMS](https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_001_030) [servicios y dataset mensual](https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_ENS_001_031/services).

**Variables a descargar:**

```text
thetao / temperatura potencial
so / salinidad
uo, vo / velocidad zonal y meridional
zos / altura de la superficie del mar
mlotst / profundidad de capa de mezcla
sea ice fraction, si está disponible en la versión seleccionada
```

**Resolución recomendada para exploración:** mensual, 0.25°, 0–1000 m. No se necesita descargar el océano completo a máxima resolución. Se deben solicitar únicamente las cajas antárticas y del Pacífico Sur.

**Cajas iniciales:**

```text
Península Antártica: 60–75°S, 75–55°O
Bellingshausen: 65–75°S, 105–70°O
Pacífico Sur intermedio: 45–55°S, 130–75°O
Pacífico Sur subtropical: 35–50°S, 120–75°O
Transición hacia Humboldt: 20–35°S, 110–75°O
Humboldt peruano: conservar el dominio existente
```

**Uso en H1:** construir anomalías mensuales regionales de SST, temperatura a 100–300–500 m, salinidad, SSH, velocidad y capa de mezcla. Las variables subsuperficiales se usarán como indicadores de propagación de señales, no como prueba de que el agua antártica llega directamente a Perú.

**Acceso recomendado:** Python mediante `copernicusmarine.subset()` o `copernicusmarine.open_dataset()` y `xarray`. Requiere cuenta y credenciales de Copernicus Marine configuradas. También puede usarse desde R leyendo los NetCDF descargados con `ncdf4`, `terra` o `stars`, pero Python es preferible para el recorte y la agregación inicial.

**Limitaciones:** es un reanálisis/modelo asimilado, no una observación directa. La resolución de 0.25° puede ser insuficiente para procesos costeros y filamentos. Para H1 exploratoria es adecuado como descriptor regional de variabilidad de gran escala.

### 4.2 Prioridad 1: NSIDC Sea Ice Concentration

**Producto recomendado:** NOAA/NSIDC Climate Data Record of Passive Microwave Sea Ice Concentration  
**Versión consultable:** G02202, versión 6 según la ficha oficial disponible.  
**Institución:** NSIDC/NOAA/NASA.

El producto contiene concentración diaria y mensual, con una grilla polar estereográfica de 25 km y cobertura desde octubre de 1978 para las regiones polar norte y sur. [Ficha oficial NSIDC G02202 v6](https://nsidc.org/data/g02202/versions/6).

Como alternativa de continuidad y documentación, el producto Bootstrap G10016 v4 ofrece concentración diaria y mensual hasta el 31 de diciembre de 2025, también en grilla polar de 25 km; su DOI informado es `10.5067/X5LG68MH013O`. [Actualización oficial NSIDC Bootstrap v4](https://nsidc.org/data/user-resources/data-announcements/data-set-update-bootstrap-sea-ice-concentrations-nimbus-7-smmr-and-dmsp-ssmi-ssmis-version-4).

**Uso recomendado:** descargar solo la región sur y calcular, por mes:

- concentración media por sector;
- extensión derivada usando un umbral documentado;
- área de hielo;
- anomalía respecto de 1998–2024;
- fecha de máximo y mínimo estacional;
- índices separados para Península Antártica y Bellingshausen.

**Acceso:** NetCDF vía descarga web/NSIDC y procesamiento con Python (`xarray`, `rioxarray`, `pyproj`) o R (`terra`, `ncdf4`). Para esta fase se recomienda generar un CSV regional mensual después del procesamiento, no utilizar directamente miles de archivos gridded en el modelo estadístico.

**Limitaciones:** los algoritmos pasivos por microondas tienen incertidumbre cerca de la costa, en zonas de hielo fragmentado y durante derretimiento superficial. La concentración no debe confundirse con extensión ni área.

### 4.3 Prioridad 1: NOAA/CPC AAO/SAM

**Producto:** Antarctic Oscillation (AAO) Monthly Time Series  
**Institución:** NOAA/CPC, distribuido también por NOAA Physical Sciences Laboratory.

El índice mensual está disponible desde enero de 1979 y se calcula a partir del primer modo EOF de anomalías de altura geopotencial a 700 hPa al sur de 20°S. [Serie oficial NOAA PSL/AAO](https://psl.noaa.gov/data/timeseries/month/DS/AAO_CPC/).

Ya existe en el repositorio como:

```text
analysis_r/data/raw/aao_cpc_monthly.csv
```

**Uso:** mantenerlo como covariable climática de control y como predictor antártico de referencia. Debe probarse con rezagos de 0, 3, 6, 12, 18 y 24 meses, pero sin incluir simultáneamente demasiadas versiones del mismo índice.

**Limitación:** AAO/SAM describe circulación atmosférica hemisférica; no mide directamente corrientes oceánicas, hielo ni transporte de masas de agua.

### 4.4 Prioridad 2: OSCAR Surface Currents

**Producto recomendado:** OSCAR Surface Currents Final v2.0  
**Dataset ID:** `OSCAR_L4_OC_FINAL_V2.0`  
**DOI:** `10.5067/OSCAR-25F20`  
**Institución:** Earth & Space Research / NASA-JPL PO.DAAC.

OSCAR proporciona corrientes superficiales globales diarias en una grilla de 0.25°. El producto final cubre desde 1993 hasta la última fecha final disponible; el catálogo indica cobertura global y acceso mediante PO.DAAC/Harmony. [Ficha oficial PO.DAAC](https://podaac.jpl.nasa.gov/dataset/OSCAR_L4_OC_FINAL_V2.0) [documentación del producto](https://www.esr.org/data-products/oscar/).

**Variables:**

```text
u, v / velocidad zonal y meridional
ug, vg / componentes geostróficas, cuando estén disponibles
```

**Uso en H1:** crear índices de velocidad y dirección en transectos o cajas del ACC y del Pacífico Sur. También se puede calcular la componente de la corriente paralela a una dirección definida por cada transecto.

**Acceso:** Python mediante `earthaccess`, `podaac-data-subscriber`, OPeNDAP o Harmony; lectura con `xarray`. R puede leer los NetCDF con `ncdf4` o `terra`, pero la descarga y el recorte son más sencillos en Python.

**Limitaciones:** OSCAR representa corrientes superficiales de la capa mezclada, no el transporte profundo ni el AAIW. Es una estimación basada en SSH, viento y SST, por lo que no debe usarse como validación completamente independiente de todos los campos CMEMS.

### 4.5 Prioridad 2: Argo GDAC

**Producto:** perfiles Argo oficiales de temperatura, salinidad y presión.  
**Institución:** Argo Data Management Team.  
**Acceso:** GDAC de Estados Unidos o Francia, con índices de perfiles y archivos NetCDF.

Los GDAC contienen perfiles, metadatos, trayectorias y datos técnicos completos. Los perfiles pueden seleccionarse por ubicación, fecha, profundidad y nivel de control de calidad. [Acceso oficial Argo GDAC](https://argo.ucsd.edu/data/data-from-gdacs/) [portal general de datos Argo](https://argo.ucsd.edu/data/).

**Selección para ANCHOVETA 360:**

```text
latitud: 20–75°S
longitud: 130–55°O
fecha: 1998–2025
variables: TEMP, PSAL, PRES
profundidad: superficie–1000 m, con énfasis en 100–500 m
modo: preferentemente delayed mode; luego real time si se documenta
```

**Uso:** no se propone usar cada perfil como observación independiente en el primer modelo. Se propone utilizarlos para:

- validar medias y anomalías CMEMS;
- estimar la profundidad y propiedades de la capa subsuperficial;
- construir una métrica exploratoria de presencia de agua relativamente fría/salina compatible con AAIW;
- cuantificar cobertura observacional por región y año.

**Acceso:** Python con índices GDAC, `argopy` o descarga HTTP/FTP; R con `argoFloats`, `oce` o lectura NetCDF. Python es preferible para localizar perfiles y aplicar filtros de calidad.

**Limitaciones:** cobertura irregular, especialmente en altas latitudes y años tempranos. Argo no es una grilla continua y no debe interpolarse sin documentar la incertidumbre.

## 5. Datos que no son prioritarios en esta primera fase

### 5.1 Biogeoquímica antártica

El producto CMEMS Global Ocean Biogeochemistry Hindcast `GLOBAL_MULTIYEAR_BGC_001_029` ofrece variables de plancton, nutrientes, oxígeno y sistema de carbonatos a escala global, con resolución de 0.25° y 75 niveles según el catálogo oficial. [Catálogo oficial CMEMS BGC](https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_BGC_001_029).

Es útil para una fase posterior, pero no es indispensable para la prueba exploratoria inicial de conectividad física. Si se incorpora desde el comienzo, debe reducirse a pocos indicadores preespecificados: clorofila superficial, oxígeno a profundidad seleccionada y nitrato superficial o subsuperficial.

### 5.2 Clorofila satelital global

Puede usarse OC-CCI o el producto de color oceánico de Copernicus para comparar productividad entre Antártida, Pacífico Sur y Humboldt. Sin embargo, la cobertura cerca del hielo, nubosidad y cambios de sensores producen problemas de comparabilidad. Debe añadirse solo después de construir correctamente el panel físico.

### 5.3 OISST de NOAA

NOAA OISST v2.1 es una alternativa independiente para SST global, con resolución de 0.25° y cobertura desde septiembre de 1981 hasta el presente. Integra satélite, barcos, boyas y Argo, y completa la grilla mediante interpolación. [Producto oficial NOAA OISST](https://www.ncei.noaa.gov/products/optimum-interpolation-sst).

Se recomienda usar OISST como control de sensibilidad, no simultáneamente con SST CMEMS en el modelo principal. Incluir ambas podría generar colinealidad y no añade necesariamente información independiente.

## 6. Configuración mínima recomendada

Para evitar una descarga demasiado grande, el primer análisis antártico debería utilizar:

| Componente | Producto | Resolución de trabajo | Función |
|---|---|---:|---|
| Clima atmosférico | NOAA/CPC AAO | mensual | predictor climático agregado |
| Hielo actual | NSIDC G02135 existente | diario → mensual | continuidad y anomalías de extensión |
| Hielo espacial | NSIDC G02202 o Bootstrap v4 | mensual, 25 km | sectores y concentración |
| Física 3D | CMEMS `GLOBAL_MULTIYEAR_PHY_001_030` | mensual, 0.25° | SST, T/S, SSH, velocidad, MLD |
| Corriente independiente | OSCAR v2.0 final | diario → mensual, 0.25° | corriente superficial y dirección |
| Validación | Argo GDAC | perfiles irregulares | T/S subsuperficiales y control de calidad |

La respuesta biológica se mantendrá separada en tres análisis:

1. RAM `tb.data`, anual, para una prueba temporal de largo plazo.
2. Biomasa hidroacústica por campaña, después de completar metadatos.
3. Desembarques, solo en un modelo pesquero con esfuerzo, cuotas, vedas y temporadas.

No se deben mezclar estas respuestas en una única variable dependiente.

## 7. Estructura de los índices regionales

Para cada producto se deben calcular medias y anomalías en regiones, no un promedio antártico único. Se recomienda generar:

```text
antarctic_peninsula_*
bellingshausen_*
south_pacific_45_55S_*
south_pacific_35_50S_*
transition_humboldt_*
humboldt_peru_*
```

Para cada región y variable se guardarán:

- media espacial ponderada por área;
- mediana espacial;
- desviación estándar espacial;
- anomalía mensual respecto de 1998–2024;
- tendencia lineal estimada dentro del periodo;
- número de celdas válidas;
- proporción de datos faltantes;
- fuente, versión y fecha de descarga.

No se recomienda promediar automáticamente todos los sectores antárticos. La Península y Bellingshausen pueden presentar dinámicas distintas y deben conservarse como predictores separados o combinarse solo después de comprobar su correlación.

## 8. Diseño estadístico exploratorio

### 8.1 Etapa 1: asociación Antártida–Pacífico/Humboldt

Para cada variable regional se calculará:

\[
X_{r,t}^{*} = \frac{X_{r,t} - \overline{X}_{r,m}}{s_{r,m}}
\]

donde la climatología se calcula por mes `m`, región `r` y periodo base 1998–2024.

Luego se ajustarán modelos con rezagos:

\[
Y_{t} = \alpha + \sum_{k \in K} \beta_k A_{t-k} + \gamma Z_t + f(t) + \varepsilon_t
\]

donde:

- `Y_t` es SST, clorofila, oxígeno, salinidad o surgencia de Humboldt;
- `A_{t-k}` es un índice antártico regional;
- `K = {0, 3, 6, 12, 18, 24}` meses;
- `Z_t` contiene Niño 1+2, PDO, estacionalidad y tendencia;
- `f(t)` representa una tendencia suave o spline temporal.

La selección de rezagos debe definirse antes de revisar resultados finales. Los seis rezagos no deben interpretarse como seis pruebas independientes sin corrección por multiplicidad.

### 8.2 Etapa 2: ambiente de Humboldt–anchoveta

Para RAM se usará la escala anual y pocos predictores preseleccionados. Para cruceros se usarán promedios ambientales dentro de la ventana real de cada campaña:

\[
\log(B_i) = \alpha + f_1(SST_i) + f_2(O_2_i) + f_3(Chl_i) + \beta A_i + u_{year(i)} + \varepsilon_i
\]

La inclusión de `A_i` solo será válida si la fecha de la campaña está suficientemente documentada. Si el CSV solo contiene un código sin fecha completa, no debe asignarse un rezago exacto.

### 8.3 Interpretación

La evidencia se clasificará como:

- asociación antártica con ambiente peruano;
- asociación consistente con rezago;
- mejora incremental frente al modelo local;
- resultado sensible a la fuente o al producto;
- evidencia insuficiente.

No se utilizará lenguaje causal como “la Antártida determina” o “el ACC transporta la señal a Humboldt” a partir de correlaciones o de importancia de variables en XGBoost.

## 9. Plan de implementación en el repositorio

### 9.1 Nuevos scripts Python

Se recomienda crear:

```text
scripts/06_download_antarctic_exploratory.py
scripts/07_build_antarctic_indices.py
scripts/08_validate_antarctic_with_argo.py
```

`06_download_antarctic_exploratory.py` debe:

- aceptar `--start`, `--end`, `--region` y `--force`;
- descargar CMEMS solo para las cajas seleccionadas;
- registrar dataset ID, versión, variables, profundidad, fecha de descarga y URL;
- descargar NSIDC por separado;
- recuperar OSCAR final con un mecanismo de acceso documentado;
- no sobrescribir datos brutos sin `--force`.

`07_build_antarctic_indices.py` debe:

- convertir todos los tiempos a UTC y luego a mes calendario;
- normalizar longitudes a un único sistema;
- aplicar máscaras de tierra y hielo cuando corresponda;
- calcular promedios regionales y anomalías;
- guardar un NetCDF intermedio y un CSV mensual compacto.

`08_validate_antarctic_with_argo.py` debe:

- filtrar perfiles por calidad;
- evitar duplicar perfiles de real-time y delayed mode;
- comparar CMEMS contra Argo en profundidad y tiempo coincidentes;
- generar error medio, RMSE, sesgo y número de perfiles por región/año.

### 9.2 Integración en R

R se utilizará para el análisis estadístico y los gráficos de inferencia:

```text
analysis_r/04_build_antarctic_panel.R
analysis_r/05_fit_exploratory_h1.R
analysis_r/06_sensitivity_products_lags.R
```

Paquetes recomendados:

```r
terra
ncdf4
tidyverse
lubridate
mgcv
nlme
lmtest
forecast
```

Python será el punto principal de adquisición y recorte; R leerá los índices regionales ya compactados. Así se evita que Python y R descarguen versiones diferentes del mismo producto.

## 10. Criterios de éxito de la fase exploratoria

La fase se considerará técnicamente completa si logra:

1. un panel mensual 1998–2024 o 1998–2025 con metadatos de versión;
2. al menos tres regiones antárticas y tres regiones de transición;
3. hielo, SAM, SST, T/S y velocidad superficial disponibles;
4. validación básica de T/S contra Argo;
5. análisis con seis rezagos predefinidos;
6. control explícito de Niño 1+2, PDO, estacionalidad y tendencia;
7. comparación de modelo local frente a modelo con bloque antártico;
8. análisis de sensibilidad al producto SST y al producto de corrientes;
9. intervalos de confianza o incertidumbre de las asociaciones;
10. separación entre observaciones, reanálisis, estimaciones satelitales y productos derivados.

## 11. Limitaciones que deben permanecer en el reporte científico

- El CMEMS es un reanálisis y no una observación directa.
- OSCAR representa la capa superficial y no reemplaza una sección subsuperficial.
- Argo tiene cobertura irregular y no resuelve por sí solo el transporte de AAIW.
- El hielo satelital puede presentar sesgos cerca de la costa y en hielo marginal.
- Los promedios regionales pueden ocultar frentes y gradientes importantes.
- La escala temporal 1998–2024 limita el número de ciclos climáticos efectivos.
- Los rezagos pueden confundirse con tendencias y autocorrelación.
- El tamaño de muestra biológico sigue siendo pequeño frente al número de predictores potenciales.
- La asociación estadística no prueba causalidad ni transporte directo Antártida–Humboldt.

## 12. Conclusión y decisión

Para el análisis exploratorio de H1 no se necesita descargar toda la información antártica disponible. La combinación recomendada es:

```text
AAO/SAM existente
+ hielo NSIDC existente y concentración espacial
+ CMEMS Global Physics mensual 0.25°
+ OSCAR v2.0 como corriente superficial complementaria
+ Argo GDAC para validación subsuperficial
```

Con este conjunto se puede evaluar si las anomalías antárticas regionales preceden o se asocian con cambios físicos en el Pacífico Sur y Humboldt. También se puede determinar si el bloque antártico añade información a un modelo local de hábitat de anchoveta.

La conclusión final deberá expresarse en términos de asociaciones, rezagos, robustez entre productos y capacidad explicativa incremental. No deberá presentarse como demostración de que la Corriente Circumpolar Antártica se transforma en la Corriente de Humboldt ni como prueba causal sobre la biomasa de anchoveta.

## 13. Fuentes oficiales consultadas

- [Copernicus Marine Global Ocean Physics Reanalysis](https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_001_030)
- [Copernicus Marine Global Ocean Ensemble Physics Reanalysis](https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_ENS_001_031)
- [Copernicus Marine Global Ocean Biogeochemistry Hindcast](https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_BGC_001_029)
- [NSIDC NOAA/NSIDC Sea Ice Concentration CDR](https://nsidc.org/data/g02202/versions/6)
- [NSIDC Bootstrap Sea Ice Concentration v4](https://nsidc.org/data/user-resources/data-announcements/data-set-update-bootstrap-sea-ice-concentrations-nimbus-7-smmr-and-dmsp-ssmi-ssmis-version-4)
- [NOAA PSL AAO/SAM](https://psl.noaa.gov/data/timeseries/month/DS/AAO_CPC/)
- [NASA/JPL PO.DAAC OSCAR v2.0](https://podaac.jpl.nasa.gov/dataset/OSCAR_L4_OC_FINAL_V2.0)
- [Earth & Space Research OSCAR documentation](https://www.esr.org/data-products/oscar/)
- [Argo GDAC access](https://argo.ucsd.edu/data/data-from-gdacs/)
- [NOAA NCEI OISST v2.1](https://www.ncei.noaa.gov/products/optimum-interpolation-sst)

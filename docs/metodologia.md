# Metodología del proyecto

## 1. Propósito

El proyecto estudia la relación entre la variabilidad oceanográfica, la productividad marina y la dinámica de la anchoveta peruana (*Engraulis ringens*) en el sistema de la Corriente de Humboldt.

El objetivo no es producir una cuota pesquera oficial ni afirmar causalidad a partir de una sola fuente. El objetivo es construir, comparar y validar modelos de complejidad creciente:

1. **Experimento A:** línea base abiótica.
2. **Experimento B:** línea base más productividad.
3. **Experimento C:** sistema dinámico fitoplancton–zooplancton–anchoveta.

El periodo de trabajo común se define inicialmente como **1998–2026**, limitado en cada fuente por su fecha real de disponibilidad. La caja principal del mar peruano es aproximadamente:

```text
longitud: -85.0 a -70.0 °O
latitud:  -18.35 a -3.38 °S
```

## 2. Principio metodológico

Las fuentes se conservan primero en formato original dentro de `data/raw/`. Después se transforman a variables comparables y, finalmente, se unen por fecha y espacio en un panel mensual.

```text
fuentes originales
        ↓
descarga y manifiesto
        ↓
control de calidad y unidades
        ↓
recorte espacial
        ↓
agregación mensual
        ↓
variables derivadas y rezagos
        ↓
panel para A, B y C
        ↓
ajuste, validación y visualización
```

No se rellenan silenciosamente los datos faltantes. Cada valor debe conservar su fuente, resolución, unidad y nivel de confianza.

## 3. Datos de respuesta

La variable de respuesta puede representar dos conceptos diferentes y no deben mezclarse sin una decisión explícita:

### 3.1 Biomasa

- Biomasa acústica desovante de IMARPE, 1964–2020.
- Biomasa total por crucero, principalmente 1998, 2004 y 2018–2026.
- Biomasa de cruceros del stock norte-centro y, cuando corresponda, del stock sur.

La biomasa por crucero es una observación irregular: no existe necesariamente un valor para cada mes. Por ello se conserva como observación de calibración/validación y no se interpola automáticamente como si fuera una medición mensual directa.

### 3.2 Desembarques

Los desembarques mensuales cubren aproximadamente 1998–2026:

- 1998–2002: tablas de Bouchon et al. / IMARPE.
- 2003–2026: BCRP/PRODUCE.

Los desembarques no son biomasa. También dependen de cuotas, vedas, días de pesca, capacidad de flota y decisiones operativas. Si se usan como respuesta, se incorporan las variables de manejo y una marca que indique el cambio de fuente.

Archivos principales:

- `data/biomasa_desovante_acustica_1964_2020.csv`
- `data/punto1_anchoveta/1d_biomasa_cruceros_imarpe/biomasa_total_cruceros.csv`
- `data/punto1_anchoveta/1a_desembarques_mensuales_bcrp/desembarques_anchoveta_mensual_2003_2026.csv`
- `data/punto1_anchoveta/1b_desembarques_1998_2002_bouchon/desembarques_anchoveta_mensual_1998_2003_por_departamento.csv`

## 4. Fuentes ambientales

| Grupo | Variables | Fuente/proceso |
|---|---|---|
| Física | temperatura, salinidad, corrientes, SSH | Reanálisis físico multianual de CMEMS |
| Biogeoquímica | clorofila, oxígeno, nitrato, fosfato, carbono fitoplanctónico | Reanálisis BGC de CMEMS |
| Color del océano | clorofila independiente | OC-CCI vía ERDDAP |
| Atmósfera | viento a 10 m | ERA5 vía CDS API |
| Productividad | PAR, Kd490, POC | NASA Ocean Color; se requieren composiciones mensuales |
| Climatología | nitrato, fosfato, silicato | WOA23; referencia mensual climatológica |
| Clima | PDO; posteriormente ONI/Niño 1+2 o ICEN | NOAA/PSL y fuentes oficiales de índices |

Los archivos actualmente descargados se describen en `data/raw/experiment_b_download_manifest.json` y en los manifiestos de descarga generales.

## 5. Descarga y organización

Las fuentes se descargan mediante:

- `scripts/01_download_data.py`: CMEMS, NOAA PDO, WOA23 y NSIDC.
- `scripts/02_download_experiment_b.py`: CMEMS para B, OC-CCI, NASA Ocean Color y ERA5.

Las credenciales no se guardan en el proyecto:

- CMEMS usa la configuración del cliente `copernicusmarine`.
- NASA usa la sesión de Earthdata gestionada por `earthaccess`.
- ERA5 usa `/home/aroon/.cdsapirc` para `cdsapi`.

Cada descarga debe producir un manifiesto con fuente, dataset, variables, periodo, ruta y error, si lo hubiera.

## 6. Preprocesamiento

### 6.1 Recorte espacial

Los NetCDF se recortan a la caja del mar peruano. Para análisis regional se pueden definir subregiones, por ejemplo:

- norte-centro;
- sur;
- franja costera;
- plataforma continental;
- mar abierto.

La distancia a la costa se calcula desde las coordenadas y una geometría de línea de costa; no se trata como una observación descargada.

### 6.2 Profundidad

Las variables superficiales se extraen usando los niveles más cercanos a la superficie. Esto no debe confundirse con la profundidad de la oxiclina o la capa de mezcla. Para esas variables se requieren perfiles verticales suficientes de Argo, WOD, IMARPE o un producto que las entregue directamente.

### 6.3 Tiempo

El panel principal se organiza con una fila por mes. Las fuentes diarias se agregan mensualmente mediante una estadística documentada, normalmente media o mediana. Las composiciones satelitales mensuales se conservan como mensuales y no se interpolan para ocultar huecos.

### 6.4 Unidades

Antes de unir fuentes se normalizan:

- temperatura a °C;
- salinidad a PSU;
- oxígeno a una unidad documentada y consistente;
- nutrientes a sus unidades originales con conversión explícita si se necesita;
- clorofila a mg m⁻³;
- carbono fitoplanctónico a mg C m⁻³ cuando corresponda;
- capturas y biomasa a toneladas.

### 6.5 Anomalías y rezagos

Para separar estacionalidad de anomalías se calcula, cuando sea necesario:

\[
X'_t = X_t - \overline{X}_{mes}
\]

También se pueden calcular rezagos de 1, 2, 3 y 6 meses para representar respuestas retardadas de la anchoveta a productividad, viento o temperatura.

## 7. Variables derivadas

Algunas variables de las ecuaciones no se descargan directamente.

### 7.1 ICEN/Niño 1+2

Se calcula el promedio espacial de SST en la región Niño 1+2, se resta una climatología de referencia y se aplica el promedio móvil definido por la metodología oficial. ONI/Niño 3.4 no debe confundirse con ICEN: el primero representa el Pacífico ecuatorial central y el segundo las condiciones costeras del Pacífico oriental.

### 7.2 Afloramiento y Ekman

Desde el viento ERA5 se calculan el estrés del viento y el transporte de Ekman. El índice resultante es una variable derivada, no una descarga independiente.

### 7.3 Zona eufótica

A partir de Kd490 se estima una profundidad eufótica aproximada:

\[
Z_{eu} \approx \frac{4.6}{K_d(490)}
\]

### 7.4 Fracciones de tamaño

Las fracciones pico, nano y micro pueden estimarse desde clorofila mediante relaciones publicadas, pero deben marcarse como estimadas y no como observaciones directas.

## 8. Experimento A: línea base abiótica

El Experimento A evalúa la relación entre la respuesta de anchoveta y variables físicas locales:

```text
SST, SSS, oxígeno, distancia a la costa, Niño 1+2/ICEN
```

La formulación estadística documentada es un GAM con distribución Tweedie:

\[
Y_t = \beta_0 + s(SST) + s(SSS) + s(SSO) + s(dc)
      + s(year) + te(long,lat) + s(ICEN) + \epsilon
\]

También se define un índice de idoneidad abiótica:

\[
HSI_A = (S_{SST}S_{SSS}S_{O2}S_{dc})^{1/4}
\]

La implementación actual de `src/nasahackaton/models/experiment_a.py` es una línea base cuadrática estandarizada. No debe describirse todavía como el GAM Tweedie final. Primero se debe construir el panel real y luego decidir si se reemplaza por un GAM o un modelo equivalente.

## 9. Experimento B: productividad

El Experimento B agrega el estado trófico del ecosistema:

```text
clorofila, nitrato, fosfato, carbono fitoplanctónico,
PAR, Kd490, viento, afloramiento y captura
```

Su objetivo es comprobar si la productividad mejora la explicación de la biomasa respecto a A.

### 9.1 HSI trófico

\[
HSI_B = (S_{SST}S_{SSS}S_{O2}S_{dc}S_{Chl})^{1/5}
\]

### 9.2 Capacidad de carga

Se puede estimar una capacidad de carga ambiental dependiente de SST y clorofila:

\[
K(SST,Chl_a) = K_0
\left(\frac{Chl_a}{Chl_0}\right)^\alpha
\exp[-\gamma\max(0,SST-T_0)^2]
\]

Los parámetros iniciales del documento de ecuaciones son provisionales y deben recalibrarse con el panel peruano real.

### 9.3 Dinámica de biomasa

La versión dinámica usa una ecuación tipo Schaefer:

\[
\frac{dB}{dt} = rB\left(1-\frac{B}{K}\right)-C_t
\]

donde (B) es biomasa, (K) es capacidad ambiental y (C_t) es captura. Esta ecuación no debe ajustarse hasta resolver la diferencia entre biomasa observada y desembarques.

## 10. Experimento C: cadena trófica

El Experimento C representa tres estados:

```text
F = fitoplancton
Z = zooplancton
A = anchoveta
```

El sistema estima los cambios de cada estado mediante consumo, crecimiento y mortalidad:

\[
\frac{dF}{dt},\quad \frac{dZ}{dt},\quad \frac{dA}{dt}
\]

Su principal dificultad es que el zooplancton no cuenta actualmente con una serie histórica mensual homogénea. Por ello C se considera una fase exploratoria y no debe presentarse como calibrado hasta disponer de observaciones o de un modelo de observación explícito.

También es necesario adaptar las ecuaciones, que están expresadas a escala diaria, a la resolución mensual de la mayoría de los datos disponibles.

## 11. Ajuste y validación

Cada experimento debe evaluarse contra una línea base y con separación temporal, no con una partición aleatoria que mezcle pasado y futuro.

### 11.1 Esquema recomendado

1. Entrenamiento en los primeros años.
2. Validación en años posteriores.
3. Prueba final en el último bloque temporal disponible.
4. Repetición con ventanas móviles o validación temporal progresiva.

### 11.2 Métricas

- RMSE y MAE para biomasa o captura;
- deviance explicada y AIC para modelos Tweedie;
- correlación temporal;
- sesgo medio;
- cobertura de intervalos de predicción;
- error separado por región, estación y fuente de respuesta.

### 11.3 Controles de sensibilidad

Se deben comparar:

- biomasa frente a desembarques como respuesta;
- con y sin años Bouchon;
- con y sin variables de manejo;
- clorofila CMEMS frente a OC-CCI;
- nutrientes CMEMS frente a WOA23;
- distintas cajas espaciales;
- distintos rezagos ambientales.

## 12. Estado actual y limitaciones

- Las biomasas acústicas y de cruceros ya están disponibles, pero son irregulares y combinan biomasa desovante y total.
- Los desembarques mensuales están disponibles, pero no equivalen a biomasa.
- CMEMS cubre las principales variables físicas y biogeoquímicas para 1998–2026-08.
- ERA5 ya contiene viento, pero todavía hay que calcular el índice de afloramiento.
- La clorofila OC-CCI está descargada como fuente satelital independiente.
- Kd490 aún no está descargado.
- PAR y POC NASA descargados son compuestos acumulados; faltan sus versiones mensuales.
- WOA23 es climatología y no aporta variabilidad interanual.
- El panel `data/processed/tables/panel_peru_monthly.csv` es sintético y solo sirve para probar el pipeline.
- La implementación actual de B es un placeholder estadístico; aún no es el modelo dinámico completo.
- Zooplancton, oxiclina y capa de mezcla siguen sin una serie observacional mensual integrada.

## 13. Reproducibilidad

Preparar el entorno:

```bash
uv sync
source .venv/bin/activate
```

Comprobar dependencias y credenciales:

```bash
python scripts/00_check_sources.py
```

Descargar las fuentes generales:

```bash
python scripts/01_download_data.py \
  --source copernicus noaa nsidc \
  --start 1998-01-01 \
  --end 2026-08-01
```

Descargar las fuentes del Experimento B:

```bash
python scripts/02_download_experiment_b.py \
  --start 1998-01-01 \
  --end 2026-08-01
```

Construir un panel real requiere proporcionar una tabla mensual integrada a:

```bash
python scripts/05_build_monthly_dataset.py \
  --input data/processed/tables/panel_real.csv \
  --output data/processed/tables/panel_peru_monthly_real.csv
```

El modo sintético se reserva para verificar que el código funciona:

```bash
python scripts/05_build_monthly_dataset.py --demo
```

No se deben ejecutar los ajustes científicos usando el panel generado con `--demo`.

## 14. Referencias de datos principales

- [CMEMS Global Multi-year Physics](https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_001_030/services)
- [CMEMS Global Multi-year Biogeochemistry](https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_BGC_001_029/description)
- [NOAA World Ocean Atlas 2023](https://www.ncei.noaa.gov/access/world-ocean-atlas-2023/)
- [NOAA PSL PDO](https://psl.noaa.gov/data/timeseries/month/PDO/)
- [NASA Ocean Color Level-3](https://oceandata.sci.gsfc.nasa.gov/l3/)
- [NASA CDS API / ERA5](https://cds.climate.copernicus.eu/how-to-api)
- [NSIDC Sea Ice Index](https://nsidc.org/data/g02135)
- [OC-CCI en OceanWatch ERDDAP](https://oceanwatch.pifsc.noaa.gov/erddap/info/esa-cci-chla-monthly-v6-0/index.html)


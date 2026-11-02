# Reporte de generación de datos, predicción y ampliación Perú–Chile

Fecha: 2 de noviembre de 2026  
Proyecto: Monitor de condiciones oceanográficas, productividad y anchoveta

## 1. Resumen ejecutivo

Se generó una primera cadena reproducible para el monitor:

```text
datos ambientales
    → paneles A, B y C
    → biomasa mensual interpolada para visualización
    → modelos A, B y C
    → escenarios de El Niño a 3 o 6 meses
```

La salida actual cubre el mar peruano y termina en agosto de 2026. La fase de escenarios genera septiembre de 2026 a febrero de 2027, con tres intensidades de El Niño.

También es viable ampliar el mapa de fitoplancton desde Perú hasta Chile. La opción recomendada es usar una fuente satelital global de color del océano para la visualización espacial y conservar CMEMS como fuente de reanálisis para variables ambientales y productividad modelada.

## 2. Datos y paneles generados

### 2.1 Panel A

El Experimento A usa temperatura, salinidad, oxígeno y un índice climático. Se ajustaron dos variantes independientes:

```text
A-ICEN
A-Niño 1+2
```

Para el monitor, la respuesta es `biomass_total_t_interpolated`. La serie conserva `biomass_value_type` para distinguir:

```text
observed      medición durante un crucero
interpolated  valor estimado entre cruceros
missing       sin valor disponible
```

La interpolación se usa porque el objetivo es un monitor, no una estimación científica publicada. Aun así, la interfaz debe mostrar la calidad del dato.

Archivo principal:

- `data/processed/models/experiment_a_monitor.json`
- `data/processed/tables/experiment_a_monitor_predictions.csv`

### 2.2 Panel B

Se compararon cuatro modelos:

| Variante | Variables añadidas | RMSE de validación |
|---|---|---:|
| B0 | SST, SSS, oxígeno | 3,379,931 t |
| B1 | B0 + clorofila-a | 2,093,508 t |
| B2 | B0 + carbono fitoplanctónico | 3,324,172 t |
| B3 | B0 + clorofila, carbono, nitrato y fosfato | 1,503,102 t |

B3 es la mejor variante en esta primera evaluación temporal. El resultado debe interpretarse como desempeño del monitor porque la respuesta contiene interpolación.

Archivo:

- `data/processed/models/experiment_b_monitor.json`

### 2.3 Panel C

El Experimento C usa:

```text
F = carbono fitoplanctónico
Z = zooplancton
A = biomasa de anchoveta
```

La calibración dinámica se realizó con diferencias mensuales y estados normalizados. Se obtuvieron ajustes exploratorios para entrenamiento, validación y prueba.

Limitación importante: F está en `mg C/m³`, mientras que Z está en `mg C/m²`. Por ello los parámetros de C sirven para simulación del monitor, pero no deben interpretarse como tasas biológicas comparables hasta definir una profundidad efectiva común.

Archivo:

- `data/processed/models/experiment_c_monitor.json`

## 3. Generación de escenarios de El Niño

Se generaron 18 registros:

```text
3 escenarios × 6 meses
septiembre de 2026 – febrero de 2027
```

Los escenarios son:

| Escenario | Multiplicador de la trayectoria central |
|---|---:|
| Débil | 0,70 |
| Central | 1,00 |
| Intenso | 1,20 |

La trayectoria central de ICEN utilizada fue:

```text
3,8 · 4,0 · 3,7 · 3,2 · 2,8 · 2,3
```

Para cada mes futuro:

1. Se toma la climatología mensual histórica.
2. Se ajustan las variables según su relación histórica con ICEN.
3. Se calculan A-ICEN, A-Niño 1+2 y B3.
4. Se simula C con los parámetros F-Z-A calibrados.
5. Se marca la fila como `scenario_not_observation`.

Archivos:

- `data/processed/tables/enso_scenarios_monitor.csv`
- `data/processed/models/enso_scenarios_monitor.json`
- `scripts/16_generate_enso_scenarios.py`

Estos escenarios deben actualizarse cuando se disponga de un nuevo pronóstico operativo de ICEN o Niño 1+2. No son observaciones futuras ni sustituyen una descarga actualizada.

## 4. Ampliación de clorofila-a hasta Chile

### 4.1 ¿Es posible?

Sí. Los productos de color del océano tienen cobertura global, por lo que no existe una limitación fundamental para incluir la costa peruana y chilena en el mismo mapa.

La ampliación recomendada para una visualización de fitoplancton es:

```text
longitud: -85° a -66°
latitud:  -56° a -3°
```

Para evitar mezclar regiones con dinámicas muy distintas, conviene dividir la vista en:

```text
Humboldt norte:   3°S–18°S   Perú
Humboldt centro: 18°S–42°S   norte y centro de Chile
Patagonia:       42°S–56°S   sur de Chile
```

La visualización puede mostrar toda la caja, pero los resúmenes y estadísticas deben calcularse por subregión.

### 4.2 Fuente recomendada para el mapa principal: ESA OC-CCI v6

OC-CCI combina observaciones de varios sensores y proporciona una serie mensual global de clorofila-a desde aproximadamente 1997. La versión v6 incluye clorofila, Kd490, incertidumbres y variables de control de observación. Tiene acceso mediante ERDDAP, THREDDS y otros servicios. [ESA Ocean Colour CCI](https://www.oceancolour.org/faq), [catálogo ERDDAP OC-CCI v6](https://comet.nefsc.noaa.gov/erddap/griddap/occci_V6_monthly_4km.html)

Ventajas:

- una misma fuente para Perú y Chile;
- serie histórica larga;
- resolución aproximada de 4 km en el producto mensual global;
- adecuada para anomalías, tendencias y mapas regionales;
- posibilidad de conservar incertidumbre y número de observaciones.

Recomendación: usar `chlor_a` en mg/m³, representar la escala en logaritmo y enmascarar celdas con baja cobertura.

### 4.3 Fuente alternativa: MODIS-Aqua mensual

El producto MODIS-Aqua de NASA distribuido por OceanWatch tiene cobertura global y datos mensuales desde 2002, con resolución cercana a 4–5 km. [NOAA OceanWatch MODIS-Aqua](https://oceanwatch.pifsc.noaa.gov/erddap/griddap/OceanWatch_aqua_chla_monthly.html), [NASA MODIS chlorophyll-a](https://modis.gsfc.nasa.gov/data/dataprod/chlor_a.php)

Es una buena alternativa para:

- comprobar que la señal de OC-CCI no es un artefacto de una única combinación de sensores;
- mostrar datos recientes;
- comparar la costa peruana con Chile usando un producto satelital homogéneo.

No se debe concatenar directamente con OC-CCI sin documentar la diferencia de algoritmo y realizar una comparación de solapamiento.

### 4.4 Fuente de reanálisis: Copernicus Marine BGC

El producto global `GLOBAL_MULTIYEAR_BGC_001_029` cubre globalmente desde 1993, tiene resolución de 0,25° y ofrece campos mensuales de clorofila, nitrato, fosfato, oxígeno y carbono fitoplanctónico. Es un producto de modelo sin asimilación de datos en esta configuración. [Copernicus Global Ocean Biogeochemistry Hindcast](https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_BGC_001_029/description)

Es la mejor fuente para extender el panel B y aportar variables que el satélite no observa directamente. No debe etiquetarse como observación satelital en la interfaz.

La recomendación es mostrar dos capas separadas:

```text
Clorofila satelital: OC-CCI o MODIS-Aqua
Productividad modelada: CMEMS BGC
```

### 4.5 Fuente para datos recientes

Copernicus también mantiene productos globales de análisis y pronóstico biogeoquímico, y productos de observación de color del océano. El producto de análisis/pronóstico global es útil para actualizar los meses recientes, mientras que la serie multianual se usa para el histórico. [Catálogo de productos Copernicus Marine](https://data.marine.copernicus.eu/products), [Global Ocean Colour Plankton monthly observations](https://data.marine.copernicus.eu/product/OCEANCOLOUR_GLO_BGC_L4_MY_009_108/description)

## 5. Limitaciones de la expansión Perú–Chile

La expansión geográfica es técnicamente viable, pero hay que controlar:

1. **Nubes y huecos:** la clorofila satelital no tiene cobertura uniforme todos los meses.
2. **Aguas costeras turbias:** sedimentos, descargas y materia orgánica pueden afectar la recuperación de clorofila.
3. **Fiordos chilenos:** la resolución de 4 km puede mezclar tierra, agua costera y canales estrechos.
4. **Floraciones algales:** clorofila alta no significa necesariamente toxicidad.
5. **Comparabilidad:** OC-CCI, MODIS y CMEMS no son la misma medición.
6. **Escala:** la caja amplia sirve para mapas, pero las estadísticas deben calcularse por regiones o celdas.

El monitor debe mostrar fecha, producto, resolución y porcentaje de celdas válidas. La concentración de clorofila debe representarse con escala logarítmica, porque su rango dinámico es amplio.

## 6. Cambios necesarios en el pipeline

El código actual está centrado en `PERU_OCEAN`:

```text
longitud: -85 a -70
latitud:  -18.35 a -3.38
```

Para ampliar la visualización se necesita:

1. Definir un `SOUTH_AMERICA_HUMBOLDT` en `src/nasahackaton/config.py`.
2. Añadir una opción `--region` o `--bbox` a los scripts de descarga.
3. Descargar OC-CCI o MODIS para la caja ampliada.
4. Mantener el recorte espacial en NetCDF antes de construir el JSON.
5. Extender `monitoring_grid_chlorophyll.json` para que incluya la nueva caja.
6. Añadir `region` y `product` a cada registro o metadato de la grilla.
7. Calcular medianas por subregión, no solo una mediana para todo Perú–Chile.
8. Mantener CMEMS separado de la capa satelital.

No es necesario cambiar las ecuaciones A, B o C para dibujar la clorofila de Chile. Sí sería necesario recalibrarlas si se quisiera interpretar la costa Perú–Chile como una única población o respuesta de anchoveta.

## 7. Recomendación final

Para la siguiente implementación:

1. Usar **OC-CCI v6 mensual** como capa satelital principal Perú–Chile.
2. Usar **CMEMS BGC** para carbono fitoplanctónico, nutrientes y oxígeno modelados.
3. Usar **MODIS-Aqua** como control independiente, no como concatenación automática.
4. Dividir el mapa en Perú, Chile centro y Patagonia.
5. Exponer en la interfaz el tipo de dato: `satellite_observation`, `model_reanalysis` o `scenario`.
6. Mantener los escenarios de El Niño separados de los datos observados.

La ampliación está respaldada por la cobertura global de los productos. El principal trabajo pendiente no es encontrar datos, sino parametrizar la caja, descargar una grilla espacial mayor y conservar correctamente la procedencia y calidad de cada capa.

# Reporte de avance: Experimentos A y B

## 1. Alcance

Se construyó el flujo de datos real para los experimentos A y B del proyecto de monitoreo de la anchoveta peruana (*Engraulis ringens*). El objetivo de esta etapa fue organizar las fuentes ambientales y biológicas en una serie temporal reproducible, sin confundir datos observados con valores interpolados o simulados.

El Experimento C —cadena fitoplancton–zooplancton–anchoveta— queda fuera de esta etapa porque todavía no existe una serie histórica mensual homogénea de zooplancton.

El periodo operativo utilizado es enero de 1998 a agosto de 2026, limitado por la cobertura común de los productos ambientales de CMEMS.

## 2. Fuentes integradas

### Variables ambientales

Se procesaron archivos CMEMS correspondientes a:

- temperatura superficial del mar (sst);
- salinidad superficial (sss);
- oxígeno disuelto;
- nitrato y fosfato;
- clorofila-a;
- carbono fitoplanctónico.

También se incorporaron:

- clorofila-a independiente de OC-CCI;
- Kd490;
- PDO mensual de NOAA;
- ICEN mensual del IGP/ENFEN;
- anomalía mensual de Niño 1+2.

El ICEN se descargó desde el archivo oficial enlazado por el IGP y se normalizó mediante [03_download_icen_igp.py](../scripts/03_download_icen_igp.py). La serie original y la tabla de eventos costeros se conservaron en data/raw/igp/.

Niño 1+2 e ICEN se mantienen como variables separadas. No se deben introducir simultáneamente en un mismo modelo sin evaluar antes la colinealidad.

### Biomasa de anchoveta

Se utilizó la tabla de biomasa total por crucero de IMARPE, conservando únicamente registros con fecha de inicio y fecha de fin disponibles. Cada crucero se trata como una observación por intervalo, no como una observación mensual independiente.

Para cada intervalo se calcularon estadísticas ambientales ponderadas por los días de cobertura del crucero. Así, una campaña de febrero-marzo utiliza las condiciones ambientales de esa ventana y no el valor de un único mes arbitrario.

El procesamiento actual contiene:

- 9 cruceros con fechas completas;
- 23 meses cubiertos por intervalos de biomasa;
- 321 meses sin biomasa observada.

Las campañas con biomasa pero sin fechas completas no se interpolaron ni se incluyeron en el panel de ajuste.

## 3. Conversión de unidades y control de calidad

Se corrigieron unidades importantes antes de construir las salidas:

- oxígeno CMEMS: de mmol/m³ a ml/L;
- carbono fitoplanctónico CMEMS: de mmol C/m³ a mg C/m³;
- distancia costera: prevista en millas náuticas cuando exista cobertura.

Los productos ambientales se agregaron espacialmente mediante la mediana de la caja peruana y temporalmente a escala mensual. Los valores faltantes no se reemplazaron silenciosamente.

El reporte de cobertura se guarda en:

[panel_quality_report.csv](../data/processed/tables/panel_quality_report.csv)

## 4. Tratamiento de la distancia a la costa

Se verificó el paquete GSHHG en data/gshhg/GSHHS_shp/. Los archivos GSHHS_i_L1 y GSHHS_h_L1 son polígonos de masas continentales e islas en WGS84 y son adecuados para calcular distancia a la costa.

Además, se incorporó:

data/gshhg/distancia_costa_celdas.csv

Este archivo contiene 452 celdas con distancia en kilómetros y millas náuticas. Su cobertura peruana es regional —Paita-Sechura, Chimbote, Callao, Pisco e Ilo— y no cubre toda la caja ambiental del mar peruano.

Por esa razón, distance_coast permanece como null en el panel general cuando no existe una correspondencia espacial segura. No se extrapolaron valores para completar artificialmente la caja.

## 5. Salidas producidas

El procesamiento se encuentra en:

[04_build_real_panel.py](../scripts/04_build_real_panel.py)

### Panel por intervalos

[panel_experiments_ab.csv](../data/processed/tables/panel_experiments_ab.csv)

Contiene una fila por crucero y las condiciones ambientales resumidas durante el intervalo:

~~~text
crucero
fecha_inicio
fecha_fin
interval_days
biomass_anchoveta
sst
sss
oxygen
chlorophyll_a
nitrate
phosphate
phytoplankton_carbon
pdo
icen
nino12
~~~

Este es el archivo apropiado para futuros ajustes por intervalos.

### Serie mensual para monitoreo

[monitoring_series_ab.json](../data/processed/tables/monitoring_series_ab.json)

Es la salida recomendada para la página. Contiene metadatos, fuentes, periodo y una lista de registros mensuales. Los valores faltantes se representan como null.

También existe la versión tabular:

[monitoring_series_ab.csv](../data/processed/tables/monitoring_series_ab.csv)

## 6. Interpolación para visualización

Se generó una versión adicional con interpolación lineal únicamente para mostrar una trayectoria continua en la página:

- [monitoring_series_ab_interpolated.json](../data/processed/tables/monitoring_series_ab_interpolated.json)
- [monitoring_series_ab_interpolated.csv](../data/processed/tables/monitoring_series_ab_interpolated.csv)

La serie interpolada contiene:

- 23 meses observados;
- 257 meses interpolados;
- 64 meses sin valor.

Cada registro incluye:

~~~text
biomass_total_t
biomass_total_t_interpolated
biomass_value_type
biomass_interpolation_method
~~~

Los tipos posibles son:

~~~text
observed
interpolated
missing
~~~

La interpolación solo se aplica entre observaciones reales. No se extrapola antes del primer crucero ni después del último. Esta serie es válida para visualización y monitoreo exploratorio, pero no para ajustar los modelos A/B como si todos sus valores fueran observaciones.

## 7. Estado de los experimentos

### Experimento A: línea base abiótica

La estructura de datos necesaria está preparada con:

- SST;
- salinidad;
- oxígeno;
- ICEN;
- Niño 1+2;
- distancia costera parcial.

Todavía no se puede considerar final el ajuste estadístico porque:

1. solo existen 9 intervalos de biomasa con fechas completas;
2. la distancia costera no cubre toda la región;
3. el código histórico aún utiliza nombres de variables heredados como oni;
4. el GAM Tweedie final todavía no está implementado.

Por lo tanto, los resultados actuales deben interpretarse como preparación de datos y no como una estimación científica definitiva de los efectos ambientales.

### Experimento B: productividad

Se incorporaron:

- clorofila-a;
- Kd490;
- nitrato;
- fosfato;
- carbono fitoplanctónico;
- componentes de idoneidad para clorofila.

También se calcularon los componentes de los índices HSI abiótico y trófico. Los HSI completos quedan como null cuando falta distancia costera.

El archivo existente de Experimento B todavía funciona como placeholder del ajuste de A. Aún debe implementarse un modelo B real con las variables de productividad y validación temporal.

## 8. Conclusión

La etapa de integración y preparación de datos para A y B está completa. Existe ahora una salida mensual reproducible para monitoreo, una tabla por intervalos para análisis de biomasa y una versión interpolada separada para visualización.

El siguiente paso científico es implementar el ajuste de A usando una variante climática por vez —ICEN o Niño 1+2— y después comparar B incorporando productividad. La biomasa interpolada no debe reemplazar a la biomasa observada durante esa comparación.

# Reporte de sesión: estado de los datos y capacidad para evaluar H1/H0

**Proyecto:** ANCHOVETA 360  
**Fecha:** 6 de noviembre de 2026  
**Alcance:** revisión del repositorio, verificación de los datos antárticos disponibles, revisión del análisis estadístico en R y comprobación del archivo hidroacústico corregido.

> **Nota de corrección (8 de noviembre de 2026):** el valor `p = 0.114958` citado en este reporte comparaba M0 con CAR(1) contra M1 sin correlación, por lo que el contraste no era válido. Con la misma estructura en ambos modelos el resultado es `p = 0.289` (IID); la conclusión (no rechazar H0) no cambia. Ver `analysis_r/README.md` y `docs/informe_analisis_exploratorio_h1_h0.md`.

## 1. Resumen ejecutivo

Durante esta sesión se verificó qué información existe actualmente en el repositorio para estudiar la cadena:

```text
océano Austral → Pacífico Sur → sistema de Humboldt → hábitat de anchoveta
```

La conclusión principal es que el proyecto sí cuenta con una base ambiental suficiente para comenzar análisis estadísticos reproducibles, pero la representación antártica todavía es parcial. Actualmente se dispone de:

- extensión diaria del hielo marino antártico;
- índice mensual AAO/SAM;
- climatologías World Ocean Atlas 2023;
- un panel mensual peruano con variables físicas, biogeoquímicas y climáticas;
- biomasa evaluada anual de RAM Legacy;
- series históricas de biomasa desovante;
- datos de desembarques, cuotas y temporadas;
- un archivo hidroacústico corregido con 70 registros únicos entre 1985 y 2017.

La primera prueba estadística en R utilizó la biomasa evaluada `tb.data` del stock norte-centro peruano `PANCHPERUNC`, junto con hielo antártico y AAO/SAM rezagados un año. Con 17 años completos, el contraste del bloque antártico produjo `p = 0.114958`; por tanto, no se rechazó H0 al 5 %. Este resultado no demuestra ausencia de relación ni permite rechazar H1 general, porque la prueba no incluyó todavía SST antártica espacial, ACC, AAIW, circulación subsuperficial ni conectividad explícita del Pacífico Sur.

## 2. Actividades realizadas

### 2.1 Revisión del repositorio y del flujo de datos

Se revisaron los scripts Python, los scripts R, los paneles procesados y los archivos brutos. El flujo actual combina:

1. Descarga y preparación ambiental mediante Python.
2. Construcción de paneles mensuales y paneles de campañas.
3. Descarga y preparación de información de RAM Legacy mediante R.
4. Construcción de un panel anual común.
5. Comparación de un modelo local con un modelo que añade indicadores antárticos.

El repositorio ya diferencia entre observaciones, productos modelados, interpolaciones y simulaciones. Esta separación debe mantenerse en todos los análisis posteriores.

### 2.2 Verificación del análisis en R

El pipeline reproducible se encuentra en:

```text
analysis_r/00_install_packages.R
analysis_r/01_download_datasets.R
analysis_r/02_build_annual_panel.R
analysis_r/03_fit_hypothesis.R
```

La respuesta utilizada fue la biomasa total evaluada (`tb.data`) del stock `PANCHPERUNC` en RAM Legacy v4.44. La intersección con el ambiente disponible cubre 1998–2015; aunque existen 18 años comunes, solo 17 quedaron completos para el ajuste final.

El contraste comparó:

```text
M0 = ambiente local + ENSO + PDO + tendencia
M1 = M0 + hielo antártico rezagado 1 año + AAO/SAM rezagado 1 año
```

Resultado principal:

```text
p del bloque antártico = 0.114958
decisión = no rechazar H0 al 5 %
```

La estimación con estructura temporal CAR(1) no convergió de forma estable con solo 17 observaciones. El pipeline dejó registrada la contingencia y utilizó GLS sin correlación temporal para el contraste final. Por ello, el resultado debe considerarse exploratorio y sujeto a validación con una respuesta biológica más directamente observada.

## 3. Qué información antártica existe actualmente

### 3.1 Datos que sí están disponibles

#### Extensión del hielo marino antártico

Archivo principal:

```text
data/raw/nsidc/S_seaice_extent_daily_v4.0.csv
analysis_r/data/raw/S_seaice_extent_daily_v4.0.csv
```

Es una serie temporal diaria de extensión total. Permite calcular medias, anomalías y rezagos anuales o mensuales. No permite, por sí sola, estudiar la distribución espacial del hielo ni identificar qué sector antártico está relacionado con el Pacífico Sur peruano.

#### AAO/SAM

Archivo utilizado por R:

```text
analysis_r/data/raw/aao_cpc_monthly.csv
```

Es un índice climático mensual que resume parte de la variabilidad atmosférica de altas latitudes australes. Es útil como covariable climática, pero no es una observación directa de transporte oceánico ni de la Corriente Circumpolar Antártica.

#### Climatologías WOA23

Los archivos se encuentran en:

```text
data/raw/woa23/
```

Contienen climatologías de temperatura, salinidad, oxígeno y nutrientes. Son útiles para caracterizar masas de agua, construir referencias climatológicas y definir anomalías, pero no representan por sí mismas la variabilidad interanual mensual de 1998–2025.

### 3.2 Datos que no están disponibles de forma suficiente

La inspección de los archivos CMEMS y ERA5 confirmó que los productos principales descargados están recortados al dominio peruano aproximado:

```text
longitud: -85 a -70 °O
latitud: -18.35 a -3.38 °S
```

Por tanto, actualmente no existe en el repositorio una representación espacial completa de:

- SST antártica;
- concentración espacial de hielo marino;
- corrientes superficiales o subsuperficiales del ACC;
- altura dinámica o SSH antártica y del Pacífico Sur;
- temperatura y salinidad subsuperficiales en la ruta Antártida–Pacífico Sur;
- indicadores directos de AAIW;
- oxígeno y nutrientes subsuperficiales antárticos;
- conectividad mediante trayectorias, transporte o advección.

En consecuencia, el repositorio permite una hipótesis antártica reducida basada en índices, pero todavía no permite evaluar de manera completa la hipótesis mecanística de conectividad oceanográfica.

## 4. Datos del Perú y del sistema de Humboldt

El panel ambiental procesado contiene 344 meses y presenta cobertura completa para las variables principales:

- SST;
- salinidad;
- clorofila-a;
- nitrato;
- fosfato;
- oxígeno;
- carbono fitoplanctónico;
- clorofila OC-CCI;
- Kd490;
- ICEN;
- PDO;
- Niño 1+2, con una ausencia puntual.

Estos datos son adecuados para estudiar la relación local entre ambiente y hábitat, especialmente en los experimentos A y B. No todos son observaciones directas: varios campos proceden de reanálisis, hindcasts, productos satelitales o modelos de circulación y biogeoquímica. Esta procedencia debe conservarse como metadato.

El panel actual todavía tiene limitaciones para algunas variables necesarias para una interpretación ecológica completa:

- `ONI` no tiene cobertura en el panel de calidad actual;
- distancia a la costa no está disponible en el panel final;
- no existe todavía un campo observado continuo de profundidad de oxiclina;
- la surgencia costera debe derivarse o validarse con viento y transporte de Ekman;
- no se debe interpretar una salida de modelo como una medición biológica.

## 5. Verificación del CSV hidroacústico corregido

Archivo:

```text
analysis_r/data/raw/Cruceros_hidroacusticos_1985_2017.csv
```

La revisión actual encontró:

- 70 filas de datos;
- 70 identificadores de crucero únicos;
- encabezados consistentes;
- ningún valor faltante en las cinco columnas;
- variables explícitamente nombradas como biomasa en miles de toneladas y áreas en millas náuticas cuadradas;
- cobertura nominal 1985–2017, según el nombre y la codificación de las campañas;
- aproximadamente 50 campañas en el periodo 1998–2017.

Las variables son:

```text
N°
Crucero
Biomasa_miles_t
Area_distribucion_nm2
Area_evaluada_nm2
```

La corrección cambia favorablemente el panorama: el archivo ya puede considerarse una fuente de biomasa hidroacústica por campaña para un análisis exploratorio. Sin embargo, todavía no contiene:

- fecha completa de inicio y fin para cada crucero;
- coordenadas o transectos;
- valores NASC por estación o transecto;
- profundidad de observación;
- identificación explícita del stock en cada fila;
- información suficiente para distinguir con seguridad todas las coberturas geográficas.

Los códigos de crucero son irregulares (`8503-05`, `9011-9101`, `9704`, `0912`, `2001-02`, entre otros). No deben convertirse automáticamente a fechas sin una tabla de equivalencias documentada en la fuente original. La siguiente etapa debe crear un diccionario de campañas y confirmar unidades, región, stock y fechas.

## 6. Qué puede afirmarse respecto de H1 y H0

### 6.1 Sobre la hipótesis general H1

Los datos actuales permiten evaluar parcialmente H1 en tres niveles:

1. **Asociación climática antártica–Perú.** Puede probarse con hielo marino y AAO/SAM frente a variables peruanas, usando correlaciones, rezagos y modelos temporales.
2. **Asociación ambiente local–anchoveta.** Puede probarse con el panel peruano y los cruceros hidroacústicos, después de armonizar campañas.
3. **Cadena de conectividad física completa.** Todavía no puede probarse de forma robusta porque faltan campos espaciales antárticos y del Pacífico Sur, circulación subsuperficial, AAIW y una métrica de transporte o conectividad.

Por ello, H1 puede mantenerse como hipótesis de investigación, pero debe formularse operacionalmente por etapas. La primera corrida no constituye una prueba completa de H1 general.

### 6.2 Sobre la hipótesis nula H0

La primera prueba no rechazó H0 para el bloque formado por hielo antártico y AAO/SAM, condicionada a los controles utilizados y al periodo de 17 años completos. La conclusión correcta es:

> No se obtuvo evidencia estadística suficiente para rechazar H0 en esta especificación inicial.

No es correcto concluir que H0 quedó demostrada. La falta de significancia puede deberse, entre otras causas, a:

- tamaño muestral pequeño;
- respuesta anual evaluada y no observación acústica primaria;
- resolución espacial limitada;
- ausencia de SST antártica, ACC, AAIW y variables subsuperficiales;
- colinealidad entre índices climáticos;
- rezago elegido de un año;
- incertidumbre de la evaluación de stock;
- falta de una estructura espacial explícita.

## 7. Capacidad actual para los tres experimentos

### Experimento A: modelo oceanográfico local

Es viable actualmente. Puede utilizar SST, salinidad, oxígeno, viento o proxies de surgencia y, cuando se incorpore el archivo hidroacústico, biomasa por campaña. Debe utilizar pocos predictores preseleccionados debido al número efectivo de campañas.

### Experimento B: modelo de productividad

También es viable a nivel exploratorio. Puede incorporar clorofila, Kd490, carbono fitoplanctónico, nitrato, fosfato, oxígeno y variables de estructura del agua. La respuesta hidroacústica debe modelarse por campaña y no rellenarse artificialmente como biomasa mensual observada.

### Experimento C: conectividad antártica

Es viable solo en su versión reducida con extensión de hielo y SAM/AAO. Para convertirlo en un modelo de conectividad completo es necesario descargar datos globales o regionales de temperatura, salinidad, corrientes, SSH, biogeoquímica y hielo espacial, y luego construir índices por regiones antárticas y del Pacífico Sur.

## 8. Datos adicionales necesarios

Para evaluar la versión completa de H1 se recomienda incorporar, en este orden:

1. **CMEMS global o regional:** temperatura, salinidad, corrientes, SSH y profundidad suficiente para estudiar la capa superior y AAIW entre 1998 y 2025.
2. **CMEMS biogeoquímico global o regional:** oxígeno, nutrientes, clorofila y producción primaria fuera del dominio peruano.
3. **NSIDC espacial:** concentración de hielo marino, no solamente extensión total.
4. **OSCAR u otro producto de corrientes superficiales:** validación de patrones superficiales y transporte.
5. **Argo, EN4 o CORA:** validación independiente de temperatura y salinidad subsuperficiales.
6. **OC-CCI global:** clorofila comparable entre Antártida, Pacífico Sur y Humboldt.
7. **Metadatos IMARPE:** fechas, regiones, stocks, transectos y metodología de los cruceros hidroacústicos.

Las regiones preliminares recomendadas son:

- Península Antártica: 60–75°S, 75–55°O;
- mar de Bellingshausen: 65–75°S, 105–70°O;
- Pacífico Sur intermedio: 45–55°S, 130–75°O;
- Pacífico Sur subtropical: 35–50°S, 120–75°O;
- transición hacia Humboldt: 20–35°S, 110–75°O;
- cajas costeras peruanas definidas según las áreas reales de los cruceros.

Estas regiones deben usarse para construir índices regionales y analizar rezagos; no debe suponerse que el ACC se convierte directamente en la Corriente de Humboldt.

## 9. Recomendación metodológica inmediata

La siguiente fase debería seguir este orden:

1. Crear un diccionario de campañas del CSV hidroacústico.
2. Confirmar fechas, región, stock y unidades con la fuente original.
3. Construir un panel por campaña con promedios ambientales calculados dentro de la ventana del crucero.
4. Mantener separadas las respuestas RAM, biomasa desovante, biomasa hidroacústica y desembarques.
5. Ajustar primero modelos GAM/GAMM reducidos para Experimentos A y B.
6. Ampliar el Experimento C con datasets antárticos espaciales.
7. Evaluar los efectos antárticos como bloque incremental sobre el modelo local y productivo.
8. Usar validación temporal, diagnósticos de autocorrelación y análisis de sensibilidad a rezagos de 0, 3, 6, 12, 18 y 24 meses.

Para inferencia científica se recomienda un GAMM o un modelo jerárquico con efectos de campaña, región y año cuando los metadatos estén completos. Para predicción se puede comparar XGBoost, pero sus mejoras de desempeño no deben interpretarse como evidencia causal. SHAP puede utilizarse para interpretar la contribución predictiva de las variables.

## 10. Conclusión

El repositorio ya superó la etapa de disponibilidad meramente descriptiva. Existe suficiente información para comenzar un análisis estadístico de la relación entre ambiente local y anchoveta, y para realizar una prueba preliminar de índices antárticos frente a la biomasa evaluada.

La corrección del CSV hidroacústico es una mejora importante: 70 campañas únicas ofrecen una base biológica mucho más útil que el panel anterior de nueve cruceros con fechas completas. Aun así, la ausencia de coordenadas, fechas completas y metadatos de stock impide tratarlo todavía como un panel espacial plenamente armonizado.

La parte antártica disponible actualmente permite estudiar una señal climática agregada, no una conectividad oceanográfica completa. Por tanto, la situación científica actual es:

> **H1 permanece plausible y parcialmente evaluable; H0 no fue rechazada en la primera especificación anual, pero tampoco quedó demostrada. Para decidir con mayor fuerza entre ambas hipótesis se necesita ampliar la cobertura antártica y del Pacífico Sur, armonizar los cruceros hidroacústicos y evaluar la cadena física–ambiental–biológica con modelos jerárquicos y validación temporal.**

## 11. Archivos relevantes del repositorio

- [Reporte previo de capacidad de datos](../02_datos/reporte_capacidad_datos_investigacion.md)
- [Reporte del primer análisis estadístico en R](REPORTE_SESION_ANALISIS_ESTADISTICO_R.md)
- [CSV hidroacústico corregido](../../analysis_r/data/raw/Cruceros_hidroacusticos_1985_2017.csv)
- [Panel anual RAM](../../analysis_r/data/processed/annual_panel_ram44.csv)
- [Resultado del contraste de hipótesis](../../analysis_r/data/processed/hypothesis_test.csv)
- [Panel mensual de calidad](../../data/processed/tables/panel_quality_report.csv)
- [Manifiesto de paneles experimentales](../../data/processed/tables/experiment_panels_manifest.json)

# Reporte de transferencia: panel de conectividad listo para análisis

**Fecha de verificación:** 2026-11-07  
**Alcance:** cierre de la etapa de descarga, validación y agregación del panel oceanográfico para ANCHOVETA 360.

## 1. Resultado conseguido

Se completó el procesamiento local del pipeline de conectividad Antártida–Pacífico Sur–Humboldt. Los productos procesados fueron copiados desde el entorno de ejecución y están disponibles en:

```text
data/processed/tables/
```

Los cuatro archivos principales son:

| Archivo | Tamaño aproximado | Función |
|---|---:|---|
| `connectivity_panel_monthly.csv` | 3.06 MB | Panel mensual regional utilizado por el análisis estadístico |
| `connectivity_pipeline_report.md` | 5.8 KB | Informe automático de cobertura y limitaciones |
| `connectivity_file_inventory.json` | 8.8 KB | Inventario de archivos, tamaños y estado |
| `connectivity_quality_report.json` | 13.6 KB | Validación estructural de los NetCDF |

Estos archivos son suficientemente pequeños para continuar localmente. No es necesario mantener abierta la sesión de Google Colab para la fase estadística.

## 2. Validación conseguida

El informe de calidad registra:

- 18 archivos CMEMS esperados.
- 18 archivos válidos.
- 0 archivos faltantes.
- 0 archivos inválidos.
- 0 archivos heredados parciales.
- 6 regiones oceanográficas.
- 336 observaciones mensuales por región.
- Cobertura común desde enero de 1998 hasta diciembre de 2025.

Las regiones disponibles son:

```text
peninsula_antarctica
bellingshausen
south_pacific_intermediate
south_pacific_subtropical
transition_humboldt
peru_humboldt
```

El panel contiene, según la región y la banda de profundidad, variables de:

- temperatura (`thetao`);
- salinidad (`so`);
- corrientes zonales y meridionales (`uo`, `vo`);
- altura del nivel del mar (`zos`);
- profundidad de capa de mezcla (`mlotst`);
- clorofila (`chl`);
- nitrato (`no3`);
- fosfato (`po4`);
- oxígeno (`o2`);
- carbono fitoplanctónico (`phyc`);
- anomalías climatológicas de las variables disponibles.

El panel no contiene OSCAR. Esta ausencia es intencional: OSCAR es un producto diario global y su descarga masiva consumió el almacenamiento de Google Drive. El Experimento C puede continuar utilizando las corrientes mensuales `uo` y `vo` de CMEMS.

## 3. Qué significa este resultado científicamente

El panel permite evaluar asociaciones ambientales entre las seis regiones y estudiar si las señales oceanográficas de las regiones antárticas y del Pacífico Sur presentan relaciones temporales con la región de Humboldt.

Todavía no demuestra:

- transporte directo desde la Antártida hasta Perú;
- transformación directa de la Corriente Circumpolar Antártica en la Corriente de Humboldt;
- causalidad sobre la biomasa de anchoveta;
- conectividad lagrangiana o transporte integrado de masas de agua.

La conclusión científica seguirá siendo exploratoria y se basará en asociaciones, rezagos, estabilidad temporal y capacidad explicativa incremental.

## 4. Archivos que todavía hacen falta para probar la hipótesis

El panel ambiental no es suficiente por sí solo para decidir entre H0 y H1. Se necesita una variable de respuesta de anchoveta con una definición explícita.

La siguiente información debe revisarse antes de ajustar el modelo:

### 4.1 Respuesta biológica primaria

Archivo candidato principal:

```text
data/biomasa_cruceros.csv
```

Debe verificarse:

- número de campañas;
- fechas exactas;
- región o stock representado;
- unidades de biomasa;
- si el valor es biomasa total, biomasa desovante o NASC convertido;
- coordenadas o cobertura espacial;
- duplicados y campañas con definiciones diferentes.

Este archivo no debe convertirse artificialmente en una serie mensual completa. Si las observaciones son de campaña, el análisis debe trabajar a nivel de campaña o utilizar una agregación anual justificada.

### 4.2 Alternativa de respuesta anual

Existe un pipeline estadístico en:

```text
analysis_r/02_build_annual_panel.R
analysis_r/03_fit_hypothesis.R
```

Este pipeline utiliza una serie de biomasa evaluada de RAM Legacy y compara dos modelos GLS anidados. Es una alternativa para un análisis anual exploratorio, pero no debe confundirse con la biomasa acústica de campañas IMARPE. Antes de usarlo se debe identificar y documentar explícitamente el `stock_id` peruano correcto.

### 4.3 Variables de control

El análisis debe incorporar, cuando estén disponibles y con cobertura compatible:

- Niño 1+2 o ICEN;
- PDO;
- estacionalidad;
- tendencia temporal;
- viento costero o proxy de surgencia;
- esfuerzo, cuotas y vedas si se utilizan desembarques;
- una definición documentada de los rezagos.

No se deben mezclar desembarques, biomasa acústica y biomasa evaluada como si fueran la misma respuesta.

## 5. Hipótesis que debe probar el siguiente agente

La pregunta operacional es:

> ¿Los indicadores antárticos y del Pacífico Sur aportan capacidad explicativa adicional para la variabilidad de la respuesta de anchoveta después de controlar por las condiciones locales de Humboldt, productividad, ENSO, PDO, estacionalidad y tendencia?

### Hipótesis nula

```text
H0: el bloque antártico no aporta información explicativa adicional.
```

Formalmente, los coeficientes o funciones asociadas a los predictores antárticos son nulos una vez incluidos los controles del modelo base.

### Hipótesis alternativa

```text
H1: el bloque antártico aporta información explicativa adicional.
```

La evidencia a favor de H1 debe basarse conjuntamente en:

- mejora fuera de muestra;
- reducción de error predictivo;
- estabilidad temporal;
- tamaño y dirección de los efectos;
- intervalos de confianza;
- contraste del bloque antártico;
- coherencia con la estructura vertical y regional.

Un p-valor menor que 0.05 no debe interpretarse como prueba de causalidad.

## 6. Modelos que deben construirse

Los modelos son acumulativos.

### Modelo A — ambiente local

Respuesta de anchoveta explicada por variables de Humboldt:

```text
respuesta ~ SST + salinidad + oxígeno + corrientes + SSH + estacionalidad
```

### Modelo B — productividad

Añade productividad y biogeoquímica:

```text
Modelo A + clorofila + nutrientes + fitoplancton + estructura vertical
```

### Modelo C — conectividad antártica

Añade indicadores antárticos y del Pacífico Sur:

```text
Modelo B + variables antárticas + variables del Pacífico Sur + rezagos
```

Los indicadores antárticos deben resumirse por región y profundidad. Ejemplos iniciales:

- temperatura y salinidad entre 100–200 m y 500–1000 m;
- velocidad o componentes `uo`/`vo` en superficie y subsuperficie;
- anomalías de altura del nivel del mar;
- clorofila y nutrientes en la capa superior;
- extensión o concentración de hielo marino;
- SAM/AAO como índice climático, si está disponible.

Los rezagos iniciales serán 0, 3, 6, 12, 18 y 24 meses. No se debe seleccionar retrospectivamente solo el rezago con menor p-valor sin corrección por comparaciones múltiples.

## 7. Orden de trabajo recomendado

### Paso 1 — auditoría de la respuesta

Generar una tabla con fecha, región, stock, unidad, valor, fuente y tipo de biomasa. El informe debe indicar cuántas observaciones realmente pueden cruzarse con el panel ambiental.

### Paso 2 — construir el panel analítico

Unir la respuesta con `connectivity_panel_monthly.csv` mediante fecha, región y profundidad. Si la respuesta es de campaña, seleccionar el promedio ambiental de una ventana definida alrededor de la fecha de campaña; no interpolar la biomasa.

### Paso 3 — definir predictores antes de ajustar

Preseleccionar pocas variables por bloque para evitar sobreajuste. Documentar las transformaciones, unidades, anomalías, estandarización y rezagos.

### Paso 4 — ajustar A, B y C

Para inferencia se recomienda comenzar con un modelo estadístico interpretable, como GAM/GAMM o un modelo lineal mixto/GLS según el tamaño de muestra. XGBoost debe ser secundario y solo utilizarse si hay suficientes observaciones independientes para validación temporal.

### Paso 5 — validar temporalmente

Usar validación bloqueada por tiempo, diagnósticos de autocorrelación, sensibilidad a ventanas de rezago y análisis de observaciones influyentes. No hacer particiones aleatorias que mezclen pasado y futuro.

### Paso 6 — emitir la decisión

El informe final debe incluir:

- estimación de efectos;
- intervalos de confianza;
- p-valores ajustados cuando corresponda;
- métricas de validación;
- comparación A/B/C;
- limitaciones de la respuesta biológica;
- decisión “rechazar H0” o “no rechazar H0” bajo la especificación evaluada.

## 8. Entorno recomendado

La fase estadística debe ejecutarse localmente porque los archivos procesados son pequeños. Colab ya no es necesario para esta fase.

Colab solo debe utilizarse si se necesita:

- volver a procesar los NetCDF originales;
- reconstruir el panel con otra profundidad o región;
- descargar una fuente que aún no esté disponible localmente.

Para el pipeline Python local, el entorno virtual existente es:

```bash
data_treatment/.venv/bin/python
```

El Python del sistema no tiene `pandas`, por lo que este comando puede fallar:

```bash
python data_treatment/scripts/13_full_connectivity_pipeline.py --mode process
```

El equivalente correcto en este entorno es:

```bash
data_treatment/.venv/bin/python \
  data_treatment/scripts/13_full_connectivity_pipeline.py \
  --mode process \
  --skip-ice
```

Sin embargo, como el procesamiento ya fue completado, no es necesario repetirlo para iniciar el análisis estadístico.

## 9. Estado de cierre de esta etapa

Esta etapa puede marcarse como **completada**:

- descarga regional CMEMS: completada;
- validación estructural: completada;
- panel mensual regional: completado;
- cobertura 1998–2025: completa;
- OSCAR: excluido deliberadamente por costo de almacenamiento;
- datos listos para análisis estadístico: sí;
- contraste H0/H1: todavía pendiente;
- integración formal con respuesta de anchoveta: todavía pendiente.

El siguiente agente debe comenzar por auditar `data/biomasa_cruceros.csv` y elegir explícitamente la definición de respuesta antes de ajustar cualquier modelo.

# Informe de análisis exploratorio de la hipótesis ambiental antártica

## ANCHOVETA 360

**Respuesta biológica:** biomasa total observada por crucero IMARPE y biomasa evaluada anual RAM Legacy  
**Periodo ambiental principal:** 1998–2025  
**Periodo de cruceros con fechas completas:** 1998–2021  
**Fecha del análisis:** noviembre de 2026  

---

## 1. Introducción

### 1.1 Contexto

ANCHOVETA 360 busca estudiar si la variabilidad ambiental del océano Austral y del Pacífico Sur presenta asociaciones temporales con las condiciones ambientales del sistema de la Corriente de Humboldt y con la variabilidad de la anchoveta peruana (*Engraulis ringens*).

La hipótesis conceptual original proponía una posible cadena ambiental:

```text
Océano Austral → Pacífico Sur → transición hacia Humboldt → ambiente peruano → anchoveta
```

Sin embargo, los datos disponibles no permiten demostrar conectividad oceanográfica completa, transporte directo de masas de agua ni causalidad biológica. Por esta razón, el presente informe evalúa una versión exploratoria y más limitada de la hipótesis.

### 1.2 Hipótesis operacional

La hipótesis alternativa operacional es:

> Los indicadores ambientales locales, de productividad y regionales antárticos/Pacífico Sur presentan asociaciones con la biomasa observada de anchoveta y pueden aportar información explicativa adicional.

La hipótesis nula operacional es:

> La incorporación progresiva de variables de productividad y de indicadores regionales antárticos/Pacífico Sur no aporta información explicativa o predictiva estable después de considerar el ambiente local y ENSO.

Esta formulación no prueba la hipótesis general de conectividad física. Evalúa únicamente si los bloques ambientales muestran asociaciones consistentes con los indicadores disponibles de anchoveta.

### 1.3 Objetivo

El objetivo fue comparar tres modelos acumulativos:

- **Experimento A:** ambiente local del sistema de Humboldt.
- **Experimento B:** ambiente local más productividad.
- **Experimento C:** ambiente local, productividad e índice regional de conectividad ambiental.

También se revisó un análisis anual independiente con biomasa evaluada de RAM Legacy para comprobar si el bloque antártico mejora un modelo temporal de mayor cobertura histórica.

> **[PLACEHOLDER FIGURA 1: Diagrama conceptual de los experimentos A, B y C]**

---

## 2. Metodología

### 2.1 Fuentes y respuesta biológica

Se utilizaron dos respuestas independientes que no fueron combinadas:

1. **Biomasa por crucero IMARPE**

   Se seleccionaron los registros con:

   - fechas completas de inicio y fin;
   - biomasa disponible;
   - cobertura `toda_costa`;
   - ausencia de duplicación de cruceros.

   El resultado fue de **9 cruceros observados**, entre agosto de 1998 y noviembre de 2021.

2. **Biomasa evaluada RAM Legacy v4.44**

   Se utilizó el stock `PANCHPERUNC`, correspondiente a la anchoveta peruana del área norte-centro. La serie contiene 53 observaciones históricas, pero la intersección completa con las variables ambientales produjo **17 años utilizables**.

RAM Legacy representa una serie de evaluación de stock y no una serie independiente de mediciones hidroacústicas IMARPE. Por ello, se utilizó como análisis temporal complementario.

No se utilizaron desembarques, biomasa interpolada ni salidas de simulación como sustitutos automáticos de la respuesta biológica.

### 2.2 Predictores ambientales

El ambiente local provino del panel procesado de experimentos A/B e incluyó:

- temperatura superficial del mar;
- oxígeno disuelto;
- clorofila-a;
- carbono fitoplanctónico;
- Niño 1+2;
- variables ambientales adicionales disponibles en el panel.

El panel regional de conectividad incluyó seis regiones:

- Península Antártica;
- mar de Bellingshausen;
- Pacífico Sur intermedio;
- Pacífico Sur subtropical;
- transición hacia Humboldt;
- Humboldt peruano.

Para el análisis C se utilizó la banda de profundidad `100–200 m`, debido a su relevancia para representar condiciones subsuperficiales sin asumir que corresponden directamente a AAIW.

El índice regional de conectividad se construyó a partir de anomalías estandarizadas de temperatura, salinidad, corrientes zonales y meridionales y oxígeno en las regiones antártica, Pacífico Sur y transición.

Este índice debe interpretarse como un **índice ambiental regional**, no como una medida de transporte, trayectoria lagrangiana o conectividad de masas de agua.

### 2.3 Tratamiento temporal e interpolación

Se realizaron dos versiones del análisis de cruceros:

#### Versión interpolada

Los predictores ambientales regionales se interpolaron linealmente en el punto medio temporal de cada crucero. La biomasa nunca fue interpolada.

#### Versión sin interpolación

Los predictores regionales utilizaron exclusivamente el valor mensual disponible correspondiente al mes central de cada crucero. La biomasa continuó siendo observada y no interpolada.

Los predictores ambientales locales de A y B se conservaron como promedios durante el intervalo completo de cada campaña, tal como fueron construidos en el panel original.

También se calcularon los rezagos de 0, 3, 6, 12, 18 y 24 meses para el índice regional.

### 2.4 Transformación de la respuesta

La respuesta de cruceros se transformó como:

\[
Y_i = \log_{10}(B_i)
\]

donde \(B_i\) es la biomasa observada en el crucero \(i\).

La transformación reduce la asimetría y permite interpretar los modelos como asociaciones sobre una escala logarítmica.

### 2.5 Modelos acumulativos

Debido a que solo existen nueve cruceros con fechas completas, se utilizaron modelos lineales parsimoniosos. No se ajustaron GAM complejos como modelo principal porque el tamaño muestral no permite estimar curvas no lineales de forma confiable.

Las especificaciones principales fueron:

#### Modelo A

\[
Y_i = \beta_0 + \beta_1 SST_i + \beta_2 Niño1+2_i + \varepsilon_i
\]

#### Modelo B

\[
Y_i = M_A + \beta_3 Chl_i + \varepsilon_i
\]

#### Modelo C

\[
Y_i = M_B + \beta_4 Conectividad_i + \varepsilon_i
\]

Las variables se estandarizaron antes del ajuste.

Se calcularon:

- R²;
- R² ajustado;
- AIC;
- RMSE leave-one-cruise-out;
- coeficientes y errores estándar;
- intervalos bootstrap;
- correlaciones de Spearman por rezago;
- corrección FDR para la familia de rezagos.

### 2.6 Análisis anual RAM

Para RAM se compararon modelos GLS anidados:

#### Modelo RAM M0

\[
\log_{10}(TB_t) = SST_t + Chl_t + O_2{}_t + Niño1+2_t + PDO_t + Tendencia_t + \varepsilon_t
\]

#### Modelo RAM M1

\[
M1 = M0 + Hielo_{t-1} + SAM_{t-1}
\]

Se realizaron dos sensibilidades:

- GLS con errores independientes;
- GLS con estructura AR(1).

En ambas comparaciones, M0 y M1 utilizaron la misma estructura de covarianza.

---

## 3. Resultados

### 3.1 Cobertura de la respuesta de cruceros

El panel de cruceros utilizado contiene:

| Característica | Resultado |
|---|---:|
| Cobertura seleccionada | `toda_costa` |
| Cruceros con fechas completas | 9 |
| Primera campaña | 1998-08-20 |
| Última campaña | 2021-11-03 |
| Biomasa interpolada | No |
| Predictores ambientales interpolados | Solo en la versión interpolada |

> **[PLACEHOLDER FIGURA 2: Serie temporal de las nueve observaciones de biomasa por crucero]**

> **[PLACEHOLDER FIGURA 3: Mapa de cobertura espacial de los cruceros y cajas ambientales]**

### 3.2 Comparación de los modelos de cruceros

#### Versión sin interpolación

| Modelo | R² | R² ajustado | AIC | RMSE LOOCV |
|---|---:|---:|---:|---:|
| A: ambiente local | 0.472 | 0.296 | 5.303 | 0.349 |
| B: productividad | 0.650 | 0.440 | 3.600 | 0.369 |
| C: conectividad | 0.689 | 0.377 | 4.548 | 0.401 |

El modelo B aumentó el ajuste dentro de muestra, pero su error leave-one-cruise-out fue ligeramente mayor que el de A. El modelo C presentó el mayor R², pero no produjo el mejor desempeño predictivo.

El coeficiente del índice de conectividad en C fue:

```text
estimación = -0.089
p = 0.520
intervalo bootstrap 95 % ≈ [-1.31, 0.23]
```

El intervalo es amplio e incluye valores positivos y negativos.

#### Versión con interpolación

| Modelo | R² ajustado | RMSE LOOCV |
|---|---:|---:|
| A: ambiente local | 0.296 | 0.349 |
| B: productividad | 0.440 | 0.369 |
| C: conectividad | 0.337 | 0.413 |

La comparación entre las dos versiones muestra que la interpolación no produjo una mejora clara. En particular, el RMSE del modelo C fue peor con interpolación.

> **[PLACEHOLDER FIGURA 4: Comparación de R² ajustado y RMSE LOOCV entre las versiones interpolada y no interpolada]**

### 3.3 Análisis de rezagos

En la versión sin interpolación, las asociaciones de Spearman entre el índice de conectividad y la biomasa fueron:

| Rezago | n | ρ | p ajustado FDR |
|---:|---:|---:|---:|
| 0 meses | 9 | 0.033 | 0.932 |
| 3 meses | 9 | 0.617 | 0.462 |
| 6 meses | 9 | -0.467 | 0.521 |
| 12 meses | 8 | -0.071 | 0.932 |
| 18 meses | 8 | -0.167 | 0.932 |
| 24 meses | 8 | 0.452 | 0.521 |

El rezago de tres meses mostró la mayor correlación nominal, pero no fue significativo después de corregir por múltiples comparaciones y se estimó con solo nueve campañas.

En la versión interpolada, el patrón también fue inestable: el signo y magnitud de las correlaciones cambiaron entre rezagos.

> **[PLACEHOLDER FIGURA 5: Correlograma exploratorio entre conectividad y biomasa por rezago]**

### 3.4 Análisis RAM con modelos corregidos

#### GLS con errores independientes

El contraste entre M0 y M1 produjo:

```text
p = 0.2887
```

Por tanto, bajo esta especificación no se rechaza H0.

#### GLS con AR(1)

El contraste con AR(1) aplicada simétricamente a ambos modelos produjo:

```text
p = 0.0010
```

Este resultado difiere sustancialmente del modelo con errores independientes. La sensibilidad indica que la conclusión depende fuertemente de la estructura temporal asumida.

El modelo AR(1) no debe considerarse evidencia confirmatoria debido al pequeño tamaño muestral y al número elevado de parámetros en relación con los 17 años disponibles.

> **[PLACEHOLDER FIGURA 6: Comparación de residuos y estructura temporal de M0 y M1 en RAM]**

### 3.5 Resumen de resultados

Los resultados principales pueden resumirse así:

| Pregunta | Resultado |
|---|---|
| ¿El ambiente local presenta asociación con biomasa? | Asociación exploratoria, no confirmatoria |
| ¿La productividad mejora el ajuste? | Mejora el ajuste interno, no la validación fuera de muestra |
| ¿La conectividad mejora la predicción? | No; C tiene mayor RMSE LOOCV |
| ¿Los rezagos son robustos? | No, cambian de signo y no sobreviven FDR |
| ¿RAM produce una decisión estable? | No; depende de IID frente a AR(1) |
| ¿Se rechaza H0? | No de forma robusta |

---

## 4. Discusión

### 4.1 Interpretación científica

Los resultados no proporcionan evidencia robusta para afirmar que los indicadores antárticos o del Pacífico Sur expliquen adicionalmente la variabilidad de la biomasa de anchoveta bajo la información disponible.

El modelo B muestra una mejora en el ajuste interno, pero esa mejora no se reproduce en la validación leave-one-cruise-out. Esto sugiere que parte de la mejora puede deberse al ajuste a las nueve campañas disponibles y no necesariamente a una capacidad predictiva generalizable.

El modelo C presenta un R² mayor que A y B en la versión sin interpolación, pero su error fuera de muestra es el mayor. Además, el coeficiente del índice de conectividad cambia de signo al comparar la versión interpolada con la no interpolada. Esto es una señal de inestabilidad, no de un efecto ambiental consolidado.

### 4.2 Efecto de la interpolación

La comparación muestra que no es necesario utilizar interpolación para obtener la señal exploratoria. La versión sin interpolación presenta un desempeño ligeramente mejor para C, aunque la diferencia no es suficiente para afirmar una mejora científica.

Por transparencia, la versión sin interpolación debe utilizarse como análisis principal de sensibilidad, mientras que la versión interpolada debe conservarse como análisis secundario. Ninguna de las dos versiones genera observaciones biológicas adicionales.

### 4.3 Dependencia de la autocorrelación en RAM

La diferencia entre `p = 0.2887` con errores independientes y `p = 0.0010` con AR(1) demuestra que la inferencia anual es muy sensible a la especificación temporal.

Con 17 observaciones, un modelo con varios predictores, una tendencia temporal y una estructura AR(1) puede producir estimaciones inestables. Por ello, el resultado AR(1) debe presentarse como sensibilidad, no como confirmación de H1.

La conclusión más prudente es que el análisis RAM no ofrece una decisión robusta e independiente de los supuestos estadísticos.

### 4.4 Limitaciones principales

1. Solo existen nueve cruceros con fechas completas para el análisis de biomasa observada.
2. Los cruceros representan una cobertura `toda_costa` y no una serie espacial homogénea de NASC o presencia/ausencia.
3. La biomasa de crucero no contiene coordenadas o transectos suficientes para un modelo espacial de hábitat.
4. La respuesta RAM corresponde a biomasa evaluada, no a una medición acústica independiente.
5. El índice de conectividad es una combinación de anomalías regionales y no una métrica física de transporte.
6. Las regiones ambientales tienen diferentes resoluciones verticales y procedencias de datos.
7. La disponibilidad de solo 17 años completos limita la inferencia temporal.
8. Los resultados son sensibles a la estructura de autocorrelación.
9. El uso de múltiples rezagos reduce la potencia efectiva y requiere corrección por comparaciones múltiples.
10. No se incorporaron esfuerzo pesquero, cuotas, vedas ni cierres porque la respuesta principal no fueron desembarques.

### 4.5 Veredicto sobre H0 y H1

El veredicto debe expresarse de forma condicionada:

> Bajo la respuesta de biomasa por crucero, la resolución ambiental disponible, los nueve cruceros con fechas completas y la validación leave-one-cruise-out, no se observa una contribución robusta de los indicadores regionales de conectividad.

> Bajo la respuesta anual RAM, el resultado depende de la estructura de autocorrelación. El modelo con errores independientes no rechaza H0, mientras que AR(1) produce una señal significativa que no puede considerarse concluyente debido al pequeño tamaño muestral y a la sensibilidad del modelo.

Por lo tanto:

```text
Conclusión principal: no se rechaza H0 de forma robusta.
Estado de H1: no refutada, pero tampoco respaldada de manera suficiente.
Alcance: asociación exploratoria, no conectividad física ni causalidad.
```

### 4.6 Recomendaciones

Para fortalecer el análisis se recomienda:

1. Incorporar más campañas IMARPE con fechas, coordenadas, stock y NASC documentados.
2. Separar consistentemente stock norte-centro, stock sur y cobertura de toda la costa.
3. Mantener la biomasa de crucero como respuesta irregular, sin interpolarla.
4. Añadir una respuesta espacial de presencia, densidad o NASC si se dispone de ella.
5. Validar los índices regionales con temperatura, salinidad y corrientes independientes.
6. Preespecificar un número reducido de rezagos y evitar seleccionar el mejor resultado retrospectivamente.
7. Repetir el análisis con bootstrap por campaña y validación temporal cuando exista mayor cobertura.
8. Utilizar GAM o GAMM únicamente cuando el tamaño muestral y la cobertura espacial lo permitan.
9. Mantener los resultados RAM y de cruceros como análisis complementarios, no como una serie combinada.
10. Presentar los modelos predictivos como herramientas de monitoreo y no como pruebas de causalidad.

---

## 5. Reproducibilidad

### Preparación con interpolación

```bash
python scripts/17_prepare_exploratory_analysis.py
Rscript analysis_r/04_exploratory_models.R
```

### Preparación sin interpolación

```bash
python scripts/17_prepare_exploratory_analysis.py \
  --no-interpolation \
  --output data/processed/tables/exploratory_cruise_panel_nointerp.csv

Rscript analysis_r/04_exploratory_models.R \
  --panel data/processed/tables/exploratory_cruise_panel_nointerp.csv \
  --out-dir analysis_r/data/exploratory_nointerp
```

### Archivos principales

- `data/processed/tables/exploratory_cruise_panel.csv`
- `data/processed/tables/exploratory_cruise_panel_nointerp.csv`
- `analysis_r/data/exploratory/cruise_model_metrics.csv`
- `analysis_r/data/exploratory_nointerp/cruise_model_metrics.csv`
- `analysis_r/data/exploratory_nointerp/cruise_connectivity_lag_correlations.csv`
- `analysis_r/data/exploratory_nointerp/ram_block_lrt_corrected.csv`

Los archivos generados distinguen la respuesta observada, los predictores ambientales y el tratamiento temporal utilizado.


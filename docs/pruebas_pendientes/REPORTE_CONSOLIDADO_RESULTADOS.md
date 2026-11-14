# Reporte consolidado de resultados: ambiente, fitoplancton y anchoveta

**Proyecto:** ANCHOVETA 360 / Chaski Polar. **Corte:** 14 de noviembre de 2026.

Este es el documento de consulta principal para los resultados discutidos hasta esta fecha. Integra las pruebas históricas, el contraste específico de carbono Antártida–Humboldt, la exploración de 33 relaciones ecológicas y la ronda de 162 tendencias incorporada en `b29945e`. Las tablas completas de las rondas recientes están incluidas al final, sin necesidad de abrir sus reportes separados. Las fuentes, archivos y comandos quedan documentados para reproducirlas.

## 1. Resumen de resultados y relaciones que interesan

**La línea con mejor soporte es la asociación de El Niño con el ambiente y el fitoplancton peruano.** También hay asociaciones locales de mezcla y carbono en Bellingshausen y el Pacífico Sur, útiles para comparar regiones. **No se obtuvo evidencia robusta de conexión directa entre biomasa fitoplanctónica antártica y peruana.**

En las tablas, **q** significa p-valor ajustado por FDR y **r parcial** corresponde a una asociación después de los controles indicados, no a la correlación bruta. Una flecha señala el predictor y la respuesta del análisis, sin demostrar causalidad.

| Prioridad | Relación o resultado | Evidencia principal | Interés para continuar | Alcance |
|---|---|---|---|---|
| 1 | Niño 1+2 → carbono fitoplanctónico peruano | r parcial −0,537; q = 1,34 × 10⁻⁷; 336 meses | Estudiar biomasa de fitoplancton, además de pigmento | Carbono CMEMS modelado; consistente en las sensibilidades realizadas |
| 1 | Niño 1+2 → clorofila de Chimbote y Callao | r parcial −0,406 y −0,388; q = 3,37 × 10⁻⁸ y 2,85 × 10⁻⁸ | Respuesta regional del pigmento bajo El Niño | OC-CCI satelital; consistente en las sensibilidades realizadas |
| 2 | Mezcla → carbono en Pacífico Sur subtropical e intermedio | r parcial −0,451 y −0,395; q = 1,74 × 10⁻¹⁴ y 6,97 × 10⁻⁵ | Comparar condiciones locales de luz/mezcla y concentración superficial | Campos modelados; asociación consistente, sin transporte demostrado |
| 2 | Mezcla → carbono en Bellingshausen | r parcial −0,226; q = 0,000729 | Mantener una pregunta antártica local y compararla con Humboldt | Campos modelados; aporte temporal modesto |
| 2 | Mezcla → clorofila/carbono peruano | r parcial +0,477; q = 6,27 × 10⁻¹⁹ | Mostrar por qué pigmento y biomasa no son equivalentes | Cociente derivado de campos del mismo modelo; hipótesis de fotoaclimatación |
| 3 | Nitrato un mes antes → carbono subtropical | r parcial +0,316; q = 0,000310 | Relación nutrientes–biomasa para estudiar con observaciones independientes | Modelo; significativa y consistente en esta exploración |
| Contexto temporal | Nivel del mar de GLORYS en Humboldt | +2,59 cm/década en 1998–2025; q = 0,000106 | Contexto físico para un monitor de cambios del océano | Tendencia, no correlación; falta sensibilidad a autocorrelación anual |
| Pendiente | Mezcla → clorofila NASA de Chimbote | r parcial −0,176; q = 0,000962 en todo el periodo | Comprobación satelital de una posible relación local | No confirma significancia en ambas mitades |
| Sin respaldo suficiente | Carbono antártico → carbono de Humboldt | 0 de 12 contrastes con FDR; q mínimo 0,1865 | Mantener el resultado negativo como parte del estudio | No demuestra ausencia de relación; no respalda la conexión propuesta |

**Recomendación:** organizar el proyecto alrededor de «qué controla la biomasa y el color del océano en distintas regiones», con El Niño y Humboldt como línea principal, y comparación de mecanismos locales con Antártida/Pacífico Sur. Un apartado de tendencias puede mostrar el cambio físico y la sensibilidad al periodo. No presentar estas asociaciones como una cadena causal Antártida → Perú → anchoveta.

**Balance de las tres rondas recientes:**

| Ronda | Pregunta | Pruebas principales | Resultado |
|---|---|---:|---|
| Script 18 | Carbono antártico frente a carbono peruano, seis rezagos | 12 | Ninguna con FDR < 0,05; 312 meses por contraste |
| Script 19 | Relaciones ecológicas locales y respuesta a El Niño | 33 | 16 con FDR; 9 conservan signo y significancia en todas las sensibilidades; una empeora mucho el error temporal |
| Ronda de seis variables | Tendencias con distintos periodos y exclusiones | 162 | 38 significativas con FDR; no son 38 hallazgos independientes |

No se suman estas cifras a las «más de 1.100 pruebas» históricas para obtener un total de evidencia: hay series, periodos y preguntas repetidos. Las correcciones FDR son por familia o ronda, no por toda la historia exploratoria del proyecto.

## 2. Datos disponibles y significado de las variables

| Variable/producto | Qué representa | Cobertura utilizada y limitaciones |
|---|---|---|
| `chl`, `chlor_a` | Concentración de clorofila-a, pigmento en mg/m³ | CMEMS modelado; OC-CCI satelital; MODIS-Aqua satelital. No son mediciones intercambiables |
| `phyc` | Carbono fitoplanctónico, concentración de biomasa en mmol C/m³ | Panel CMEMS regional 1998–2025 y serie peruana hasta agosto de 2026. Conversión a mg C/m³: ×12,0107 |
| Clorofila/carbono | Pigmento por carbono, usado en logaritmo en H33 | Cociente de resúmenes regionales, no medición celular directa ni productividad |
| `mlotst` | Profundidad de capa de mezcla, metros | 336 meses por región en `surface_2d`; no está en `surface_0_5m` |
| `thetao`, `so`, `uo`, `vo`, `zos` | Temperatura, salinidad, corrientes y altura del mar | Reanálisis físico CMEMS; no observaciones directas independientes |
| `no3`, `po4`, `o2` | Nutrientes y oxígeno | Campos CMEMS; mantener unidades y procedencia |
| Niño 1+2, ICEN, ONI, PDO, SAM/AAO | Índices climáticos | Describen dominios y procesos diferentes; evaluar colinealidad y cobertura |
| NSIDC G02135 | Extensión agregada de hielo marino antártico | No equivale a concentración sectorial ni transporte oceánico |
| NASA POWER / ERA5 | Lluvia, atmósfera y viento | Productos con grillas y procedencias propias; evitar discontinuidades entre fuentes |
| Biomasa de cruceros IMARPE | Respuesta biológica por campaña | Irregular; 9 campañas originales con fechas completas; sensibilidad ampliada a 12 con fechas aproximadas |
| RAM Legacy `PANCHPERUNC`, `tb.data` | Biomasa evaluada del stock norte-centro | Resultado de evaluación de stock; 17 años completos en el análisis ambiental anual |
| BCRP/PRODUCE y FAO | Desembarques/capturas | Afectados por cuotas, vedas, esfuerzo y decisiones operativas; no equivalen a biomasa |

El panel regional tiene seis regiones: Península Antártica, Bellingshausen, Pacífico Sur intermedio, Pacífico Sur subtropical, transición hacia Humboldt y Humboldt peruano. `phyc` tiene 336 meses por región en 0–5, 100–200 y 200–500 m; no hay datos de esa variable en 500–1000 m. Los NetCDF regionales grandes no están en esta copia, pero sí sus series procesadas. El NetCDF peruano contiene 344 meses, enero de 1998–agosto de 2026.

La agregación regional original es la mediana espacial del promedio de niveles de profundidad. Por ello, el resultado es concentración superficial o por banda, **no biomasa total integrada por área o por columna de agua**.

El código antiguo contiene una conversión `carbono = clorofila / 0,02`. Una multiplicación constante conserva la correlación y no produce evidencia nueva. Las pruebas recientes de carbono usan `phyc` de CMEMS, que sí es otra variable. POC es carbono orgánico particulado, no exclusivamente fitoplanctónico; producción primaria es una tasa, no una concentración de biomasa.

MODIS-Aqua de Giovanni cubre julio de 2002–noviembre de 2025 en Chimbote y Paita: 281 meses en la lectura actual completa. Algunos análisis históricos usaron 280. OC-CCI comparte sensores con MODIS: comparar productos comprueba sensibilidad al procesamiento y la cobertura, sin independencia total de observaciones. En Antártida hay ausencias ópticas estacionales; no se rellenaron inviernos.

## 3. Métodos y cómo interpretar la evidencia

| Familia | Método y controles | Criterio y alcance |
|---|---|---|
| Pruebas históricas A/B/E | Correlación, parcial cuando corresponde, anomalías mensuales, n efectivo de Pyper–Peterman | FDR por familia, mismo signo sin 1998 y por mitades. Resultados de métodos distintos no son directamente intercambiables |
| Carbono Antártida–Humboldt, script 18 | OLS; Niño 1+2 simultáneo y rezagado; tendencia y mes; covarianza HAC/Bartlett de 12 meses | FDR sobre 12 contrastes; sensibilidad HAC6/HAC24, periodos, rangos y clorofila secundaria |
| Exploración ecológica, script 19 | Anomalías y OLS; tendencia y mes; control ENSO si no es el predictor; HAC12 | FDR global sobre 33 hipótesis; repetir hasta 2011, desde 2012, sin 1998, HAC6/HAC24 |
| Tendencias de seis variables | Anomalía mensual, media anual con ≥9 meses, Kendall y pendiente de Sen con IC aproximado | FDR sobre 162 pruebas. Sin ajuste por autocorrelación anual; incluye periodos solapados |
| Predicción histórica E8 | Origen móvil, ajuste con años previos, Niño y clorofila rezagados | Comparación con climatología y persistencia; distinta de la evaluación condicional del script 19 |
| Evaluación condicional del script 19 | Ajuste por años 2012–2025 usando solo entrenamiento previo | Predictor contemporáneo conocido cuando el rezago es cero; no pronóstico operativo |

Un resultado significativo puede ser pequeño, depender del producto o empeorar la evaluación temporal. Los intervalos incluidos son individuales, no intervalos simultáneos corregidos por multiplicidad. Un q < 0,05 no es la probabilidad de que H0 sea verdadera. No rechazar H0 no prueba ausencia de relación.

Los periodos ya fueron inspeccionados en estudios anteriores. La división retrospectiva del periodo y la FDR de cada tanda no convierten la investigación en una validación ciega. Los campos CMEMS comparten estructura de modelo y forzamiento: una asociación entre ellos requiere comprobación observacional externa.

## 4. Relaciones ecológicas recientes: qué se mantiene y qué no

### 4.1 El Niño y carbono/pigmento peruano

El contraste Niño 1+2–carbono peruano se mantiene en 1998–2011 (r parcial −0,560), 2012–2025 (−0,598) y sin 1998 (−0,574). La clorofila de Chimbote y Callao de OC-CCI también mantiene la asociación negativa. El carbono es modelado; la clorofila es pigmento estimado por satélite.

La evaluación condicional con origen móvil reduce el RMSE alrededor de 15,0 % para carbono peruano, 13,6 % para clorofila de Chimbote y 12,8 % para Callao, respecto a los mismos controles sin el predictor. Son diferencias observadas sin intervalo de incertidumbre de la mejora; no se ha demostrado significancia de esas diferencias ni superioridad operativa frente a persistencia en esta ronda.

### 4.2 Mezcla y comparación regional

Una capa de mezcla más profunda se asocia con menor carbono superficial en Bellingshausen y los sectores intermedio y subtropical del Pacífico Sur, después de controlar ENSO, tendencia y estacionalidad. Esto es compatible con cambios de luz y/o dilución, pero no distingue mecanismos ni demuestra pérdida de biomasa integrada.

La relación no se mantiene de la misma forma en la Península ni en el carbono peruano: r parcial −0,046 y −0,049, con q = 0,639 y 0,706. La comparación regional incluye estos resultados negativos.

La mejora condicional de RMSE es aproximadamente 2,1 % en Bellingshausen, 8,0 % en Pacífico intermedio y 7,4 % en el subtropical. La capa de mezcla fue recuperada seleccionando la banda `surface_2d`; el script histórico E7 la buscaba en una banda distinta y la descartaba como vacía.

### 4.3 Pigmento por carbono y nutrientes

En Humboldt, más mezcla se asocia con más pigmento por carbono (H33). La mejora condicional de RMSE es 13,2 %. El resultado permite formular una pregunta de fotoaclimatación, pero también puede reflejar relaciones incorporadas en el modelo; no mide productividad ni crecimiento celular directamente.

Nitrato un mes antes y carbono subtropical (H28) es significativo y consistente, con mejora condicional de RMSE de 6,3 %. En cambio, la relación equivalente en la transición de Humboldt (H29) tiene r parcial +0,515 y q = 2,10 × 10⁻⁶, pero **empeora el RMSE aproximadamente 267 %**. Aunque pasa las sensibilidades de significancia, no se recomienda como predictor.

### 4.4 Comprobación NASA

En MODIS-Aqua de Chimbote, la mezcla regional y Niño 1+2 tienen asociaciones negativas significativas en el periodo completo (H20 y H06). No se confirman significativamente en ambas mitades: para mezcla, q = 0,330 hasta 2011 y 0,0645 desde 2012. Las cajas de mezcla regional y clorofila costera no coinciden exactamente. En Paita no aparece una asociación simultánea significativa para esos dos predictores.

## 5. Contraste específico de carbono Antártida–Humboldt

Se comparó `phyc` de Península y Bellingshausen con `phyc` peruano para rezagos de 0, 3, 6, 12, 18 y 24 meses. Un rezago positivo significa que la serie antártica precede a la peruana. La ventana común elimina los primeros 24 meses y contiene 312 meses entre 2000 y 2025.

**Ninguno de los 12 contrastes supera FDR.** Tres p-valores originales son inferiores a 0,05, pero su q es 0,1865. La conclusión es «no se obtuvo evidencia suficiente para rechazar H0 en la especificación evaluada».

Las asociaciones locales de la sección anterior no cambian esta conclusión. El antecedente H1e documenta 180 pruebas de ambiente austral frente a clorofila/carbono peruano, sin resultados robustos, pero no se localizaron sus tablas ni su script específico en esta copia: se conserva como antecedente documentado, no como resultado reejecutado.

## 6. Tendencias de seis variables: cifras verificadas y correcciones

La ronda añadida en `b29945e` contiene 162 pruebas y 38 q < 0,05. Se verificó numéricamente la FDR del CSV contra la implementación de referencia y se reprodujeron nueve ajustes del panel local: nivel del mar, temperatura y oxígeno, cada uno desde 1998, 2003 y 2010. Coinciden sus pendientes y p-valores. No se reejecutaron todas las fuentes externas de la ronda.

| Variable | Periodo | Sen por década | q FDR verificado | Lectura |
|---|---|---:|---:|---|
| Nivel del mar GLORYS, Humboldt | 1998–2025 | +0,02586 m | 0,000106 | Tendencia positiva |
| Nivel del mar GLORYS, Humboldt | 2003–2025 | +0,02865 m | 0,000127 | Tendencia positiva |
| Nivel del mar GLORYS, Humboldt | 2010–2025 | +0,02658 m | 0,04894 | Significativa, cerca del umbral |
| Nivel del mar, sin años extremos | 2010–2025 | +0,02276 m | 0,05193 | No supera FDR |
| Temperatura 100–200 m, Humboldt | 1998–2025 | +0,1614 °C | 0,05193 | No supera FDR |
| Temperatura 100–200 m, Humboldt | 2003–2025 | +0,2600 °C | 0,01530 | Significativa |
| Temperatura 100–200 m, Humboldt | 2010–2025 | +0,3720 °C | 0,10364 | No supera FDR |
| Oxígeno 100–200 m, Humboldt | 1998–2025 | +1,597 mmol/m³ | 0,63694 | Sin tendencia significativa |
| Oxígeno 100–200 m, Humboldt | 2003–2025 | +5,363 mmol/m³ | 0,01760 | Significativa, dependiente del inicio |
| Hielo antártico | 1979–2026 | −0,02758 millones km² | 0,82560 | Sin tendencia significativa |
| Hielo antártico | 1998–2026 | −0,4261 millones km² | 0,04565 | Significativa en este periodo |
| Hielo antártico, sin extremos | 2003–2026 | −0,5353 millones km² | 0,05955 | No supera FDR |
| Hielo antártico, sin extremos | 2010–2026 | −0,8597 millones km² | 0,03940 | Significativa |
| ERSST norte-centro, región Niño 1+2 | 1900–2026 | +0,0765 °C | 0,0008 aprox. | Serie larga; sin significancia desde 1979 |
| ERSST costa sur | 1900–2026 | +0,1053 °C | <0,0001 | Serie larga; sin significancia desde 1979 |

Las siguientes afirmaciones del reporte original quedan corregidas por el CSV:

- Temperatura 100–200 m en 1998–2025: q no es 0,034 sino **0,05193**, lo que cambia el veredicto.
- Nivel del mar desde 2010: q es **0,04894** con todos los años; al excluir 1998, 2016 y 2023 sube a **0,05193**. No mantiene significancia en todos los periodos/exclusiones.
- Hielo desde 2003 sin extremos: q = **0,05955**; no mantiene significancia, aunque sí lo hace desde 2010.
- Otros q del resumen anterior estaban desactualizados; para esta consolidación prevalecen los 162 valores de la tabla versionada.

El nivel del mar tiene la señal temporal más consistente de esta tanda, con límites. La temperatura subsuperficial y el oxígeno dependen del inicio. Las medias anuales no garantizan independencia: **falta corregir autocorrelación anual**. El criterio de ≥9 meses permite años incompletos, incluido potencialmente 2026; se debe repetir terminando en 2025. Excluir tres años no equivale a controlar ENSO continuamente.

Los mareógrafos miden nivel relativo, que incluye movimiento vertical de la costa. Callao da aproximadamente −1,26 cm/década en 1970–2024 (q = 0,0231), pero no una tendencia significativa en 1998–2024 (q = 0,6369). No es una contradicción automática con `zos` regional de GLORYS. Las señales de viento se consideran descartadas como hallazgo por discontinuidades entre fuentes y periodos cortos; los resultados restantes constan en el anexo.

## 7. Resultados históricos que siguen siendo relevantes

### 7.1 Cadena ambiental de El Niño

La tanda E7 documenta las siguientes asociaciones, con su método original de n efectivo y FDR. Los rezagos corresponden a selecciones exploratorias dentro de esa tanda, no a estimaciones confirmatorias de tiempos de transporte.

| Niño 1+2 frente a | Rezago | r histórico | Estado |
|---|---:|---:|---|
| Temperatura superficial de Humboldt | 0 meses | +0,84 | Pasa el criterio histórico |
| Nivel del mar | 0 | +0,68 | Pasa el criterio histórico |
| Temperatura a 100–200 m | 2 | +0,64 | Pasa el criterio histórico |
| Oxígeno a 100–200 m | 0 | +0,60 | Pasa el criterio histórico |
| Oxígeno superficial | 1 | −0,66 | Pasa el criterio histórico |
| Fosfato superficial | 2 | −0,54 | Pasa el criterio histórico |
| Clorofila CMEMS | 0 | −0,32 | Pasa el criterio histórico |
| Nitrato superficial | 0 | −0,20 | No pasa FDR |

El aumento de oxígeno a 100–200 m es compatible con cambios en la posición de la zona mínima de oxígeno; no significa que todo el océano pierda o gane oxígeno de igual manera. El desplazamiento exacto de esa frontera no se estimó con estos promedios por bandas.

El resumen histórico decía que ninguna variable añadía información sobre clorofila al controlar El Niño. La tabla E7 contiene **dos de 80 contrastes** que sí pasan su criterio: temperatura 100–200 m con Chimbote (r = −0,242; q = 0,0482) y oxígeno 100–200 m con Callao (r = −0,166; q = 0,0381). Son señales pequeñas, cercanas al umbral, y no prueban mediación causal; la de oxígeno se debilita en la segunda mitad. La redacción correcta es que la mayoría de señales desaparece al controlar ENSO y no se estableció un mediador independiente robusto.

### 7.2 Pruebas A/B y pistas descartadas o no confirmadas

| Prueba | Tamaño documentado | Resultado y consecuencia |
|---|---:|---|
| Clorofila antártica–peruana H1a/H1b | 50 desfases | Ninguno con FDR |
| Ambiente austral–clorofila/carbono H1e | 180 | Sin resultado robusto según registro; artefactos específicos no localizados |
| Profundidad/altimetría regional | Más de 600 según registro | Sin señal robusta; la pista de 3–4 años se atribuyó al ciclo ENSO |
| A1 Clorofila–desembarques | 100 | Ninguna robusta; mejor candidata r ≈ 0,24 y q ≈ 0,07. Manejo pesquero incompletamente controlado |
| A3 Viento–clorofila | 40 | Ninguna robusta |
| A5 Nivel del mar–clorofila | 50 | Diez robustas sin controlar ENSO, cero con control; sin adelanto independiente demostrado |
| A2 Kd490–clorofila/oxígeno | 16 | Cinco con clorofila; r ≈ 0,99, ligadas a la recuperación óptica. Sin resultado robusto con oxígeno |
| B1 ENSO–Antártida | 104 | Ninguna robusta |
| B2 SAM × ENSO | 6 | Ninguna interacción significativa |
| B3 Cadena Antártida–Pacífico–Perú | 240 = 156 + 84 | Ningún eslabón robusto que complete la cadena |
| B4 Corrientes–temperatura/nitrato peruano | 208 | Ninguna robusta; candidata zonal r ≈ 0,29, q ≈ 0,057 |
| B5 SAM/hielo–capturas FAO | 128 | Ninguna robusta; poca potencia anual y capturas no equivalentes a abundancia |
| Reglas de asociación | 218 candidatas | Sin novedad independiente más allá de mar cálido–clorofila baja |
| E1 Extremos de clorofila/temperatura | 14 | Sin tendencias significativas tras FDR |
| E2 Fenología de clorofila | 21 | Sin tendencias significativas tras FDR |
| E3 Intensidad de eventos y recuperación | Cuatro eventos, uno incompleto | Insuficiente para conclusión firme |

Las reducciones históricas de clorofila en meses de Niño 1+2 ≥ +1 °C rondan 45 % en Chimbote/Callao, 20–23 % en Pisco/Ilo y son pequeñas en Paita. Son descripciones de esos datos y periodos, no pérdidas causales de biomasa ni efectos uniformes sobre la costa.

La asimetría térmica ajustada describe pendientes con calor de −25,8 %/°C en Chimbote, −26,3 en Callao, −30,1 en Ilo, −18,2 en Pisco y −6,0 en Paita. Las pendientes con frío no son iguales entre zonas. En 2015–2025 el modelo asimétrico mejora al lineal entre −1,4 % y +1,6 %: no tiene ventaja predictiva consistente.

### 7.3 Paita, lluvia y contraste NASA

Con OC-CCI se documentó un aumento de clorofila de Paita 2–8 meses después del calentamiento, máximo a cinco meses (r ≈ +0,36). Conserva signo sin 1998 y al quitar la parte lineal asociada a lluvia; eso no descarta todos los mecanismos de escorrentía. Niño 1+2–lluvia de Paita da r ≈ +0,40. La relación tardía mantiene dirección con MODIS-Aqua (r ≈ +0,16 a +0,22) pero no supera FDR, con q reportados aproximadamente 0,05–0,13. Queda como pista dependiente del producto y periodo.

### 7.4 Tendencias previas de clorofila, temperatura y mapas

- Cinco zonas peruanas, OC-CCI 1998–2025: sin tendencia anual significativa (p ≈ 0,13–0,80).
- Chimbote 2003–2025: OC-CCI indica −0,31 mg/m³ por década (p = 0,033), MODIS-Aqua −0,14 (p = 0,68). No hay corroboración entre productos.
- Rey Jorge con CRW: +0,18 °C/década en 1998–2025 (p = 0,002), pero +0,02 en 1986–2025 (p = 0,64). Península: +0,16 (p = 0,030) y −0,01 (p = 0,76), respectivamente. ERSST cambia la lectura según periodo y resolución; no sostener una conclusión regional única de calentamiento con estas selecciones.
- El Mann–Kendall estacional mensual sin corrección de autocorrelación puede producir p demasiado optimistas; no reemplaza una sensibilidad temporal adecuada.
- E9 por celda: el registro documenta en clorofila 32 % de celdas significativas desde 1998 (1.781 aumentan y 108 disminuyen), 8 % desde 2003 y casi ninguna desde 2012. En temperatura, 2 % desde 1998 (38 aumentos de 39 significativas) y ninguna desde 2012. Las series de mapas están cuantizadas; hay dependencia espacial y sensibilidad al año inicial. No generalizar esos porcentajes como prueba uniforme de cambio oceánico.

## 8. Predicción, monitor y respuesta de anchoveta

### 8.1 Predicción histórica E8 de clorofila

El modelo usa Niño 1+2 y clorofila rezagados, con origen móvil 2010–2025. La tabla completa por zona y horizonte figura en el anexo. A un mes mejora RMSE frente a climatología entre 5,2 % y 17,4 %, y frente a persistencia entre 9,4 % y 21,6 % para ese horizonte. La cifra histórica de hasta 31 % frente a persistencia incluye horizontes mayores. A tres meses la mejora frente a climatología es pequeña y en Pisco negativa.

La comprobación histórica E8 de 2026 reporta siete meses observados con Niño conocido: r = 0,84 en Callao, 0,77 en Chimbote, 0,91 en Pisco y 0,64 en Paita; en Ilo falla, con media observada cercana a −45 % frente a −8 % estimada. Esa corrida usa una fuente de series distinta del `monitor_data.json` que en otros análisis solo tenía un mes de clorofila costera para 2026. No mezclar coberturas. No es un pronóstico de El Niño ni una prueba prospectiva con el índice desconocido.

### 8.2 Cruceros observados y RAM

Con nueve cruceros de cobertura `toda_costa`, el modelo A local tiene RMSE leave-one-cruise-out ≈ 0,349 en log10 de biomasa; B, al añadir clorofila, ≈ 0,369; C, con índice regional, ≈ 0,401. Más R² dentro de muestra no significó mejor predicción. El índice de conectividad de C dio p ≈ 0,520 y un intervalo amplio.

La sensibilidad ampliada a 12 cruceros con fechas aproximadas mantiene la ventaja predictiva de A sobre B; al excluir 1998 los coeficientes de Niño se debilitan. El diccionario de campañas, fechas reales, stocks y cobertura espacial sigue siendo necesario. Los resultados completos de las diez variantes A/B figuran en el anexo.

En RAM, con 17 años completos, el contraste con covarianza IID común a M0/M1 da **p = 0,288705**. Con AR(1) común da **p = 0,001025**. La diferencia muestra sensibilidad al supuesto temporal y al pequeño tamaño muestral; no ofrece una decisión robusta. El antiguo **p = 0,114958** comparaba estructuras de covarianza distintas y no es válido para ese contraste.

### 8.3 Modelos del monitor y simulación trófica

La comparación B del monitor usa **biomasa interpolada de anchoveta** como respuesta. RMSE de validación: B0 local 3.379.931 t; B1 con clorofila 2.093.508 t; B2 con carbono 3.324.172 t; B3 con productividad combinada 1.503.102 t. Son métricas del monitor, no pruebas observacionales de efectos ambientales sobre biomasa.

El sistema dinámico F–Z–A utiliza carbono fitoplanctónico, zooplancton y anchoveta. F y Z tienen unidades/definiciones verticales diferentes en las fuentes; las calibraciones normalizadas sirven para exploración, no tasas biológicas validadas. Los escenarios septiembre de 2026–febrero de 2027 son simulaciones, no observaciones.

El nombre «Experimento C» aparece en dos contextos: cadena trófica del monitor e incorporación de conectividad en los modelos estadísticos. No son el mismo experimento.

Castillo et al. (2025), sobre El Niño 2023, analiza condiciones locales de Humboldt y distribución de anchoveta; emplea clorofila VIIRS/NPP y observaciones de cruceros. No plantea ni prueba la conexión Antártida–Humboldt. Sirve como antecedente local, no como evidencia de la conexión regional.

## 9. Conclusiones y próximos pasos

1. **Priorizar El Niño y carbono/pigmento peruano.** Mostrar la asociación y sus límites; evaluar nuevas observaciones, incertidumbre de las mejoras y condiciones operativas de predicción.
2. **Comparar mezcla y biomasa entre regiones.** Bellingshausen y Pacífico Sur ofrecen preguntas locales con soporte en el modelo; Perú y Península proporcionan contrastes negativos que deben mostrarse.
3. **Separar pigmento de biomasa y productividad.** Validar `phyc` y el cociente con carbono satelital o in situ, sin asumir que POC sea exclusivamente fitoplancton.
4. **Validar tendencias con autocorrelación y años completos.** Priorizar nivel del mar; repetir hasta 2025; comprobar fuentes y movimiento vertical costero antes de comparar mareógrafos con modelos.
5. **Armonizar cajas espaciales.** Extraer campos físicos y satelitales para dominios comparables; ampliar Giovanni a Callao, Pisco, Ilo y zonas antárticas si hay cobertura suficiente.
6. **Mantener la respuesta de anchoveta separada.** Más campañas con fechas/stock y datos espaciales son necesarias para asociar ambiente y biomasa observada.
7. **Presentar la conexión Antártida–Perú como pregunta sin respaldo robusto actual.** No reinterpretar correlaciones locales o tendencias paralelas como transporte ni causalidad.

El reto de tendencias puede cubrirse mostrando variables, región, serie temporal, tasas, pruebas y sensibilidad. Un resultado no significativo es parte del producto científico, no un motivo para ocultar una región o escoger otro inicio hasta obtener significancia.

## 10. Reproducción, procedencia y verificación

Desde `data_treatment`:

```bash
# Carbono antártico frente a carbono peruano.
uv run python scripts/18_test_phytoplankton_carbon_connectivity.py

# Exploración ecológica de 33 relaciones, sensibilidades y evaluación condicional.
uv run python scripts/19_investigate_ecosystem_relationships.py

# Verificación de ambos scripts.
uv run python -m unittest discover -s tests -v
```

Ambos scripts usan datos locales y no requieren Colab ni nuevas descargas para estas corridas. Se verificaron siete pruebas automatizadas: HAC con/sin huecos, sentido del rezago, unidades, duplicados/constantes, FDR, extracción de mezcla, cobertura NASA, control ENSO y entrenamiento temporal. Algunas pruebas cubren más de una propiedad.

La ronda `docs/pruebas_pendientes/ronda_seis_variables.py` usa rutas absolutas de Windows; ajustar `R` y proporcionar mareógrafos PSMSL, archivos mensuales NSIDC, ERSST y datos de viento antes de ejecutarla. Esta consolidación no modifica los scripts históricos ni recalcula los contrastes con métodos nuevos.

Las entradas procesadas de los scripts recientes y sus salidas están en `data/processed/analysis/`. Cada corrida guarda configuración y hashes de entradas. Esas carpetas pueden no estar versionadas; los anexos de este documento preservan los valores consolidados. La ronda de tendencias tiene su CSV y consola versionados en `data/tablas_pruebas_pendientes/`.

**Nivel de comprobación:** cifras recientes leídas de CSV; FDR de las 162 tendencias recalculada; nueve pruebas del panel reproducidas. Los resultados históricos no reproducidos aquí se identifican como documentados. No se suman familias ni se reemplazan métodos para obtener un veredicto favorable.

## 11. Fuentes científicas y catálogos

- Luz, nutrientes y cambios en pigmento por carbono frente a Callao: [Thielecke et al. (2025)](https://epub.ub.uni-muenchen.de/129214/). Respaldo de hipótesis local, no validación de nuestras correlaciones regionales.
- Cambios físicos y biogeoquímicos durante El Niño en Perú: [Espinoza-Morriberón et al. (2017)](https://doi.org/10.1002/2016JC012439). Respalda estudiar suministro de nutrientes y mezcla en conjunto.
- Diferencias entre indicadores ópticos y carbono en Océano Austral: [estudio de SOTS (2019)](https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2019.00595/full). Su ubicación no equivale a las cajas de Península/Bellingshausen.
- Datos modelados: [CMEMS BGC](https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_BGC_001_029/description); física CMEMS/GLORYS. Clorofila satelital: ESA OC-CCI v6 y NASA MODIS-Aqua L3m CHL v2022.0 vía Giovanni. Temperatura: NOAA CRW v3.1 y ERSST v5. Atmósfera: ERA5 y NASA POWER. Hielo: NSIDC G02135. Índices: NOAA PSL, IGP/ENFEN. Pesca: IMARPE, RAM Legacy v4.44, BCRP/PRODUCE y FAO GlobalProduction 2026.1.
- La API CMR confirmó carbono satelital específico: [MODISA_L4b_CARBON](https://search.earthdata.nasa.gov/search/granules?p=C3455985653-OB_CLOUD), desde julio de 2002, y [VIIRSN_L4b_CARBON](https://search.earthdata.nasa.gov/search/granules?p=C3455986117-OB_CLOUD), desde enero de 2012. No se encontraron descargados localmente; no se utilizaron en los contrastes reportados. El producto MODIS tuvo una corrección y fue descrito como provisional por [OB.DAAC en 2025](https://forum.earthdata.nasa.gov/viewtopic.php?t=6481); verificar versión y calidad antes de usarlo.

## 12. Anexos de resultados completos

Los anexos incluyen resultados positivos y negativos. Los p/q no se redondean a cero: se usa notación científica cuando corresponde. En tablas, «—» significa que el dato no aplica o no está disponible.

### A. Las 33 relaciones ecológicas: estimación y evaluación temporal

Fuente: `data/processed/analysis/ecosystem_relationships/summary.csv`. Filas: 33.

| ID | Predictor | Respuesta | Rezago meses | Tipo de evidencia | n | β est. | IC95 inf. | IC95 sup. | r parcial | p HAC | q FDR | Todas las sensibilidades | Mejora RMSE cond. % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H01 | nino12 | occci:paita | 0 | climate_index_vs_satellite | 336 | -0.024784 | -0.217573 | 0.168005 | -0.024782 | 0.800496 | 0.852141 | no | -4.188915 |
| H02 | nino12 | occci:chimbote | 0 | climate_index_vs_satellite | 334 | -0.404944 | -0.536671 | -0.273217 | -0.406178 | 4.088e-09 | 3.3726e-08 | sí | 13.626709 |
| H03 | nino12 | occci:callao | 0 | climate_index_vs_satellite | 335 | -0.388068 | -0.512632 | -0.263504 | -0.387916 | 2.5876e-09 | 2.8464e-08 | sí | 12.798529 |
| H04 | nino12 | occci:pisco | 0 | climate_index_vs_satellite | 336 | -0.137135 | -0.310253 | 0.035984 | -0.137771 | 0.120114 | 0.220209 | no | 1.13844 |
| H05 | nino12 | occci:ilo | 0 | climate_index_vs_satellite | 336 | -0.160971 | -0.278369 | -0.043573 | -0.164439 | 0.007353 | 0.016176 | no | 1.760505 |
| H06 | nino12 | modis:chimbote | 0 | climate_index_vs_satellite | 281 | -0.145254 | -0.265623 | -0.024884 | -0.144015 | 0.018211 | 0.037561 | no | 1.091381 |
| H07 | nino12 | modis:paita | 0 | climate_index_vs_satellite | 281 | -0.047048 | -0.171381 | 0.077284 | -0.047853 | 0.456902 | 0.638745 | no | -1.664957 |
| H08 | nino12 | peru_humboldt:phyc | 0 | climate_index_vs_model | 336 | -0.461183 | -0.618861 | -0.303505 | -0.537271 | 2.027e-08 | 1.3378e-07 | sí | 14.962484 |
| H09 | peninsula_antarctica:mlotst | peninsula_antarctica:phyc | 0 | same_model | 336 | -0.046326 | -0.17453 | 0.081878 | -0.0456 | 0.477655 | 0.638745 | no | 0.038285 |
| H10 | bellingshausen:mlotst | bellingshausen:phyc | 0 | same_model | 336 | -0.230386 | -0.351699 | -0.109073 | -0.225515 | 0.000221 | 0.0007293 | sí | 2.07448 |
| H11 | peru_humboldt:mlotst | peru_humboldt:phyc | 0 | same_model | 336 | -0.036317 | -0.17222 | 0.099585 | -0.049452 | 0.599428 | 0.706469 | no | -0.775365 |
| H12 | south_pacific_intermediate:mlotst | south_pacific_intermediate:phyc | 0 | same_model | 336 | -0.396874 | -0.57435 | -0.219398 | -0.394568 | 1.4783e-05 | 6.9694e-05 | sí | 8.035156 |
| H13 | south_pacific_subtropical:mlotst | south_pacific_subtropical:phyc | 0 | same_model | 336 | -0.491488 | -0.605968 | -0.377009 | -0.450616 | 1.0554e-15 | 1.7413e-14 | sí | 7.409805 |
| H14 | transition_humboldt:mlotst | transition_humboldt:phyc | 0 | same_model | 336 | 0.148005 | 0.006316 | 0.289693 | 0.151657 | 0.040679 | 0.078966 | no | 0.759391 |
| H15 | peru_humboldt:mlotst | occci:paita | 0 | model_vs_satellite | 336 | 0.061454 | -0.081198 | 0.204107 | 0.060596 | 0.397323 | 0.595984 | no | -1.399527 |
| H16 | peru_humboldt:mlotst | occci:chimbote | 0 | model_vs_satellite | 334 | -0.186008 | -0.295535 | -0.076481 | -0.201224 | 0.00093302 | 0.002368 | no | 3.270729 |
| H17 | peru_humboldt:mlotst | occci:callao | 0 | model_vs_satellite | 335 | -0.072566 | -0.182107 | 0.036974 | -0.077575 | 0.193398 | 0.319106 | no | -0.314301 |
| H18 | peru_humboldt:mlotst | occci:pisco | 0 | model_vs_satellite | 336 | 0.001622 | -0.086528 | 0.089772 | 0.001622 | 0.971137 | 0.971137 | no | -0.457846 |
| H19 | peru_humboldt:mlotst | occci:ilo | 0 | model_vs_satellite | 336 | -0.042285 | -0.184223 | 0.099653 | -0.04317 | 0.558214 | 0.706469 | no | -0.776412 |
| H20 | peru_humboldt:mlotst | modis:chimbote | 0 | model_vs_satellite | 281 | -0.173953 | -0.26851 | -0.079395 | -0.175571 | 0.00034986 | 0.00096211 | no | 1.779938 |
| H21 | peru_humboldt:mlotst | modis:paita | 0 | model_vs_satellite | 281 | -0.049964 | -0.190294 | 0.090366 | -0.051252 | 0.483898 | 0.638745 | no | -0.423284 |
| H22 | peninsula_antarctica:mlotst | occci:peninsula_antartica | 0 | model_vs_satellite | 245 | 0.092149 | -0.030101 | 0.214398 | 0.089811 | 0.138874 | 0.241203 | no | 0.223671 |
| H23 | peninsula_antarctica:mlotst | occci:rey_jorge | 0 | model_vs_satellite | 226 | 0.028718 | -0.105619 | 0.163055 | 0.028016 | 0.673902 | 0.759014 | no | -0.553177 |
| H24 | peninsula_antarctica:no3 | peninsula_antarctica:phyc | 1 | same_model | 335 | -0.015493 | -0.163512 | 0.132527 | -0.012267 | 0.836983 | 0.863139 | no | -0.86522 |
| H25 | bellingshausen:no3 | bellingshausen:phyc | 1 | same_model | 335 | 0.325234 | 0.151474 | 0.498994 | 0.218748 | 0.00027115 | 0.00081345 | no | 0.032757 |
| H26 | peru_humboldt:no3 | peru_humboldt:phyc | 1 | same_model | 335 | 0.025499 | -0.10017 | 0.151168 | 0.028775 | 0.690013 | 0.759014 | no | -1.053029 |
| H27 | south_pacific_intermediate:no3 | south_pacific_intermediate:phyc | 1 | same_model | 335 | 0.071117 | -0.071125 | 0.213359 | 0.070293 | 0.326026 | 0.512327 | no | -0.226038 |
| H28 | south_pacific_subtropical:no3 | south_pacific_subtropical:phyc | 1 | same_model | 335 | 0.340459 | 0.172249 | 0.508669 | 0.315657 | 8.4652e-05 | 0.00031039 | sí | 6.304357 |
| H29 | transition_humboldt:no3 | transition_humboldt:phyc | 1 | same_model | 335 | 0.489844 | 0.304009 | 0.675678 | 0.514795 | 3.8254e-07 | 2.104e-06 | sí | -266.843944 |
| H30 | peru_humboldt:thermal_gradient | peru_humboldt:phyc | 0 | same_model | 336 | -0.040618 | -0.187673 | 0.106437 | -0.043177 | 0.587229 | 0.706469 | no | -0.920308 |
| H31 | peninsula_antarctica:mlotst | peninsula_antarctica:log_chl_carbon | 0 | same_model_derived_ratio | 336 | 0.188697 | 0.062075 | 0.315319 | 0.179 | 0.003611 | 0.008513 | no | 2.27243 |
| H32 | bellingshausen:mlotst | bellingshausen:log_chl_carbon | 0 | same_model_derived_ratio | 336 | 0.334515 | 0.175517 | 0.493514 | 0.332529 | 4.4592e-05 | 0.00018394 | no | 6.761994 |
| H33 | peru_humboldt:mlotst | peru_humboldt:log_chl_carbon | 0 | same_model_derived_ratio | 336 | 0.483092 | 0.387403 | 0.578781 | 0.477037 | 1.8995e-20 | 6.2682e-19 | sí | 13.217887 |

Los códigos `same_model` y `same_model_derived_ratio` identifican relaciones internas o derivadas de CMEMS; `model_vs_satellite` compara productos físicos modelados con pigmento satelital. Las clases con `climate_index` usan un índice climático como predictor. Estos códigos no garantizan independencia de fuentes.

### B. Sensibilidades completas de las 33 relaciones

Fuente: `data/processed/analysis/ecosystem_relationships/all_results.csv`. Filas: 165.

<details>
<summary>Desplegar las 165 filas: periodos, exclusión de 1998 y anchos HAC</summary>

| ID | Escenario | HAC meses | n | Estado | β est. | IC95 inf. | IC95 sup. | r parcial | p HAC | q FDR | Significativa |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H01 | early | 12 | 168 | ok | -0.267671 | -0.460908 | -0.074433 | -0.262584 | 0.006942 | 0.022907 | sí |
| H02 | early | 12 | 166 | ok | -0.329268 | -0.554645 | -0.103891 | -0.324489 | 0.004464 | 0.016369 | sí |
| H03 | early | 12 | 167 | ok | -0.270127 | -0.478712 | -0.061542 | -0.272479 | 0.011484 | 0.031582 | sí |
| H04 | early | 12 | 168 | ok | -0.05341 | -0.265853 | 0.159032 | -0.055339 | 0.620138 | 0.660147 | no |
| H05 | early | 12 | 168 | ok | -0.140738 | -0.375744 | 0.094269 | -0.139316 | 0.238611 | 0.37496 | no |
| H06 | early | 12 | 114 | ok | -0.044187 | -0.194234 | 0.105859 | -0.04869 | 0.56036 | 0.65613 | no |
| H07 | early | 12 | 114 | ok | -0.29938 | -0.413802 | -0.184958 | -0.299272 | 1.101e-06 | 1.2112e-05 | sí |
| H08 | early | 12 | 168 | ok | -0.511619 | -0.774092 | -0.249147 | -0.559936 | 0.00017232 | 0.00081238 | sí |
| H09 | early | 12 | 168 | ok | -0.056969 | -0.258106 | 0.144167 | -0.056683 | 0.576599 | 0.65613 | no |
| H10 | early | 12 | 168 | ok | -0.215792 | -0.379813 | -0.05177 | -0.217543 | 0.01026 | 0.03078 | sí |
| H11 | early | 12 | 168 | ok | -0.003215 | -0.11749 | 0.11106 | -0.004195 | 0.955752 | 0.955752 | no |
| H12 | early | 12 | 168 | ok | -0.337508 | -0.492153 | -0.182864 | -0.330051 | 2.8907e-05 | 0.00019079 | sí |
| H13 | early | 12 | 168 | ok | -0.52677 | -0.663517 | -0.390022 | -0.517409 | 2.6122e-12 | 4.3102e-11 | sí |
| H14 | early | 12 | 168 | ok | 0.137229 | 0.006863 | 0.267596 | 0.176511 | 0.039231 | 0.099587 | no |
| H15 | early | 12 | 168 | ok | 0.180969 | -0.091834 | 0.453772 | 0.181747 | 0.191975 | 0.329825 | no |
| H16 | early | 12 | 166 | ok | -0.152118 | -0.308967 | 0.00473 | -0.156982 | 0.057227 | 0.134893 | no |
| H17 | early | 12 | 167 | ok | -0.101653 | -0.250536 | 0.04723 | -0.105496 | 0.17936 | 0.329825 | no |
| H18 | early | 12 | 168 | ok | 0.037039 | -0.102196 | 0.176275 | 0.037968 | 0.599964 | 0.65996 | no |
| H19 | early | 12 | 168 | ok | 0.042891 | -0.071906 | 0.157689 | 0.042355 | 0.461564 | 0.585832 | no |
| H20 | early | 12 | 114 | ok | -0.114773 | -0.289825 | 0.060279 | -0.123153 | 0.196296 | 0.329825 | no |
| H21 | early | 12 | 114 | ok | -0.088651 | -0.26396 | 0.086658 | -0.090334 | 0.318121 | 0.471235 | no |
| H22 | early | 12 | 124 | ok | -0.052234 | -0.228613 | 0.124145 | -0.052926 | 0.558538 | 0.65613 | no |
| H23 | early | 12 | 113 | ok | -0.11801 | -0.274491 | 0.038471 | -0.11798 | 0.137765 | 0.28414 | no |
| H24 | early | 12 | 167 | ok | 0.027944 | -0.110536 | 0.166424 | 0.026795 | 0.690678 | 0.712262 | no |
| H25 | early | 12 | 167 | ok | 0.349537 | 0.180678 | 0.518397 | 0.322365 | 6.9964e-05 | 0.0003848 | sí |
| H26 | early | 12 | 167 | ok | 0.167552 | -0.170101 | 0.505205 | 0.136775 | 0.328437 | 0.471235 | no |
| H27 | early | 12 | 167 | ok | 0.083499 | -0.10815 | 0.275147 | 0.063591 | 0.390696 | 0.515719 | no |
| H28 | early | 12 | 167 | ok | 0.367403 | 0.126161 | 0.608645 | 0.226467 | 0.003072 | 0.01267 | sí |
| H29 | early | 12 | 167 | ok | 0.530872 | 0.410499 | 0.651244 | 0.631762 | 4.8633e-15 | 1.6049e-13 | sí |
| H30 | early | 12 | 168 | ok | -0.135267 | -0.312923 | 0.04239 | -0.155786 | 0.134591 | 0.28414 | no |
| H31 | early | 12 | 168 | ok | 0.147316 | -0.078747 | 0.37338 | 0.147035 | 0.199894 | 0.329825 | no |
| H32 | early | 12 | 168 | ok | 0.08137 | -0.099885 | 0.262625 | 0.083435 | 0.376529 | 0.515719 | no |
| H33 | early | 12 | 168 | ok | 0.425414 | 0.254679 | 0.59615 | 0.447817 | 2.1897e-06 | 1.8065e-05 | sí |
| H01 | late | 12 | 168 | ok | 0.144389 | -0.089566 | 0.378345 | 0.144691 | 0.224632 | 0.352993 | no |
| H02 | late | 12 | 168 | ok | -0.494365 | -0.649398 | -0.339332 | -0.495338 | 2.9834e-09 | 3.2818e-08 | sí |
| H03 | late | 12 | 168 | ok | -0.476354 | -0.622866 | -0.329843 | -0.476024 | 1.5781e-09 | 2.6038e-08 | sí |
| H04 | late | 12 | 168 | ok | -0.146091 | -0.369816 | 0.077634 | -0.147167 | 0.198991 | 0.328335 | no |
| H05 | late | 12 | 168 | ok | -0.178892 | -0.33941 | -0.018375 | -0.182801 | 0.029179 | 0.068779 | no |
| H06 | late | 12 | 167 | ok | -0.159096 | -0.350226 | 0.032034 | -0.169407 | 0.102131 | 0.210644 | no |
| H07 | late | 12 | 167 | ok | 0.043406 | -0.09597 | 0.182783 | 0.044571 | 0.539296 | 0.593885 | no |
| H08 | late | 12 | 168 | ok | -0.558198 | -0.747571 | -0.368826 | -0.597957 | 3.2575e-08 | 2.6874e-07 | sí |
| H09 | late | 12 | 168 | ok | 0.078685 | -0.065367 | 0.222738 | 0.064641 | 0.282231 | 0.404941 | no |
| H10 | late | 12 | 168 | ok | -0.33421 | -0.603775 | -0.064646 | -0.2814 | 0.015439 | 0.046318 | sí |
| H11 | late | 12 | 168 | ok | -0.00016249 | -0.194209 | 0.193884 | -0.00021111 | 0.998682 | 0.998682 | no |
| H12 | late | 12 | 168 | ok | -0.431153 | -0.656468 | -0.205839 | -0.418892 | 0.00022395 | 0.00092379 | sí |
| H13 | late | 12 | 168 | ok | -0.375317 | -0.535703 | -0.214931 | -0.3478 | 7.9861e-06 | 4.3924e-05 | sí |
| H14 | late | 12 | 168 | ok | 0.130874 | -0.0547 | 0.316449 | 0.144607 | 0.165561 | 0.303529 | no |
| H15 | late | 12 | 168 | ok | 0.008168 | -0.151071 | 0.167406 | 0.008041 | 0.919418 | 0.94815 | no |
| H16 | late | 12 | 168 | ok | -0.286814 | -0.401541 | -0.172087 | -0.321587 | 2.0364e-06 | 1.3441e-05 | sí |
| H17 | late | 12 | 168 | ok | -0.075728 | -0.210547 | 0.05909 | -0.08365 | 0.268869 | 0.403304 | no |
| H18 | late | 12 | 168 | ok | -0.045408 | -0.165838 | 0.075022 | -0.044956 | 0.457475 | 0.54433 | no |
| H19 | late | 12 | 168 | ok | -0.101441 | -0.37312 | 0.170239 | -0.102493 | 0.461856 | 0.54433 | no |
| H20 | late | 12 | 167 | ok | -0.119614 | -0.222854 | -0.016374 | -0.125686 | 0.023454 | 0.064499 | no |
| H21 | late | 12 | 167 | ok | -0.056326 | -0.250163 | 0.137512 | -0.056305 | 0.566748 | 0.603312 | no |
| H22 | late | 12 | 121 | ok | 0.239052 | -0.005807 | 0.483911 | 0.213078 | 0.055586 | 0.12229 | no |
| H23 | late | 12 | 113 | ok | 0.062806 | -0.139758 | 0.26537 | 0.056748 | 0.539895 | 0.593885 | no |
| H24 | late | 12 | 168 | ok | 0.200986 | -0.047927 | 0.449899 | 0.11102 | 0.112726 | 0.218821 | no |
| H25 | late | 12 | 168 | ok | 0.293394 | 0.036371 | 0.550417 | 0.163745 | 0.025544 | 0.064842 | no |
| H26 | late | 12 | 168 | ok | 0.06815 | -0.094695 | 0.230996 | 0.084537 | 0.409633 | 0.540716 | no |
| H27 | late | 12 | 168 | ok | 0.110245 | -0.10395 | 0.32444 | 0.106978 | 0.310827 | 0.427387 | no |
| H28 | late | 12 | 168 | ok | 0.281624 | 0.112086 | 0.451163 | 0.304862 | 0.001279 | 0.004691 | sí |
| H29 | late | 12 | 168 | ok | 0.435085 | 0.218885 | 0.651285 | 0.498018 | 0.00010809 | 0.00050956 | sí |
| H30 | late | 12 | 168 | ok | 0.108532 | -0.051183 | 0.268247 | 0.097188 | 0.181427 | 0.31511 | no |
| H31 | late | 12 | 168 | ok | 0.061339 | -0.096844 | 0.219523 | 0.054301 | 0.444809 | 0.54433 | no |
| H32 | late | 12 | 168 | ok | 0.278332 | 0.084137 | 0.472526 | 0.277436 | 0.005256 | 0.017344 | sí |
| H33 | late | 12 | 168 | ok | 0.451972 | 0.339145 | 0.564799 | 0.523871 | 4.6857e-13 | 1.5463e-11 | sí |
| H01 | without_1998 | 12 | 324 | ok | 0.012033 | -0.177693 | 0.201758 | 0.011807 | 0.900769 | 0.958883 | no |
| H02 | without_1998 | 12 | 322 | ok | -0.317717 | -0.429009 | -0.206424 | -0.31716 | 4.3372e-08 | 3.5782e-07 | sí |
| H03 | without_1998 | 12 | 323 | ok | -0.313399 | -0.434521 | -0.192277 | -0.30783 | 6.1933e-07 | 3.4063e-06 | sí |
| H04 | without_1998 | 12 | 324 | ok | -0.051175 | -0.209852 | 0.107501 | -0.050918 | 0.526163 | 0.694535 | no |
| H05 | without_1998 | 12 | 324 | ok | -0.101179 | -0.227938 | 0.02558 | -0.100562 | 0.117302 | 0.215054 | no |
| H06 | without_1998 | 12 | 281 | ok | -0.145254 | -0.265623 | -0.024884 | -0.144015 | 0.018211 | 0.037561 | sí |
| H07 | without_1998 | 12 | 281 | ok | -0.047048 | -0.171381 | 0.077284 | -0.047853 | 0.456902 | 0.66536 | no |
| H08 | without_1998 | 12 | 324 | ok | -0.514242 | -0.63228 | -0.396204 | -0.573547 | 4.8916e-16 | 5.3807e-15 | sí |
| H09 | without_1998 | 12 | 324 | ok | 0.017032 | -0.102375 | 0.136439 | 0.016369 | 0.779155 | 0.876263 | no |
| H10 | without_1998 | 12 | 324 | ok | -0.243965 | -0.375636 | -0.112295 | -0.233345 | 0.00031268 | 0.00093804 | sí |
| H11 | without_1998 | 12 | 324 | ok | -0.047256 | -0.177094 | 0.082582 | -0.065278 | 0.474432 | 0.66536 | no |
| H12 | without_1998 | 12 | 324 | ok | -0.369301 | -0.551772 | -0.18683 | -0.366992 | 8.5141e-05 | 0.00035121 | sí |
| H13 | without_1998 | 12 | 324 | ok | -0.478968 | -0.581634 | -0.376302 | -0.438348 | 6.3867e-18 | 1.0538e-16 | sí |
| H14 | without_1998 | 12 | 324 | ok | 0.191878 | 0.041212 | 0.342545 | 0.185541 | 0.012728 | 0.028002 | sí |
| H15 | without_1998 | 12 | 324 | ok | 0.016501 | -0.099804 | 0.132805 | 0.016427 | 0.780308 | 0.876263 | no |
| H16 | without_1998 | 12 | 322 | ok | -0.211554 | -0.30374 | -0.119367 | -0.225746 | 9.0113e-06 | 4.2482e-05 | sí |
| H17 | without_1998 | 12 | 323 | ok | -0.084265 | -0.187653 | 0.019124 | -0.088336 | 0.109799 | 0.213138 | no |
| H18 | without_1998 | 12 | 324 | ok | -0.003873 | -0.099386 | 0.091641 | -0.003914 | 0.936462 | 0.965727 | no |
| H19 | without_1998 | 12 | 324 | ok | -0.025977 | -0.193803 | 0.14185 | -0.026327 | 0.760906 | 0.876263 | no |
| H20 | without_1998 | 12 | 281 | ok | -0.173953 | -0.26851 | -0.079395 | -0.175571 | 0.00034986 | 0.00096211 | sí |
| H21 | without_1998 | 12 | 281 | ok | -0.049964 | -0.190294 | 0.090366 | -0.051252 | 0.483898 | 0.66536 | no |
| H22 | without_1998 | 12 | 236 | ok | 0.086832 | -0.042564 | 0.216229 | 0.083161 | 0.187386 | 0.325459 | no |
| H23 | without_1998 | 12 | 218 | ok | 0.017591 | -0.116791 | 0.151972 | 0.016958 | 0.796603 | 0.876263 | no |
| H24 | without_1998 | 12 | 323 | ok | 0.026825 | -0.116378 | 0.170028 | 0.018416 | 0.712681 | 0.876263 | no |
| H25 | without_1998 | 12 | 323 | ok | 0.378319 | 0.175203 | 0.581435 | 0.203028 | 0.0002913 | 0.00093804 | sí |
| H26 | without_1998 | 12 | 323 | ok | 0.00057219 | -0.114649 | 0.115794 | 0.00068001 | 0.99221 | 0.99221 | no |
| H27 | without_1998 | 12 | 323 | ok | 0.082998 | -0.059013 | 0.225009 | 0.081426 | 0.251024 | 0.394466 | no |
| H28 | without_1998 | 12 | 323 | ok | 0.262895 | 0.104252 | 0.421539 | 0.261684 | 0.001236 | 0.002913 | sí |
| H29 | without_1998 | 12 | 323 | ok | 0.500236 | 0.307842 | 0.692629 | 0.515419 | 5.5039e-07 | 3.4063e-06 | sí |
| H30 | without_1998 | 12 | 324 | ok | 0.065538 | -0.037915 | 0.168991 | 0.0633 | 0.213512 | 0.352294 | no |
| H31 | without_1998 | 12 | 324 | ok | 0.238347 | 0.106095 | 0.370599 | 0.218239 | 0.00045142 | 0.001146 | sí |
| H32 | without_1998 | 12 | 324 | ok | 0.329023 | 0.161576 | 0.496469 | 0.323536 | 0.0001347 | 0.00049389 | sí |
| H33 | without_1998 | 12 | 324 | ok | 0.48223 | 0.386705 | 0.577755 | 0.480112 | 2.3252e-20 | 7.6733e-19 | sí |
| H01 | HAC6 | 6 | 336 | ok | -0.024784 | -0.227594 | 0.178026 | -0.024782 | 0.810159 | 0.862428 | no |
| H02 | HAC6 | 6 | 334 | ok | -0.404944 | -0.551302 | -0.258587 | -0.406178 | 1.0419e-07 | 6.8766e-07 | sí |
| H03 | HAC6 | 6 | 335 | ok | -0.388068 | -0.521192 | -0.254944 | -0.387916 | 2.2512e-08 | 1.8573e-07 | sí |
| H04 | HAC6 | 6 | 336 | ok | -0.137135 | -0.325117 | 0.050848 | -0.137771 | 0.1522 | 0.266545 | no |
| H05 | HAC6 | 6 | 336 | ok | -0.160971 | -0.284687 | -0.037255 | -0.164439 | 0.01093 | 0.024046 | sí |
| H06 | HAC6 | 6 | 281 | ok | -0.145254 | -0.279842 | -0.010666 | -0.144015 | 0.034512 | 0.066994 | no |
| H07 | HAC6 | 6 | 281 | ok | -0.047048 | -0.170947 | 0.076851 | -0.047853 | 0.455331 | 0.62608 | no |
| H08 | HAC6 | 6 | 336 | ok | -0.461183 | -0.618011 | -0.304355 | -0.537271 | 1.7141e-08 | 1.8573e-07 | sí |
| H09 | HAC6 | 6 | 336 | ok | -0.046326 | -0.168024 | 0.075371 | -0.0456 | 0.454453 | 0.62608 | no |
| H10 | HAC6 | 6 | 336 | ok | -0.230386 | -0.350488 | -0.110285 | -0.225515 | 0.00019135 | 0.00063146 | sí |
| H11 | HAC6 | 6 | 336 | ok | -0.036317 | -0.174866 | 0.102231 | -0.049452 | 0.606414 | 0.714702 | no |
| H12 | HAC6 | 6 | 336 | ok | -0.396874 | -0.583902 | -0.209845 | -0.394568 | 3.8463e-05 | 0.00015866 | sí |
| H13 | HAC6 | 6 | 336 | ok | -0.491488 | -0.617687 | -0.36529 | -0.450616 | 2.183e-13 | 3.602e-12 | sí |
| H14 | HAC6 | 6 | 336 | ok | 0.148005 | 0.018036 | 0.277973 | 0.151657 | 0.025748 | 0.053106 | no |
| H15 | HAC6 | 6 | 336 | ok | 0.061454 | -0.089608 | 0.212517 | 0.060596 | 0.424094 | 0.62608 | no |
| H16 | HAC6 | 6 | 334 | ok | -0.186008 | -0.296953 | -0.075064 | -0.201224 | 0.001082 | 0.002974 | sí |
| H17 | HAC6 | 6 | 335 | ok | -0.072566 | -0.174673 | 0.029541 | -0.077575 | 0.163017 | 0.268978 | no |
| H18 | HAC6 | 6 | 336 | ok | 0.001622 | -0.087715 | 0.090959 | 0.001622 | 0.971521 | 0.971521 | no |
| H19 | HAC6 | 6 | 336 | ok | -0.042285 | -0.175575 | 0.091004 | -0.04317 | 0.53298 | 0.676475 | no |
| H20 | HAC6 | 6 | 281 | ok | -0.173953 | -0.272341 | -0.075564 | -0.175571 | 0.00058348 | 0.00175 | sí |
| H21 | HAC6 | 6 | 281 | ok | -0.049964 | -0.187941 | 0.088013 | -0.051252 | 0.476481 | 0.628955 | no |
| H22 | HAC6 | 6 | 245 | ok | 0.092149 | -0.034627 | 0.218924 | 0.089811 | 0.153466 | 0.266545 | no |
| H23 | HAC6 | 6 | 226 | ok | 0.028718 | -0.10652 | 0.163956 | 0.028016 | 0.67595 | 0.753237 | no |
| H24 | HAC6 | 6 | 335 | ok | -0.015493 | -0.188537 | 0.157552 | -0.012267 | 0.860294 | 0.887178 | no |
| H25 | HAC6 | 6 | 335 | ok | 0.325234 | 0.10118 | 0.549288 | 0.218748 | 0.004573 | 0.010779 | sí |
| H26 | HAC6 | 6 | 335 | ok | 0.025499 | -0.09796 | 0.148958 | 0.028775 | 0.684761 | 0.753237 | no |
| H27 | HAC6 | 6 | 335 | ok | 0.071117 | -0.084439 | 0.226674 | 0.070293 | 0.369081 | 0.579985 | no |
| H28 | HAC6 | 6 | 335 | ok | 0.340459 | 0.166678 | 0.514239 | 0.315657 | 0.00014027 | 0.00051431 | sí |
| H29 | HAC6 | 6 | 335 | ok | 0.489844 | 0.288198 | 0.691489 | 0.514795 | 2.6886e-06 | 1.4787e-05 | sí |
| H30 | HAC6 | 6 | 336 | ok | -0.040618 | -0.187948 | 0.106712 | -0.043177 | 0.587926 | 0.714702 | no |
| H31 | HAC6 | 6 | 336 | ok | 0.188697 | 0.059488 | 0.317906 | 0.179 | 0.004335 | 0.010779 | sí |
| H32 | HAC6 | 6 | 336 | ok | 0.334515 | 0.18031 | 0.488721 | 0.332529 | 2.6016e-05 | 0.00012265 | sí |
| H33 | HAC6 | 6 | 336 | ok | 0.483092 | 0.381271 | 0.584913 | 0.477037 | 1.7375e-18 | 5.7337e-17 | sí |
| H01 | HAC24 | 24 | 336 | ok | -0.024784 | -0.222705 | 0.173137 | -0.024782 | 0.805564 | 0.849212 | no |
| H02 | HAC24 | 24 | 334 | ok | -0.404944 | -0.529386 | -0.280503 | -0.406178 | 5.4554e-10 | 6.001e-09 | sí |
| H03 | HAC24 | 24 | 335 | ok | -0.388068 | -0.511036 | -0.2651 | -0.387916 | 1.6506e-09 | 1.3617e-08 | sí |
| H04 | HAC24 | 24 | 336 | ok | -0.137135 | -0.306582 | 0.032313 | -0.137771 | 0.112323 | 0.205925 | no |
| H05 | HAC24 | 24 | 336 | ok | -0.160971 | -0.267045 | -0.054897 | -0.164439 | 0.003048 | 0.007184 | sí |
| H06 | HAC24 | 24 | 281 | ok | -0.145254 | -0.271486 | -0.019021 | -0.144015 | 0.024279 | 0.050076 | no |
| H07 | HAC24 | 24 | 281 | ok | -0.047048 | -0.189424 | 0.095328 | -0.047853 | 0.515851 | 0.705142 | no |
| H08 | HAC24 | 24 | 336 | ok | -0.461183 | -0.631555 | -0.290811 | -0.537271 | 1.8937e-07 | 1.0415e-06 | sí |
| H09 | HAC24 | 24 | 336 | ok | -0.046326 | -0.177075 | 0.084422 | -0.0456 | 0.486258 | 0.697675 | no |
| H10 | HAC24 | 24 | 336 | ok | -0.230386 | -0.356579 | -0.104193 | -0.225515 | 0.00037985 | 0.001045 | sí |
| H11 | HAC24 | 24 | 336 | ok | -0.036317 | -0.16638 | 0.093745 | -0.049452 | 0.583146 | 0.712733 | no |
| H12 | HAC24 | 24 | 336 | ok | -0.396874 | -0.552527 | -0.241221 | -0.394568 | 8.7366e-07 | 4.1187e-06 | sí |
| H13 | HAC24 | 24 | 336 | ok | -0.491488 | -0.608315 | -0.374662 | -0.450616 | 3.4382e-15 | 5.673e-14 | sí |
| H14 | HAC24 | 24 | 336 | ok | 0.148005 | 0.003042 | 0.292967 | 0.151657 | 0.045409 | 0.088147 | no |
| H15 | HAC24 | 24 | 336 | ok | 0.061454 | -0.083318 | 0.206227 | 0.060596 | 0.404265 | 0.606397 | no |
| H16 | HAC24 | 24 | 334 | ok | -0.186008 | -0.297686 | -0.074331 | -0.201224 | 0.001165 | 0.002958 | sí |
| H17 | HAC24 | 24 | 335 | ok | -0.072566 | -0.196235 | 0.051102 | -0.077575 | 0.249182 | 0.41115 | no |
| H18 | HAC24 | 24 | 336 | ok | 0.001622 | -0.090953 | 0.094198 | 0.001622 | 0.972517 | 0.972517 | no |
| H19 | HAC24 | 24 | 336 | ok | -0.042285 | -0.192655 | 0.108084 | -0.04317 | 0.580482 | 0.712733 | no |
| H20 | HAC24 | 24 | 281 | ok | -0.173953 | -0.26888 | -0.079026 | -0.175571 | 0.00036849 | 0.001045 | sí |
| H21 | HAC24 | 24 | 281 | ok | -0.049964 | -0.208017 | 0.108089 | -0.051252 | 0.534199 | 0.705142 | no |
| H22 | HAC24 | 24 | 245 | ok | 0.092149 | -0.040476 | 0.224773 | 0.089811 | 0.172345 | 0.299335 | no |
| H23 | HAC24 | 24 | 226 | ok | 0.028718 | -0.095179 | 0.152616 | 0.028016 | 0.648219 | 0.737629 | no |
| H24 | HAC24 | 24 | 335 | ok | -0.015493 | -0.152019 | 0.121033 | -0.012267 | 0.823478 | 0.849212 | no |
| H25 | HAC24 | 24 | 335 | ok | 0.325234 | 0.173843 | 0.476624 | 0.218748 | 3.1006e-05 | 0.00012741 | sí |
| H26 | HAC24 | 24 | 335 | ok | 0.025499 | -0.103392 | 0.15439 | 0.028775 | 0.697372 | 0.767109 | no |
| H27 | HAC24 | 24 | 335 | ok | 0.071117 | -0.062276 | 0.204511 | 0.070293 | 0.295012 | 0.46359 | no |
| H28 | HAC24 | 24 | 335 | ok | 0.340459 | 0.180956 | 0.499962 | 0.315657 | 3.4749e-05 | 0.00012741 | sí |
| H29 | HAC24 | 24 | 335 | ok | 0.489844 | 0.311671 | 0.668016 | 0.514795 | 1.2457e-07 | 8.2216e-07 | sí |
| H30 | HAC24 | 24 | 336 | ok | -0.040618 | -0.195159 | 0.113924 | -0.043177 | 0.605457 | 0.713574 | no |
| H31 | HAC24 | 24 | 336 | ok | 0.188697 | 0.06306 | 0.314334 | 0.179 | 0.003359 | 0.007391 | sí |
| H32 | HAC24 | 24 | 336 | ok | 0.334515 | 0.153919 | 0.515111 | 0.332529 | 0.00031277 | 0.001032 | sí |
| H33 | HAC24 | 24 | 336 | ok | 0.483092 | 0.390372 | 0.575812 | 0.477037 | 1.6228e-21 | 5.3551e-20 | sí |

</details>

### C. Los 12 contrastes principales de carbono Antártida–Humboldt

Fuente: `data/processed/analysis/phytoplankton_carbon_connectivity/primary_results.csv`. Filas: 12.

| Origen | Rezago meses | n | β est. | IC95 inf. | IC95 sup. | r parcial | p HAC | q FDR | AC1 residual |
|---|---|---|---|---|---|---|---|---|---|
| peninsula_antarctica | 0 | 312 | 0.034276 | -0.055463 | 0.124016 | 0.045204 | 0.452839 | 0.543407 | 0.594556 |
| peninsula_antarctica | 3 | 312 | -0.083371 | -0.164378 | -0.002364 | -0.1085 | 0.043719 | 0.186487 | 0.584314 |
| peninsula_antarctica | 6 | 312 | -0.041778 | -0.118423 | 0.034867 | -0.054802 | 0.284268 | 0.495915 | 0.594374 |
| peninsula_antarctica | 12 | 312 | 0.042785 | -0.053458 | 0.139027 | 0.056082 | 0.38235 | 0.5098 | 0.594267 |
| peninsula_antarctica | 18 | 312 | -0.094226 | -0.181288 | -0.007164 | -0.122175 | 0.034001 | 0.186487 | 0.586368 |
| peninsula_antarctica | 24 | 312 | -0.060526 | -0.17273 | 0.051678 | -0.081504 | 0.289284 | 0.495915 | 0.593177 |
| bellingshausen | 0 | 312 | 0.032117 | -0.037578 | 0.101812 | 0.044441 | 0.365193 | 0.5098 | 0.594115 |
| bellingshausen | 3 | 312 | 0.00096086 | -0.047665 | 0.049587 | 0.001324 | 0.969006 | 0.969006 | 0.597736 |
| bellingshausen | 6 | 312 | -0.005683 | -0.059714 | 0.048347 | -0.00788 | 0.836141 | 0.912154 | 0.59732 |
| bellingshausen | 12 | 312 | 0.038024 | -0.031647 | 0.107694 | 0.052483 | 0.283668 | 0.495915 | 0.59182 |
| bellingshausen | 18 | 312 | -0.049699 | -0.098651 | -0.00074814 | -0.068315 | 0.046622 | 0.186487 | 0.58461 |
| bellingshausen | 24 | 312 | 0.059976 | -0.017778 | 0.13773 | 0.083655 | 0.13007 | 0.39021 | 0.576871 |

### D. Sensibilidades del contraste Antártida–Humboldt

Fuente: `data/processed/analysis/phytoplankton_carbon_connectivity/sensitivity_results.csv`. Filas: 84.

<details>
<summary>Desplegar las 84 filas, incluidas clorofila y asociación por rangos secundarias</summary>

| Origen | Rezago meses | Familia | n | β est. | IC95 inf. | IC95 sup. | r parcial | p HAC | q FDR | Significativa |
|---|---|---|---|---|---|---|---|---|---|---|
| peninsula_antarctica | 0 | HAC_6 | 312 | 0.034276 | -0.057476 | 0.126028 | 0.045204 | 0.462804 | 0.555365 | no |
| peninsula_antarctica | 3 | HAC_6 | 312 | -0.083371 | -0.166918 | 0.00017597 | -0.1085 | 0.050481 | 0.201925 | no |
| peninsula_antarctica | 6 | HAC_6 | 312 | -0.041778 | -0.118095 | 0.034539 | -0.054802 | 0.282205 | 0.504643 | no |
| peninsula_antarctica | 12 | HAC_6 | 312 | 0.042785 | -0.053982 | 0.139551 | 0.056082 | 0.384928 | 0.513238 | no |
| peninsula_antarctica | 18 | HAC_6 | 312 | -0.094226 | -0.178535 | -0.009917 | -0.122175 | 0.028615 | 0.201925 | no |
| peninsula_antarctica | 24 | HAC_6 | 312 | -0.060526 | -0.172156 | 0.051104 | -0.081504 | 0.286816 | 0.504643 | no |
| bellingshausen | 0 | HAC_6 | 312 | 0.032117 | -0.040348 | 0.104583 | 0.044441 | 0.383787 | 0.513238 | no |
| bellingshausen | 3 | HAC_6 | 312 | 0.00096086 | -0.051591 | 0.053513 | 0.001324 | 0.97132 | 0.97132 | no |
| bellingshausen | 6 | HAC_6 | 312 | -0.005683 | -0.064091 | 0.052724 | -0.00788 | 0.848263 | 0.925378 | no |
| bellingshausen | 12 | HAC_6 | 312 | 0.038024 | -0.033214 | 0.109261 | 0.052483 | 0.294375 | 0.504643 | no |
| bellingshausen | 18 | HAC_6 | 312 | -0.049699 | -0.098675 | -0.00072348 | -0.068315 | 0.046732 | 0.201925 | no |
| bellingshausen | 24 | HAC_6 | 312 | 0.059976 | -0.019523 | 0.139476 | 0.083655 | 0.138685 | 0.416055 | no |
| peninsula_antarctica | 0 | HAC_24 | 312 | 0.034276 | -0.05952 | 0.128073 | 0.045204 | 0.472605 | 0.567126 | no |
| peninsula_antarctica | 3 | HAC_24 | 312 | -0.083371 | -0.163247 | -0.003495 | -0.1085 | 0.040842 | 0.232692 | no |
| peninsula_antarctica | 6 | HAC_24 | 312 | -0.041778 | -0.113076 | 0.02952 | -0.054802 | 0.249768 | 0.505131 | no |
| peninsula_antarctica | 12 | HAC_24 | 312 | 0.042785 | -0.040335 | 0.125904 | 0.056082 | 0.311886 | 0.505131 | no |
| peninsula_antarctica | 18 | HAC_24 | 312 | -0.094226 | -0.185394 | -0.003059 | -0.122175 | 0.042839 | 0.232692 | no |
| peninsula_antarctica | 24 | HAC_24 | 312 | -0.060526 | -0.184326 | 0.063274 | -0.081504 | 0.336754 | 0.505131 | no |
| bellingshausen | 0 | HAC_24 | 312 | 0.032117 | -0.043254 | 0.107489 | 0.044441 | 0.402367 | 0.536489 | no |
| bellingshausen | 3 | HAC_24 | 312 | 0.00096086 | -0.041773 | 0.043695 | 0.001324 | 0.964735 | 0.964735 | no |
| bellingshausen | 6 | HAC_24 | 312 | -0.005683 | -0.05798 | 0.046613 | -0.00788 | 0.830789 | 0.906316 | no |
| bellingshausen | 12 | HAC_24 | 312 | 0.038024 | -0.030066 | 0.106113 | 0.052483 | 0.272663 | 0.505131 | no |
| bellingshausen | 18 | HAC_24 | 312 | -0.049699 | -0.10113 | 0.001731 | -0.068315 | 0.058173 | 0.232692 | no |
| bellingshausen | 24 | HAC_24 | 312 | 0.059976 | -0.020917 | 0.14087 | 0.083655 | 0.145591 | 0.436772 | no |
| peninsula_antarctica | 0 | without_1998 | 312 | 0.034276 | -0.055463 | 0.124016 | 0.045204 | 0.452839 | 0.543407 | no |
| peninsula_antarctica | 3 | without_1998 | 312 | -0.083371 | -0.164378 | -0.002364 | -0.1085 | 0.043719 | 0.457369 | no |
| peninsula_antarctica | 6 | without_1998 | 312 | -0.041778 | -0.118423 | 0.034867 | -0.054802 | 0.284268 | 0.490542 | no |
| peninsula_antarctica | 12 | without_1998 | 312 | 0.042785 | -0.053458 | 0.139027 | 0.056082 | 0.38235 | 0.5098 | no |
| peninsula_antarctica | 18 | without_1998 | 306 | -0.0785 | -0.165331 | 0.00833 | -0.102764 | 0.076228 | 0.457369 | no |
| peninsula_antarctica | 24 | without_1998 | 300 | -0.069127 | -0.171943 | 0.033688 | -0.091271 | 0.186765 | 0.490542 | no |
| bellingshausen | 0 | without_1998 | 312 | 0.032117 | -0.037578 | 0.101812 | 0.044441 | 0.365193 | 0.5098 | no |
| bellingshausen | 3 | without_1998 | 312 | 0.00096086 | -0.047665 | 0.049587 | 0.001324 | 0.969006 | 0.969006 | no |
| bellingshausen | 6 | without_1998 | 312 | -0.005683 | -0.059714 | 0.048347 | -0.00788 | 0.836141 | 0.912154 | no |
| bellingshausen | 12 | without_1998 | 312 | 0.038024 | -0.031647 | 0.107694 | 0.052483 | 0.283668 | 0.490542 | no |
| bellingshausen | 18 | without_1998 | 306 | -0.038751 | -0.089921 | 0.012418 | -0.053742 | 0.137171 | 0.490542 | no |
| bellingshausen | 24 | without_1998 | 300 | 0.042302 | -0.035617 | 0.120221 | 0.059365 | 0.28615 | 0.490542 | no |
| peninsula_antarctica | 0 | first_half | 156 | 0.046986 | -0.048086 | 0.142059 | 0.06212 | 0.330227 | 0.668756 | no |
| peninsula_antarctica | 3 | first_half | 156 | -0.038308 | -0.184236 | 0.107621 | -0.050796 | 0.604582 | 0.725499 | no |
| peninsula_antarctica | 6 | first_half | 156 | -0.074282 | -0.197495 | 0.048932 | -0.100034 | 0.235314 | 0.668756 | no |
| peninsula_antarctica | 12 | first_half | 156 | 0.043717 | -0.072084 | 0.159519 | 0.058338 | 0.456694 | 0.668756 | no |
| peninsula_antarctica | 18 | first_half | 156 | -0.183521 | -0.29479 | -0.072251 | -0.239317 | 0.001395 | 0.016741 | sí |
| peninsula_antarctica | 24 | first_half | 156 | -0.162973 | -0.330346 | 0.0044 | -0.219636 | 0.056247 | 0.337485 | no |
| bellingshausen | 0 | first_half | 156 | 0.036525 | -0.051508 | 0.124559 | 0.049014 | 0.413468 | 0.668756 | no |
| bellingshausen | 3 | first_half | 156 | 0.021114 | -0.080535 | 0.122763 | 0.028312 | 0.681945 | 0.74394 | no |
| bellingshausen | 6 | first_half | 156 | -0.003227 | -0.137702 | 0.131247 | -0.004408 | 0.962226 | 0.962226 | no |
| bellingshausen | 12 | first_half | 156 | 0.041943 | -0.081131 | 0.165018 | 0.056778 | 0.501567 | 0.668756 | no |
| bellingshausen | 18 | first_half | 156 | -0.035808 | -0.126597 | 0.05498 | -0.047235 | 0.436837 | 0.668756 | no |
| bellingshausen | 24 | first_half | 156 | 0.069417 | -0.050441 | 0.189274 | 0.092902 | 0.254152 | 0.668756 | no |
| peninsula_antarctica | 0 | second_half | 156 | 0.003881 | -0.106534 | 0.114296 | 0.005117 | 0.944701 | 0.959549 | no |
| peninsula_antarctica | 3 | second_half | 156 | -0.001689 | -0.06739 | 0.064013 | -0.002196 | 0.959549 | 0.959549 | no |
| peninsula_antarctica | 6 | second_half | 156 | 0.02009 | -0.077716 | 0.117896 | 0.026194 | 0.685294 | 0.959549 | no |
| peninsula_antarctica | 12 | second_half | 156 | 0.037377 | -0.098481 | 0.173236 | 0.04878 | 0.587357 | 0.959549 | no |
| peninsula_antarctica | 18 | second_half | 156 | 0.006244 | -0.102055 | 0.114542 | 0.008105 | 0.909417 | 0.959549 | no |
| peninsula_antarctica | 24 | second_half | 156 | -0.05908 | -0.203374 | 0.085215 | -0.077163 | 0.419612 | 0.89807 | no |
| bellingshausen | 0 | second_half | 156 | 0.020609 | -0.094708 | 0.135926 | 0.027926 | 0.724386 | 0.959549 | no |
| bellingshausen | 3 | second_half | 156 | 0.039304 | -0.01798 | 0.096587 | 0.053283 | 0.177123 | 0.89807 | no |
| bellingshausen | 6 | second_half | 156 | 0.033827 | -0.039275 | 0.106929 | 0.045848 | 0.361837 | 0.89807 | no |
| bellingshausen | 12 | second_half | 156 | 0.049216 | -0.032632 | 0.131065 | 0.066675 | 0.236523 | 0.89807 | no |
| bellingshausen | 18 | second_half | 156 | -0.023502 | -0.084708 | 0.037704 | -0.032158 | 0.449035 | 0.89807 | no |
| bellingshausen | 24 | second_half | 156 | 0.080114 | -0.030942 | 0.191169 | 0.11091 | 0.156032 | 0.89807 | no |
| peninsula_antarctica | 0 | partial_rank_secondary | 312 | 0.037676 | -0.042323 | 0.117676 | 0.04906 | 0.354764 | 0.709527 | no |
| peninsula_antarctica | 3 | partial_rank_secondary | 312 | -0.052216 | -0.151376 | 0.046943 | -0.067384 | 0.300895 | 0.709527 | no |
| peninsula_antarctica | 6 | partial_rank_secondary | 312 | 0.004967 | -0.081867 | 0.091801 | 0.0065 | 0.910445 | 0.955151 | no |
| peninsula_antarctica | 12 | partial_rank_secondary | 312 | 0.029204 | -0.053677 | 0.112085 | 0.038152 | 0.488569 | 0.837547 | no |
| peninsula_antarctica | 18 | partial_rank_secondary | 312 | -0.064438 | -0.178051 | 0.049176 | -0.083402 | 0.265248 | 0.709527 | no |
| peninsula_antarctica | 24 | partial_rank_secondary | 312 | -0.08158 | -0.170173 | 0.007014 | -0.1076 | 0.070967 | 0.621304 | no |
| bellingshausen | 0 | partial_rank_secondary | 312 | 0.061515 | -0.012624 | 0.135654 | 0.084451 | 0.103551 | 0.621304 | no |
| bellingshausen | 3 | partial_rank_secondary | 312 | -0.033196 | -0.099164 | 0.032772 | -0.045787 | 0.322827 | 0.709527 | no |
| bellingshausen | 6 | partial_rank_secondary | 312 | 0.008953 | -0.077112 | 0.095017 | 0.012372 | 0.837933 | 0.955151 | no |
| bellingshausen | 12 | partial_rank_secondary | 312 | 0.008588 | -0.080955 | 0.098131 | 0.011848 | 0.850419 | 0.955151 | no |
| bellingshausen | 18 | partial_rank_secondary | 312 | -0.012848 | -0.093154 | 0.067459 | -0.017742 | 0.753096 | 0.955151 | no |
| bellingshausen | 24 | partial_rank_secondary | 312 | -0.002196 | -0.078983 | 0.074591 | -0.003073 | 0.955151 | 0.955151 | no |
| peninsula_antarctica | 0 | chlorophyll_secondary | 312 | 0.069454 | -0.030336 | 0.169243 | 0.074457 | 0.17181 | 0.294532 | no |
| peninsula_antarctica | 3 | chlorophyll_secondary | 312 | 0.01816 | -0.09232 | 0.128641 | 0.020882 | 0.74655 | 0.74655 | no |
| peninsula_antarctica | 6 | chlorophyll_secondary | 312 | -0.034435 | -0.12205 | 0.05318 | -0.038189 | 0.439858 | 0.527829 | no |
| peninsula_antarctica | 12 | chlorophyll_secondary | 312 | 0.101213 | -0.024558 | 0.226984 | 0.10901 | 0.114321 | 0.228643 | no |
| peninsula_antarctica | 18 | chlorophyll_secondary | 312 | -0.049585 | -0.155761 | 0.056591 | -0.052295 | 0.358808 | 0.484587 | no |
| peninsula_antarctica | 24 | chlorophyll_secondary | 312 | -0.069307 | -0.219157 | 0.080542 | -0.07438 | 0.36344 | 0.484587 | no |
| bellingshausen | 0 | chlorophyll_secondary | 312 | 0.054514 | -0.006505 | 0.115533 | 0.060242 | 0.079749 | 0.228643 | no |
| bellingshausen | 3 | chlorophyll_secondary | 312 | 0.088237 | -0.01691 | 0.193385 | 0.105049 | 0.099696 | 0.228643 | no |
| bellingshausen | 6 | chlorophyll_secondary | 312 | 0.086126 | 0.004494 | 0.167758 | 0.099263 | 0.038725 | 0.154898 | no |
| bellingshausen | 12 | chlorophyll_secondary | 312 | 0.07915 | 0.009623 | 0.148678 | 0.088149 | 0.025807 | 0.154845 | no |
| bellingshausen | 18 | chlorophyll_secondary | 312 | 0.022109 | -0.055201 | 0.099418 | 0.02431 | 0.573993 | 0.626174 | no |
| bellingshausen | 24 | chlorophyll_secondary | 312 | 0.067762 | 0.01355 | 0.121974 | 0.074502 | 0.014469 | 0.154845 | no |

</details>

Las sensibilidades `chlorophyll_secondary` y `partial_rank_secondary` responden a preguntas secundarias y corrigen familias separadas; no se usan para rescatar un resultado principal negativo.

### E. Las 162 pruebas de tendencias: tabla corregida de referencia

Fuente: `data/tablas_pruebas_pendientes/ronda_seis_variables.csv`. Filas: 162.

<details>
<summary>Desplegar todas las variables, periodos, exclusiones e intervalos de Sen</summary>

| Variable | Unidad | Periodo | Inicio | Variante | n años | τ | Sen/década | IC95 inf. | IC95 sup. | p | q FDR | Significativa |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Nivel del mar (GLORYS zos, Humboldt) | m | 1998-2025 | completo | todos los anios | 28 | 0.592593 | 0.025856 | 0.019619 | 0.032875 | 2.6237e-06 | 0.00010626 | sí |
| Nivel del mar (GLORYS zos, Humboldt) | m | 1999-2025 | completo | sin anios Nino extremo | 25 | 0.693333 | 0.025661 | 0.019837 | 0.030875 | 9.9636e-08 | 6.8679e-06 | sí |
| Nivel del mar (GLORYS zos, Humboldt) | m | 2003-2025 | desde 2003 | todos los anios | 23 | 0.644269 | 0.028653 | 0.021109 | 0.039476 | 3.9052e-06 | 0.00012653 | sí |
| Nivel del mar (GLORYS zos, Humboldt) | m | 2003-2025 | desde 2003 | sin anios Nino extremo | 21 | 0.657143 | 0.026475 | 0.019757 | 0.034429 | 7.786e-06 | 0.00021022 | sí |
| Nivel del mar (GLORYS zos, Humboldt) | m | 2010-2025 | desde 2010 | todos los anios | 16 | 0.466667 | 0.026583 | 0.00763 | 0.04866 | 0.011481 | 0.048944 | sí |
| Nivel del mar (GLORYS zos, Humboldt) | m | 2010-2025 | desde 2010 | sin anios Nino extremo | 14 | 0.494505 | 0.022762 | 0.00763 | 0.038593 | 0.013838 | 0.051925 | no |
| Nivel del mar (mareografo Matarani) | m | 1942-1969 | completo | todos los anios | 27 | -0.225071 | -0.009778 | -0.024583 | 0.00299 | 0.104325 | 0.24854 | no |
| Nivel del mar (mareografo Matarani) | m | 1942-1969 | completo | sin anios Nino extremo | 27 | -0.225071 | -0.009778 | -0.024583 | 0.00299 | 0.104325 | 0.24854 | no |
| Nivel del mar (mareografo Matarani) | m | 1950-1969 | desde 1950 | todos los anios | 19 | -0.005848 | -0.00055556 | -0.026667 | 0.025905 | 1 | 1 | no |
| Nivel del mar (mareografo Matarani) | m | 1950-1969 | desde 1950 | sin anios Nino extremo | 19 | -0.005848 | -0.00055556 | -0.026667 | 0.025905 | 1 | 1 | no |
| Nivel del mar (mareografo Talara) | m | 1942-1969 | completo | todos los anios | 28 | 0.16159 | 0.007995 | -0.007083 | 0.024545 | 0.228055 | 0.456111 | no |
| Nivel del mar (mareografo Talara) | m | 1942-1969 | completo | sin anios Nino extremo | 28 | 0.16159 | 0.007995 | -0.007083 | 0.024545 | 0.228055 | 0.456111 | no |
| Nivel del mar (mareografo Talara) | m | 1950-1969 | desde 1950 | todos los anios | 20 | 0.189474 | 0.016826 | -0.016136 | 0.045648 | 0.25984 | 0.495224 | no |
| Nivel del mar (mareografo Talara) | m | 1950-1969 | desde 1950 | sin anios Nino extremo | 20 | 0.189474 | 0.016826 | -0.016136 | 0.045648 | 0.25984 | 0.495224 | no |
| Nivel del mar (mareografo Chimbote) | m | 1955-1968 | completo | todos los anios | 14 | -0.340659 | -0.060208 | -0.183333 | 0.017833 | 0.101021 | 0.24796 | no |
| Nivel del mar (mareografo Chimbote) | m | 1955-1968 | completo | sin anios Nino extremo | 14 | -0.340659 | -0.060208 | -0.183333 | 0.017833 | 0.101021 | 0.24796 | no |
| Nivel del mar (mareografo San Juan) | m | 1958-1968 | completo | todos los anios | 9 | -0.777778 | -0.116545 | -0.158056 | -0.043333 | 0.002425 | 0.017602 | sí |
| Nivel del mar (mareografo San Juan) | m | 1958-1968 | completo | sin anios Nino extremo | 9 | -0.777778 | -0.116545 | -0.158056 | -0.043333 | 0.002425 | 0.017602 | sí |
| Nivel del mar (mareografo Callao) | m | 1970-2024 | completo | todos los anios | 54 | -0.271838 | -0.012639 | -0.02 | -0.005 | 0.003707 | 0.023096 | sí |
| Nivel del mar (mareografo Callao) | m | 1970-2024 | completo | sin anios Nino extremo | 52 | -0.268477 | -0.012972 | -0.020265 | -0.004542 | 0.004966 | 0.027742 | sí |
| Nivel del mar (mareografo Callao) | m | 1998-2024 | desde 1998 | todos los anios | 26 | -0.113846 | -0.012105 | -0.032736 | 0.013264 | 0.431303 | 0.636944 | no |
| Nivel del mar (mareografo Callao) | m | 1999-2024 | desde 1998 | sin anios Nino extremo | 24 | -0.043478 | -0.003498 | -0.029664 | 0.019472 | 0.787272 | 0.891875 | no |
| Nivel del mar (mareografo Callao) | m | 2003-2024 | desde 2003 | todos los anios | 21 | -0.114286 | -0.015278 | -0.045598 | 0.0196 | 0.492075 | 0.687208 | no |
| Nivel del mar (mareografo Callao) | m | 2003-2024 | desde 2003 | sin anios Nino extremo | 20 | -0.084211 | -0.013449 | -0.043056 | 0.032628 | 0.630799 | 0.798355 | no |
| Nivel del mar (mareografo Callao) | m | 2010-2024 | desde 2010 | todos los anios | 14 | -0.604396 | -0.074015 | -0.11765 | -0.033036 | 0.001957 | 0.017602 | sí |
| Nivel del mar (mareografo Callao) | m | 2010-2024 | desde 2010 | sin anios Nino extremo | 13 | -0.564103 | -0.074424 | -0.1325 | -0.020625 | 0.006677 | 0.035234 | sí |
| Nivel del mar (mareografo Callao) | m | 1979-2024 | desde 1979 | todos los anios | 45 | -0.369697 | -0.016607 | -0.024167 | -0.008186 | 0.00034316 | 0.006177 | sí |
| Nivel del mar (mareografo Callao) | m | 1979-2024 | desde 1979 | sin anios Nino extremo | 43 | -0.370986 | -0.017 | -0.024524 | -0.008406 | 0.00045504 | 0.007372 | sí |
| Nivel del mar (mareografo Callao) | m | 1980-2024 | desde 1980 | todos los anios | 44 | -0.35518 | -0.016274 | -0.024919 | -0.007628 | 0.00067783 | 0.009983 | sí |
| Nivel del mar (mareografo Callao) | m | 1980-2024 | desde 1980 | sin anios Nino extremo | 42 | -0.356562 | -0.016894 | -0.024974 | -0.007901 | 0.00087762 | 0.011848 | sí |
| Nivel del mar (mareografo Callao) | m | 1990-2024 | desde 1990 | todos los anios | 34 | -0.247772 | -0.014722 | -0.027628 | -0.00083333 | 0.039341 | 0.115878 | no |
| Nivel del mar (mareografo Callao) | m | 1990-2024 | desde 1990 | sin anios Nino extremo | 32 | -0.229839 | -0.013543 | -0.027149 | 0.00091667 | 0.066579 | 0.171204 | no |
| Hielo marino antartico (extension, NSIDC) | M km2 | 1979-2026 | completo | todos los anios | 48 | -0.039007 | -0.027583 | -0.147619 | 0.102899 | 0.695743 | 0.825595 | no |
| Hielo marino antartico (extension, NSIDC) | M km2 | 1979-2026 | completo | sin anios Nino extremo | 45 | 0.026263 | 0.019624 | -0.107407 | 0.140741 | 0.799233 | 0.896764 | no |
| Hielo marino antartico (extension, NSIDC) | M km2 | 1998-2026 | desde 1998 | todos los anios | 29 | -0.334975 | -0.426136 | -0.612698 | -0.074479 | 0.010425 | 0.045646 | sí |
| Hielo marino antartico (extension, NSIDC) | M km2 | 1999-2026 | desde 1998 | sin anios Nino extremo | 26 | -0.273846 | -0.392361 | -0.568627 | 0.015278 | 0.051741 | 0.142102 | no |
| Hielo marino antartico (extension, NSIDC) | M km2 | 2003-2026 | desde 2003 | todos los anios | 24 | -0.434783 | -0.635625 | -0.981667 | -0.3831 | 0.002499 | 0.017602 | sí |
| Hielo marino antartico (extension, NSIDC) | M km2 | 2003-2026 | desde 2003 | sin anios Nino extremo | 22 | -0.367965 | -0.535256 | -0.788297 | -0.074479 | 0.016542 | 0.059552 | no |
| Hielo marino antartico (extension, NSIDC) | M km2 | 2010-2026 | desde 2010 | todos los anios | 17 | -0.544118 | -1.158333 | -1.711905 | -0.491667 | 0.00178 | 0.017602 | sí |
| Hielo marino antartico (extension, NSIDC) | M km2 | 2010-2026 | desde 2010 | sin anios Nino extremo | 15 | -0.504762 | -0.859722 | -1.576667 | -0.380952 | 0.00827 | 0.039404 | sí |
| Hielo marino antartico (extension, NSIDC) | M km2 | 1980-2026 | desde 1980 | todos los anios | 47 | -0.024977 | -0.024074 | -0.146491 | 0.118452 | 0.804442 | 0.896764 | no |
| Hielo marino antartico (extension, NSIDC) | M km2 | 1980-2026 | desde 1980 | sin anios Nino extremo | 44 | 0.044397 | 0.028233 | -0.100833 | 0.159167 | 0.670983 | 0.81447 | no |
| Hielo marino antartico (extension, NSIDC) | M km2 | 1990-2026 | desde 1990 | todos los anios | 37 | -0.183183 | -0.162868 | -0.331667 | 0.053125 | 0.110573 | 0.252293 | no |
| Hielo marino antartico (extension, NSIDC) | M km2 | 1990-2026 | desde 1990 | sin anios Nino extremo | 34 | -0.108734 | -0.084615 | -0.278125 | 0.136765 | 0.365841 | 0.623855 | no |
| TSM ERSST Norte-centro (Nino 1+2) | C | 1854-2026 | completo | todos los anios | 173 | 0.13725 | 0.030616 | 0.007418 | 0.056268 | 0.007346 | 0.037191 | sí |
| TSM ERSST Norte-centro (Nino 1+2) | C | 1854-2026 | completo | sin anios Nino extremo | 170 | 0.113679 | 0.023793 | 0.002624 | 0.049429 | 0.027763 | 0.094562 | no |
| TSM ERSST Norte-centro (Nino 1+2) | C | 1998-2026 | desde 1998 | todos los anios | 29 | 0.108374 | 0.172917 | -0.178924 | 0.594463 | 0.423307 | 0.636944 | no |
| TSM ERSST Norte-centro (Nino 1+2) | C | 1999-2026 | desde 1998 | sin anios Nino extremo | 26 | 0.113846 | 0.169987 | -0.165616 | 0.520985 | 0.431303 | 0.636944 | no |
| TSM ERSST Norte-centro (Nino 1+2) | C | 2003-2026 | desde 2003 | todos los anios | 24 | 0.130435 | 0.231853 | -0.19267 | 0.860324 | 0.389341 | 0.636944 | no |
| TSM ERSST Norte-centro (Nino 1+2) | C | 2003-2026 | desde 2003 | sin anios Nino extremo | 22 | 0.056277 | 0.120187 | -0.251161 | 0.612376 | 0.738094 | 0.859611 | no |
| TSM ERSST Norte-centro (Nino 1+2) | C | 2010-2026 | desde 2010 | todos los anios | 17 | 0.088235 | 0.25748 | -0.68807 | 1.554988 | 0.655308 | 0.81447 | no |
| TSM ERSST Norte-centro (Nino 1+2) | C | 2010-2026 | desde 2010 | sin anios Nino extremo | 15 | 0.028571 | 0.134389 | -0.820361 | 1.389117 | 0.92257 | 0.958054 | no |
| TSM ERSST Norte-centro (Nino 1+2) | C | 1979-2026 | desde 1979 | todos los anios | 48 | 0.056738 | 0.043769 | -0.123352 | 0.203231 | 0.569468 | 0.744713 | no |
| TSM ERSST Norte-centro (Nino 1+2) | C | 1979-2026 | desde 1979 | sin anios Nino extremo | 45 | 0.014141 | 0.006351 | -0.145899 | 0.163028 | 0.891068 | 0.94696 | no |
| TSM ERSST Norte-centro (Nino 1+2) | C | 1950-2026 | desde 1950 | todos los anios | 77 | 0.237867 | 0.123001 | 0.050535 | 0.199024 | 0.002204 | 0.017602 | sí |
| TSM ERSST Norte-centro (Nino 1+2) | C | 1950-2026 | desde 1950 | sin anios Nino extremo | 74 | 0.208441 | 0.100532 | 0.026731 | 0.174816 | 0.008605 | 0.039828 | sí |
| TSM ERSST Norte-centro (Nino 1+2) | C | 1980-2026 | desde 1980 | todos los anios | 47 | 0.06568 | 0.055981 | -0.11555 | 0.217345 | 0.514981 | 0.699641 | no |
| TSM ERSST Norte-centro (Nino 1+2) | C | 1980-2026 | desde 1980 | sin anios Nino extremo | 44 | 0.02537 | 0.01192 | -0.145565 | 0.174816 | 0.808205 | 0.896764 | no |
| TSM ERSST Norte-centro (Nino 1+2) | C | 1990-2026 | desde 1990 | todos los anios | 37 | 0.027027 | 0.031863 | -0.194032 | 0.291422 | 0.813883 | 0.896764 | no |
| TSM ERSST Norte-centro (Nino 1+2) | C | 1990-2026 | desde 1990 | sin anios Nino extremo | 34 | -0.012478 | -0.005053 | -0.201371 | 0.221199 | 0.917351 | 0.958054 | no |
| TSM ERSST Norte-centro (Nino 1+2) | C | 1900-2026 | desde 1900 | todos los anios | 127 | 0.247594 | 0.076472 | 0.042164 | 0.111198 | 3.6527e-05 | 0.00084533 | sí |
| TSM ERSST Norte-centro (Nino 1+2) | C | 1900-2026 | desde 1900 | sin anios Nino extremo | 124 | 0.222922 | 0.066573 | 0.030912 | 0.101369 | 0.00024099 | 0.00488 | sí |
| TSM ERSST Costa sur | C | 1854-2026 | completo | todos los anios | 173 | 0.107541 | 0.024457 | 0.001372 | 0.04704 | 0.035688 | 0.107064 | no |
| TSM ERSST Costa sur | C | 1854-2026 | completo | sin anios Nino extremo | 170 | 0.082631 | 0.018401 | -0.004624 | 0.040911 | 0.109689 | 0.252293 | no |
| TSM ERSST Costa sur | C | 1998-2026 | desde 1998 | todos los anios | 29 | 0.1133 | 0.125539 | -0.215037 | 0.481967 | 0.401974 | 0.636944 | no |
| TSM ERSST Costa sur | C | 1999-2026 | desde 1998 | sin anios Nino extremo | 26 | 0.113846 | 0.107189 | -0.19007 | 0.400101 | 0.431303 | 0.636944 | no |
| TSM ERSST Costa sur | C | 2003-2026 | desde 2003 | todos los anios | 24 | 0.123188 | 0.182107 | -0.279128 | 0.717696 | 0.417155 | 0.636944 | no |
| TSM ERSST Costa sur | C | 2003-2026 | desde 2003 | sin anios Nino extremo | 22 | 0.038961 | 0.071459 | -0.365984 | 0.482689 | 0.823643 | 0.896764 | no |
| TSM ERSST Costa sur | C | 2010-2026 | desde 2010 | todos los anios | 17 | 0.176471 | 0.450812 | -0.5199 | 1.396386 | 0.348846 | 0.601203 | no |
| TSM ERSST Costa sur | C | 2010-2026 | desde 2010 | sin anios Nino extremo | 15 | 0.12381 | 0.281005 | -0.568346 | 1.274817 | 0.558966 | 0.742234 | no |
| TSM ERSST Costa sur | C | 1979-2026 | desde 1979 | todos los anios | 48 | -0.035461 | -0.032627 | -0.157056 | 0.096893 | 0.722199 | 0.847799 | no |
| TSM ERSST Costa sur | C | 1979-2026 | desde 1979 | sin anios Nino extremo | 45 | -0.090909 | -0.064721 | -0.182249 | 0.056427 | 0.378638 | 0.636944 | no |
| TSM ERSST Costa sur | C | 1950-2026 | desde 1950 | todos los anios | 77 | 0.253589 | 0.128354 | 0.051578 | 0.192525 | 0.0011 | 0.013711 | sí |
| TSM ERSST Costa sur | C | 1950-2026 | desde 1950 | sin anios Nino extremo | 74 | 0.223991 | 0.107697 | 0.03316 | 0.171386 | 0.004752 | 0.027494 | sí |
| TSM ERSST Costa sur | C | 1980-2026 | desde 1980 | todos los anios | 47 | -0.032377 | -0.027208 | -0.161761 | 0.107189 | 0.748236 | 0.859676 | no |
| TSM ERSST Costa sur | C | 1980-2026 | desde 1980 | sin anios Nino extremo | 44 | -0.086681 | -0.062835 | -0.186797 | 0.074454 | 0.406895 | 0.636944 | no |
| TSM ERSST Costa sur | C | 1990-2026 | desde 1990 | todos los anios | 37 | 0.018018 | 0.0226 | -0.211036 | 0.207625 | 0.875287 | 0.93905 | no |
| TSM ERSST Costa sur | C | 1990-2026 | desde 1990 | sin anios Nino extremo | 34 | -0.023173 | -0.025237 | -0.229954 | 0.146181 | 0.84718 | 0.914954 | no |
| TSM ERSST Costa sur | C | 1900-2026 | desde 1900 | todos los anios | 127 | 0.341582 | 0.105284 | 0.070544 | 0.140488 | 1.2294e-08 | 1.9917e-06 | sí |
| TSM ERSST Costa sur | C | 1900-2026 | desde 1900 | sin anios Nino extremo | 124 | 0.320745 | 0.095417 | 0.061959 | 0.131472 | 1.2718e-07 | 6.8679e-06 | sí |
| TSM satelital paita | C | 1998-2025 | completo | todos los anios | 28 | 0.111111 | 0.137319 | -0.245098 | 0.573485 | 0.421457 | 0.636944 | no |
| TSM satelital paita | C | 1999-2025 | completo | sin anios Nino extremo | 25 | 0.14 | 0.15816 | -0.186538 | 0.572222 | 0.341939 | 0.595635 | no |
| TSM satelital paita | C | 2003-2025 | desde 2003 | todos los anios | 23 | 0.12253 | 0.183333 | -0.325 | 0.870833 | 0.432493 | 0.636944 | no |
| TSM satelital paita | C | 2003-2025 | desde 2003 | sin anios Nino extremo | 21 | 0.057143 | 0.101389 | -0.411111 | 0.627976 | 0.742874 | 0.859611 | no |
| TSM satelital paita | C | 2010-2025 | desde 2010 | todos los anios | 16 | 0 | -0.015545 | -1.133333 | 1.263889 | 1 | 1 | no |
| TSM satelital paita | C | 2010-2025 | desde 2010 | sin anios Nino extremo | 14 | -0.098901 | -0.186538 | -1.353571 | 0.877778 | 0.667174 | 0.81447 | no |
| TSM satelital chimbote | C | 1998-2025 | completo | todos los anios | 28 | 0.195767 | 0.299107 | -0.15651 | 0.72549 | 0.150441 | 0.324953 | no |
| TSM satelital chimbote | C | 1999-2025 | completo | sin anios Nino extremo | 25 | 0.226667 | 0.288976 | -0.123889 | 0.605 | 0.118343 | 0.266273 | no |
| TSM satelital chimbote | C | 2003-2025 | desde 2003 | todos los anios | 23 | 0.201581 | 0.336859 | -0.251562 | 0.994792 | 0.188838 | 0.397296 | no |
| TSM satelital chimbote | C | 2003-2025 | desde 2003 | sin anios Nino extremo | 21 | 0.133333 | 0.231538 | -0.445833 | 0.72549 | 0.419595 | 0.636944 | no |
| TSM satelital chimbote | C | 2010-2025 | desde 2010 | todos los anios | 16 | -0.016667 | -0.047135 | -1.31875 | 1.375521 | 0.964695 | 0.982897 | no |
| TSM satelital chimbote | C | 2010-2025 | desde 2010 | sin anios Nino extremo | 14 | -0.120879 | -0.467045 | -1.524583 | 0.711458 | 0.59064 | 0.759394 | no |
| TSM satelital callao | C | 1998-2025 | completo | todos los anios | 28 | 0.185185 | 0.232552 | -0.102941 | 0.585714 | 0.174403 | 0.371754 | no |
| TSM satelital callao | C | 1999-2025 | completo | sin anios Nino extremo | 25 | 0.213333 | 0.209107 | -0.09375 | 0.47662 | 0.142382 | 0.311702 | no |
| TSM satelital callao | C | 2003-2025 | desde 2003 | todos los anios | 23 | 0.185771 | 0.272619 | -0.192188 | 0.79951 | 0.227198 | 0.456111 | no |
| TSM satelital callao | C | 2003-2025 | desde 2003 | sin anios Nino extremo | 21 | 0.12381 | 0.161901 | -0.292803 | 0.588636 | 0.455044 | 0.646641 | no |
| TSM satelital callao | C | 2010-2025 | desde 2010 | todos los anios | 16 | -0.033333 | -0.162708 | -1.226042 | 1.09375 | 0.894351 | 0.94696 | no |
| TSM satelital callao | C | 2010-2025 | desde 2010 | sin anios Nino extremo | 14 | -0.120879 | -0.266667 | -1.25 | 0.544444 | 0.59064 | 0.759394 | no |
| TSM satelital pisco | C | 1998-2025 | completo | todos los anios | 28 | 0.15873 | 0.138958 | -0.145238 | 0.480357 | 0.24627 | 0.480671 | no |
| TSM satelital pisco | C | 1999-2025 | completo | sin anios Nino extremo | 25 | 0.18 | 0.124701 | -0.125 | 0.396429 | 0.21823 | 0.453247 | no |
| TSM satelital pisco | C | 2003-2025 | desde 2003 | todos los anios | 23 | 0.15415 | 0.195833 | -0.19537 | 0.720833 | 0.319379 | 0.574882 | no |
| TSM satelital pisco | C | 2003-2025 | desde 2003 | sin anios Nino extremo | 21 | 0.085714 | 0.096389 | -0.321212 | 0.471795 | 0.611933 | 0.780575 | no |
| TSM satelital pisco | C | 2010-2025 | desde 2010 | todos los anios | 16 | -0.05 | -0.160952 | -1.014583 | 0.915625 | 0.824801 | 0.896764 | no |
| TSM satelital pisco | C | 2010-2025 | desde 2010 | sin anios Nino extremo | 14 | -0.142857 | -0.321212 | -1.1 | 0.573148 | 0.518253 | 0.699641 | no |
| TSM satelital ilo | C | 1998-2025 | completo | todos los anios | 28 | -0.079365 | -0.05675 | -0.307292 | 0.152083 | 0.570027 | 0.744713 | no |
| TSM satelital ilo | C | 1999-2025 | completo | sin anios Nino extremo | 25 | -0.093333 | -0.054944 | -0.294792 | 0.117778 | 0.532192 | 0.712521 | no |
| TSM satelital ilo | C | 2003-2025 | desde 2003 | todos los anios | 23 | 0.011858 | 0.018958 | -0.315833 | 0.297115 | 0.958368 | 0.982631 | no |
| TSM satelital ilo | C | 2003-2025 | desde 2003 | sin anios Nino extremo | 21 | -0.066667 | -0.062569 | -0.379167 | 0.185746 | 0.698188 | 0.825595 | no |
| TSM satelital ilo | C | 2010-2025 | desde 2010 | todos los anios | 16 | -0.15 | -0.2375 | -0.853333 | 0.301786 | 0.450285 | 0.64594 | no |
| TSM satelital ilo | C | 2010-2025 | desde 2010 | sin anios Nino extremo | 14 | -0.230769 | -0.350379 | -0.853333 | 0.166026 | 0.27918 | 0.50817 | no |
| Oxigeno 100-200 m (Humboldt) | mmol/m3 | 1998-2025 | completo | todos los anios | 28 | 0.111111 | 1.596993 | -3.71833 | 5.628277 | 0.421457 | 0.636944 | no |
| Oxigeno 100-200 m (Humboldt) | mmol/m3 | 1999-2025 | completo | sin anios Nino extremo | 25 | 0.16 | 1.863419 | -2.193922 | 5.628277 | 0.275468 | 0.507112 | no |
| Oxigeno 100-200 m (Humboldt) | mmol/m3 | 2003-2025 | desde 2003 | todos los anios | 23 | 0.44664 | 5.362728 | 1.66711 | 12.277727 | 0.002413 | 0.017602 | sí |
| Oxigeno 100-200 m (Humboldt) | mmol/m3 | 2003-2025 | desde 2003 | sin anios Nino extremo | 21 | 0.47619 | 4.763151 | 1.555536 | 10.472001 | 0.002084 | 0.017602 | sí |
| Oxigeno 100-200 m (Humboldt) | mmol/m3 | 2010-2025 | desde 2010 | todos los anios | 16 | 0.133333 | 3.566608 | -11.922072 | 15.561846 | 0.505644 | 0.699641 | no |
| Oxigeno 100-200 m (Humboldt) | mmol/m3 | 2010-2025 | desde 2010 | sin anios Nino extremo | 14 | 0.186813 | 3.954626 | -12.304672 | 19.514156 | 0.387988 | 0.636944 | no |
| Temperatura 100-200 m (Humboldt) | C | 1998-2025 | completo | todos los anios | 28 | 0.328042 | 0.161356 | 0.039623 | 0.274972 | 0.014103 | 0.051925 | no |
| Temperatura 100-200 m (Humboldt) | C | 1999-2025 | completo | sin anios Nino extremo | 25 | 0.4 | 0.16399 | 0.044748 | 0.2725 | 0.004626 | 0.027494 | sí |
| Temperatura 100-200 m (Humboldt) | C | 2003-2025 | desde 2003 | todos los anios | 23 | 0.470356 | 0.260029 | 0.101016 | 0.395164 | 0.001322 | 0.015299 | sí |
| Temperatura 100-200 m (Humboldt) | C | 2003-2025 | desde 2003 | sin anios Nino extremo | 21 | 0.457143 | 0.232823 | 0.098498 | 0.366608 | 0.003253 | 0.021077 | sí |
| Temperatura 100-200 m (Humboldt) | C | 2010-2025 | desde 2010 | todos los anios | 16 | 0.4 | 0.371953 | 0.044748 | 0.574934 | 0.032626 | 0.103635 | no |
| Temperatura 100-200 m (Humboldt) | C | 2010-2025 | desde 2010 | sin anios Nino extremo | 14 | 0.428571 | 0.325531 | 0.009885 | 0.557554 | 0.035566 | 0.107064 | no |
| Viento rapidez Paita (hasta 2016) | m/s | 1998-2016 | completo | todos los anios | 19 | 0.076023 | 0.039243 | -0.202288 | 0.268145 | 0.678725 | 0.81447 | no |
| Viento rapidez Paita (hasta 2016) | m/s | 1999-2015 | completo | sin anios Nino extremo | 17 | 0.161765 | 0.083449 | -0.128181 | 0.319593 | 0.392728 | 0.636944 | no |
| Viento rapidez Paita (hasta 2016) | m/s | 2003-2016 | desde 2003 | todos los anios | 14 | -0.164835 | -0.175093 | -0.572606 | 0.172408 | 0.450563 | 0.64594 | no |
| Viento rapidez Paita (hasta 2016) | m/s | 2003-2015 | desde 2003 | sin anios Nino extremo | 13 | -0.025641 | -0.03738 | -0.432983 | 0.319593 | 0.952362 | 0.982631 | no |
| Viento v Paita (hasta 2016) | m/s | 1998-2016 | completo | todos los anios | 19 | 0.076023 | 0.079238 | -0.167685 | 0.283994 | 0.678725 | 0.81447 | no |
| Viento v Paita (hasta 2016) | m/s | 1999-2015 | completo | sin anios Nino extremo | 17 | 0.147059 | 0.110277 | -0.138642 | 0.308317 | 0.439687 | 0.641705 | no |
| Viento v Paita (hasta 2016) | m/s | 2003-2016 | desde 2003 | todos los anios | 14 | -0.208791 | -0.161021 | -0.53834 | 0.128781 | 0.330811 | 0.582516 | no |
| Viento v Paita (hasta 2016) | m/s | 2003-2015 | desde 2003 | sin anios Nino extremo | 13 | -0.076923 | -0.060528 | -0.403667 | 0.291264 | 0.765025 | 0.872775 | no |
| Viento rapidez Chimbote (hasta 2016) | m/s | 1998-2016 | completo | todos los anios | 19 | -0.415205 | -0.379612 | -0.635515 | -0.074756 | 0.012824 | 0.051925 | no |
| Viento rapidez Chimbote (hasta 2016) | m/s | 1999-2015 | completo | sin anios Nino extremo | 17 | -0.279412 | -0.27689 | -0.576218 | 0.091426 | 0.128789 | 0.285806 | no |
| Viento rapidez Chimbote (hasta 2016) | m/s | 2003-2016 | desde 2003 | todos los anios | 14 | -0.450549 | -0.534965 | -0.75958 | -0.068255 | 0.0264 | 0.092973 | no |
| Viento rapidez Chimbote (hasta 2016) | m/s | 2003-2015 | desde 2003 | sin anios Nino extremo | 13 | -0.384615 | -0.44737 | -0.812966 | 0.068217 | 0.076317 | 0.193176 | no |
| Viento v Chimbote (hasta 2016) | m/s | 1998-2016 | completo | todos los anios | 19 | -0.438596 | -0.33749 | -0.548097 | -0.10209 | 0.008264 | 0.039404 | sí |
| Viento v Chimbote (hasta 2016) | m/s | 1999-2015 | completo | sin anios Nino extremo | 17 | -0.294118 | -0.277752 | -0.492458 | 0.114843 | 0.108865 | 0.252293 | no |
| Viento v Chimbote (hasta 2016) | m/s | 2003-2016 | desde 2003 | todos los anios | 14 | -0.516484 | -0.499037 | -0.742905 | -0.143583 | 0.009753 | 0.043889 | sí |
| Viento v Chimbote (hasta 2016) | m/s | 2003-2015 | desde 2003 | sin anios Nino extremo | 13 | -0.435897 | -0.388806 | -0.742905 | 0.066467 | 0.042182 | 0.119885 | no |
| Viento rapidez Callao (hasta 2016) | m/s | 1998-2016 | completo | todos los anios | 19 | -0.48538 | -0.451687 | -0.712485 | -0.201097 | 0.003154 | 0.021077 | sí |
| Viento rapidez Callao (hasta 2016) | m/s | 1999-2015 | completo | sin anios Nino extremo | 17 | -0.352941 | -0.327024 | -0.574867 | 0.014793 | 0.051753 | 0.142102 | no |
| Viento rapidez Callao (hasta 2016) | m/s | 2003-2016 | desde 2003 | todos los anios | 14 | -0.494505 | -0.591331 | -0.876767 | -0.135022 | 0.013838 | 0.051925 | no |
| Viento rapidez Callao (hasta 2016) | m/s | 2003-2015 | desde 2003 | sin anios Nino extremo | 13 | -0.410256 | -0.523999 | -0.880669 | 0.092058 | 0.057257 | 0.149607 | no |
| Viento v Callao (hasta 2016) | m/s | 1998-2016 | completo | todos los anios | 19 | -0.497076 | -0.422782 | -0.664065 | -0.16525 | 0.002433 | 0.017602 | sí |
| Viento v Callao (hasta 2016) | m/s | 1999-2015 | completo | sin anios Nino extremo | 17 | -0.367647 | -0.287027 | -0.48225 | -0.007083 | 0.042171 | 0.119885 | no |
| Viento v Callao (hasta 2016) | m/s | 2003-2016 | desde 2003 | todos los anios | 14 | -0.538462 | -0.508167 | -0.841625 | -0.153635 | 0.006742 | 0.035234 | sí |
| Viento v Callao (hasta 2016) | m/s | 2003-2015 | desde 2003 | sin anios Nino extremo | 13 | -0.461538 | -0.456037 | -0.766167 | -0.007083 | 0.030482 | 0.098763 | no |
| Viento rapidez Pisco (hasta 2016) | m/s | 1998-2016 | completo | todos los anios | 19 | -0.368421 | -0.269502 | -0.569429 | -0.014838 | 0.028602 | 0.094562 | no |
| Viento rapidez Pisco (hasta 2016) | m/s | 1999-2015 | completo | sin anios Nino extremo | 17 | -0.205882 | -0.11171 | -0.357083 | 0.191302 | 0.270561 | 0.503802 | no |
| Viento rapidez Pisco (hasta 2016) | m/s | 2003-2016 | desde 2003 | todos los anios | 14 | -0.494505 | -0.436337 | -0.807306 | -0.019354 | 0.013838 | 0.051925 | no |
| Viento rapidez Pisco (hasta 2016) | m/s | 2003-2015 | desde 2003 | sin anios Nino extremo | 13 | -0.410256 | -0.318798 | -0.761089 | 0.064339 | 0.057257 | 0.149607 | no |
| Viento v Pisco (hasta 2016) | m/s | 1998-2016 | completo | todos los anios | 19 | -0.368421 | -0.228111 | -0.525287 | -0.016861 | 0.028602 | 0.094562 | no |
| Viento v Pisco (hasta 2016) | m/s | 1999-2015 | completo | sin anios Nino extremo | 17 | -0.205882 | -0.081067 | -0.336262 | 0.146958 | 0.270561 | 0.503802 | no |
| Viento v Pisco (hasta 2016) | m/s | 2003-2016 | desde 2003 | todos los anios | 14 | -0.494505 | -0.395306 | -0.723481 | -0.04075 | 0.013838 | 0.051925 | no |
| Viento v Pisco (hasta 2016) | m/s | 2003-2015 | desde 2003 | sin anios Nino extremo | 13 | -0.410256 | -0.252667 | -0.707048 | 0.050617 | 0.057257 | 0.149607 | no |
| Viento rapidez Ilo (hasta 2016) | m/s | 1998-2016 | completo | todos los anios | 19 | -0.122807 | -0.041852 | -0.271513 | 0.065584 | 0.489338 | 0.687208 | no |
| Viento rapidez Ilo (hasta 2016) | m/s | 1999-2015 | completo | sin anios Nino extremo | 17 | 0.088235 | 0.015702 | -0.166158 | 0.197843 | 0.655308 | 0.81447 | no |
| Viento rapidez Ilo (hasta 2016) | m/s | 2003-2016 | desde 2003 | todos los anios | 14 | -0.032967 | -0.025894 | -0.314197 | 0.26093 | 0.914485 | 0.958054 | no |
| Viento rapidez Ilo (hasta 2016) | m/s | 2003-2015 | desde 2003 | sin anios Nino extremo | 13 | 0.102564 | 0.03074 | -0.290848 | 0.346432 | 0.675433 | 0.81447 | no |
| Viento v Ilo (hasta 2016) | m/s | 1998-2016 | completo | todos los anios | 19 | 0.164224 | 0.087979 | -0.122097 | 0.259646 | 0.326989 | 0.582113 | no |
| Viento v Ilo (hasta 2016) | m/s | 1999-2015 | completo | sin anios Nino extremo | 17 | 0.376386 | 0.144135 | 0.007859 | 0.359697 | 0.0355 | 0.107064 | no |
| Viento v Ilo (hasta 2016) | m/s | 2003-2016 | desde 2003 | todos los anios | 14 | 0.132599 | 0.073991 | -0.173014 | 0.36124 | 0.510586 | 0.699641 | no |
| Viento v Ilo (hasta 2016) | m/s | 2003-2015 | desde 2003 | sin anios Nino extremo | 13 | 0.245166 | 0.108751 | -0.13745 | 0.431792 | 0.245507 | 0.480671 | no |

</details>

Se conservan las filas de viento para trazabilidad, aunque no se recomiendan como hallazgo. Las pruebas de esta tabla no corrigen autocorrelación anual y algunas fuentes llegan a 2026.

### F. Predicción histórica E8: todos los horizontes y zonas

Fuente: `data/tablas_pruebas_pendientes/nuevos_E8_prediccion_origen_movil.csv`. Filas: 15.

| Zona | Horizonte meses | n | RMSE clim. | RMSE persist. | RMSE modelo | Mejora clim. % | Mejora persist. % | r |
|---|---|---|---|---|---|---|---|---|
| paita | 1 | 192 | 31.2 | 32.3 | 27.3 | 12.5 | 15.7 | 0.49 |
| paita | 2 | 192 | 31.2 | 39.8 | 29.8 | 4.3 | 25 | 0.292 |
| paita | 3 | 192 | 31.2 | 43.4 | 29.9 | 4.2 | 31.2 | 0.3 |
| chimbote | 1 | 192 | 34.2 | 32.3 | 29.3 | 14.4 | 9.4 | 0.542 |
| chimbote | 2 | 192 | 34.2 | 39.4 | 31.8 | 7 | 19.4 | 0.416 |
| chimbote | 3 | 192 | 34.2 | 43.1 | 33 | 3.4 | 23.4 | 0.377 |
| callao | 1 | 192 | 39.1 | 45.8 | 35.9 | 8.3 | 21.6 | 0.397 |
| callao | 2 | 192 | 39.1 | 52.2 | 37.3 | 4.6 | 28.4 | 0.306 |
| callao | 3 | 192 | 39.1 | 53.1 | 37.9 | 3.1 | 28.6 | 0.264 |
| pisco | 1 | 192 | 27.2 | 30.7 | 25.8 | 5.2 | 16 | 0.348 |
| pisco | 2 | 192 | 27.2 | 33.1 | 27.1 | 0.6 | 18.2 | 0.207 |
| pisco | 3 | 192 | 27.2 | 36.9 | 28.4 | -4.1 | 23.2 | -0.049 |
| ilo | 1 | 192 | 44.3 | 40.8 | 36.6 | 17.4 | 10.3 | 0.565 |
| ilo | 2 | 192 | 44.3 | 47.5 | 40.8 | 7.9 | 14 | 0.395 |
| ilo | 3 | 192 | 44.3 | 50.2 | 42.4 | 4.4 | 15.6 | 0.305 |

### G. Sensibilidad de A/B con biomasa observada por crucero

Fuente: `analysis_r/data/sensitivity/cruise_sensitivity_metrics.csv`. Filas: 10.

| Variante | Modelo | n | R² | R² ajustado | RMSE LOOCV log10 | Coef. Niño | p Niño |
|---|---|---|---|---|---|---|---|
| 9_cruceros_original | A_local | 9 | 0.47192 | 0.295893 | 0.34934 | -0.17447 | 0.101597 |
| 9_cruceros_original | B_productivity | 9 | 0.650044 | 0.44007 | 0.368708 | -0.16354 | 0.098963 |
| 8_cruceros_sin_1998 | A_local | 8 | 0.680657 | 0.55292 | 0.056446 | -0.023267 | 0.190469 |
| 8_cruceros_sin_1998 | B_productivity | 8 | 0.724082 | 0.517144 | 0.060797 | -0.026785 | 0.181419 |
| 12_cruceros_ampliado | A_local | 12 | 0.4603 | 0.340367 | 0.301998 | -0.147668 | 0.051011 |
| 12_cruceros_ampliado | B_productivity | 12 | 0.553171 | 0.38561 | 0.321541 | -0.12424 | 0.096108 |
| 11_cruceros_ampliado_sin_1998 | A_local | 11 | 0.563882 | 0.454853 | 0.064693 | -0.011068 | 0.536939 |
| 11_cruceros_ampliado_sin_1998 | B_productivity | 11 | 0.566101 | 0.380144 | 0.066798 | -0.011076 | 0.564016 |
| 11_cruceros_ampliado_sin_2102-07 | A_local | 11 | 0.453825 | 0.317282 | 0.313309 | -0.152505 | 0.066742 |
| 11_cruceros_ampliado_sin_2102-07 | B_productivity | 11 | 0.547377 | 0.353396 | 0.335675 | -0.1286 | 0.120435 |

### H. Comparación A/B/C original con nueve cruceros

Fuente: `analysis_r/data/exploratory_nointerp/cruise_model_metrics.csv`. Filas: 3.

| model | n | r2 | adj_r2 | AIC | loocv_rmse |
|---|---|---|---|---|---|
| A_local | 9 | 0.47192 | 0.295893 | 5.303061 | 0.34934 |
| B_productivity | 9 | 0.650044 | 0.44007 | 3.600105 | 0.368708 |
| C_connectivity | 9 | 0.688651 | 0.377302 | 4.548061 | 0.40128 |

### I. RAM: comparación corregida de estructuras comunes

Fuente: `analysis_r/data/exploratory_nointerp/ram_block_lrt_corrected.csv`. Filas: 4.

| Estructura | Modelo | Parámetros | AIC | LogLik | LR | p |
|---|---|---|---|---|---|---|
| GLS_ML_same_IID_covariance | 1 | 8 | -18.599552 | 17.299776 | — | — |
| GLS_ML_same_IID_covariance | 2 | 10 | -17.084255 | 18.542128 | 2.484703 | 0.288705 |
| GLS_ML_same_AR1_covariance | 1 | 9 | -21.181522 | 19.590761 | — | — |
| GLS_ML_same_AR1_covariance | 2 | 11 | -30.947922 | 26.473961 | 13.7664 | 0.001025 |

### J. Documentos y scripts de procedencia

- [SEGUIMIENTO_PRUEBAS.md](SEGUIMIENTO_PRUEBAS.md): fuente histórica o detalle de una ronda; ante discrepancias numéricas prevalecen los CSV consolidados aquí.
- [HALLAZGOS_Y_RESULTADOS.md](HALLAZGOS_Y_RESULTADOS.md): fuente histórica o detalle de una ronda; ante discrepancias numéricas prevalecen los CSV consolidados aquí.
- [CONTEXTO_TRABAJO.md](CONTEXTO_TRABAJO.md): fuente histórica o detalle de una ronda; ante discrepancias numéricas prevalecen los CSV consolidados aquí.
- [RESULTADOS_PRUEBAS_PENDIENTES.md](RESULTADOS_PRUEBAS_PENDIENTES.md): fuente histórica o detalle de una ronda; ante discrepancias numéricas prevalecen los CSV consolidados aquí.
- [RESULTADOS_RONDA_SEIS_VARIABLES.md](RESULTADOS_RONDA_SEIS_VARIABLES.md): fuente histórica o detalle de una ronda; ante discrepancias numéricas prevalecen los CSV consolidados aquí.
- [INVESTIGACION_RELACIONES_ECOLOGICAS.md](INVESTIGACION_RELACIONES_ECOLOGICAS.md): fuente histórica o detalle de una ronda; ante discrepancias numéricas prevalecen los CSV consolidados aquí.
- [PLAN_ANALISIS_BIOMASA_FITOPLANCTON.md](PLAN_ANALISIS_BIOMASA_FITOPLANCTON.md): fuente histórica o detalle de una ronda; ante discrepancias numéricas prevalecen los CSV consolidados aquí.

Los comandos y scripts de las pruebas históricas A/B/E están en `docs/pruebas_pendientes/`; pueden requerir las rutas y fuentes externas originales. Los scripts 18/19 y las pruebas automatizadas están en `scripts/` y `tests/`. No se borró ni se sustituyó ningún archivo histórico.


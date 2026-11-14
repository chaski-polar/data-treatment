# Relaciones aprovechables para continuar el proyecto

Fecha: 14 de noviembre de 2026. Investigación bibliográfica y nueva exploración con datos locales.

## Conclusión de trabajo

Sí existen asociaciones significativas y estables entre variables disponibles. La ruta más defendible es comparar los controles locales de la biomasa y del pigmento en distintas regiones, junto con la respuesta peruana a El Niño. Estas pruebas no respaldan un transporte directo de fitoplancton ni una cadena causal Antártida–Perú.

Se ejecutaron 33 contrastes definidos en el script antes de calcular resultados. Dieciséis pasan FDR en el periodo completo; nueve conservan signo y significancia en las sensibilidades establecidas. Uno de esos nueve empeora fuertemente la evaluación temporal, de modo que no se recomienda como predictor.

## Hallazgo de la auditoría

El script anterior `enfoque_mecanismo.py` consultaba la profundidad de la capa de mezcla (`mlotst`) en `surface_0_5m` y la descartaba como vacía. En el panel esta variable está en `surface_2d`, con **336 meses válidos para cada una de las seis regiones**. No faltaba descargarla: faltaba seleccionar la banda correcta.

Esto explica por qué una variable relevante no apareció en la tanda anterior. La nueva investigación utiliza esos datos existentes y no reconstruye ni modifica el panel original.

## Por qué estudiar mezcla, luz y carbono

Un experimento de mesocosmos frente a Callao encontró que la disponibilidad de luz y nitrato influye sobre biomasa y productividad; en condiciones de poca luz aumentó la cantidad de pigmento respecto al carbono. Esto justifica distinguir clorofila, carbono y producción primaria, y explorar su relación con la mezcla. No permite interpretar automáticamente una correlación regional como prueba de ese mecanismo. [Thielecke et al., 2025](https://epub.ub.uni-muenchen.de/129214/).

Un estudio del sistema peruano con modelo físico-biogeoquímico relaciona la reducción de productividad durante El Niño con cambios en el suministro de nutrientes y en la mezcla, además de señalar que viento favorable al afloramiento y flujo efectivo de nutrientes pueden desacoplarse. Por eso un índice simple de viento no tiene por qué explicar bien la clorofila. [Espinoza-Morriberón et al., 2017](https://doi.org/10.1002/2016JC012439).

Observaciones en el Océano Austral muestran que pigmento, partículas y carbono pueden presentar ciclos diferentes y que interpretar su cociente exige considerar mezcla, luz y otras limitaciones. El sitio estudiado no es Bellingshausen ni la Península: es respaldo de la hipótesis conceptual, no validación directa de nuestras cajas. [Estudio de SOTS, 2019](https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2019.00595/full).

## Diseño y criterios

- Periodo máximo 1998–2025; NASA MODIS comienza en julio de 2002 y termina en noviembre de 2025 (281 meses disponibles).
- Variables de entrada: `phyc`, `chl`, `no3`, `mlotst`, temperatura superficial y a 100–200 m de CMEMS; clorofila OC-CCI por zona; clorofila MODIS-Aqua de Giovanni; Niño 1+2.
- Lista acotada de 33 contrastes: ENSO–pigmento/carbono; mezcla–carbono/pigmento; nitrato un mes antes–carbono; contraste térmico vertical–carbono; mezcla–log(clorofila/carbono).
- Se eliminan los promedios mensuales y se ajusta tendencia y efectos fijos de mes. Para predictores distintos de Niño 1+2 también se controla ese índice, contemporáneo y en el mes fuente cuando hay rezago.
- Inferencia bilateral con HAC/Newey–West, ancho de 12 meses, conservando distancias calendario. FDR Benjamini–Hochberg sobre **las 33 pruebas completas**, incluidos controles de relaciones ya conocidas.
- Sensibilidades: hasta 2011; desde 2012; sin 1998; HAC de 6 y 24 meses. Cada escenario corrige su familia completa de 33 pruebas.
- Se considera consistente en estas comprobaciones si mantiene signo y q < 0,05 en todos esos escenarios; esto no constituye una certificación de robustez frente a cualquier especificación.
- Los periodos ya fueron inspeccionados en estudios anteriores. Es exploración retrospectiva; FDR de esta tanda no corrige todas las búsquedas históricas del proyecto ni convierte el resultado en confirmatorio.

## Resultados principales

`r` es correlación parcial después de los controles; `q` es el p-valor ajustado por FDR. Las cifras corresponden al periodo completo de cada par.

| ID | Relación | n | r parcial | q FDR | Consistente en todas las sensibilidades |
|---|---|---:|---:|---:|---|
| H08 | Niño 1+2 → carbono fitoplanctónico de Humboldt | 336 | −0,537 | 1,34 × 10⁻⁷ | Sí |
| H02 | Niño 1+2 → clorofila de Chimbote, OC-CCI | 334 | −0,406 | 3,37 × 10⁻⁸ | Sí |
| H03 | Niño 1+2 → clorofila de Callao, OC-CCI | 335 | −0,388 | 2,85 × 10⁻⁸ | Sí |
| H10 | Capa de mezcla → carbono en Bellingshausen | 336 | −0,226 | 7,29 × 10⁻⁴ | Sí |
| H12 | Capa de mezcla → carbono en Pacífico Sur intermedio | 336 | −0,395 | 6,97 × 10⁻⁵ | Sí |
| H13 | Capa de mezcla → carbono en Pacífico Sur subtropical | 336 | −0,451 | 1,74 × 10⁻¹⁴ | Sí |
| H28 | Nitrato un mes antes → carbono en Pacífico Sur subtropical | 335 | +0,316 | 3,10 × 10⁻⁴ | Sí |
| H33 | Capa de mezcla → pigmento por carbono en Humboldt | 336 | +0,477 | 6,27 × 10⁻¹⁹ | Sí |
| H20 | Capa de mezcla peruana → clorofila de Chimbote, MODIS-Aqua | 281 | −0,176 | 9,62 × 10⁻⁴ | No |
| H06 | Niño 1+2 → clorofila de Chimbote, MODIS-Aqua | 281 | −0,144 | 0,0376 | No |

### La línea principal: El Niño y carbono peruano

H08 utiliza `phyc` de CMEMS, no carbono obtenido multiplicando clorofila por una constante. La asociación negativa se mantiene en 1998–2011 (r = −0,560), en 2012–2025 (−0,598) y sin 1998 (−0,574). Es una base más clara para estudiar biomasa fitoplanctónica peruana que la búsqueda de conexión directa con la Antártida.

Los resultados de clorofila de Chimbote y Callao con OC-CCI se mantienen también en ambas mitades. Eso aporta evidencia de pigmento satelital, aunque no convierte el carbono modelado en una observación.

### Mezcla y biomasa: comparación entre regiones

En Bellingshausen y en dos sectores del Pacífico Sur, meses con mezcla más profunda se asocian con menos carbono en la capa superficial, incluso después de controlar Niño 1+2, estacionalidad y tendencia. Esto es compatible con restricciones de luz y/o dilución superficial, pero no distingue ambos procesos ni demuestra menor biomasa integrada en toda la columna.

La misma asociación no aparece de forma estable en el carbono de la Península Antártica ni del dominio peruano. Este contraste regional es científicamente útil y debe mostrarse junto con los resultados positivos, sin generalizar «más mezcla siempre significa menos fitoplancton».

### El pigmento no es igual a la biomasa

En Perú, H33 muestra más clorofila por unidad de carbono cuando la mezcla se profundiza. La asociación es fuerte en el modelo y concuerda con una hipótesis de fotoaclimatación. Sin embargo, el cociente usa dos variables de CMEMS, cuyas ecuaciones pueden incorporar ese comportamiento: no es un descubrimiento fisiológico independiente.

La pregunta presentable es: **¿puede cambiar el color del mar sin que cambie proporcionalmente la biomasa?** El resultado invita a comparar indicadores, no a tratar el cociente como productividad primaria ni evidencia de transporte.

## Qué aportan los datos NASA

Las relaciones de Niño 1+2 y de mezcla con clorofila MODIS-Aqua de Chimbote pasan FDR en la serie completa, pero no se confirman significativamente en ambas mitades. En H20 el signo se mantiene, pero q es 0,330 antes de 2012 y 0,0645 después. En H06 tampoco se confirma por mitades. Esto limita la fuerza del respaldo NASA.

En Paita, ninguna de estas dos relaciones simultáneas es significativa en el periodo completo. La respuesta tardía discutida en trabajos previos queda fuera de esta tanda: no se buscaron nuevos rezagos para obtener significancia.

OC-CCI incluye observaciones de MODIS entre otros sensores; comparar productos evalúa sensibilidad a algoritmos, cobertura y agregación, no independencia total de observaciones. Las cajas CMEMS y las cajas costeras tampoco son idénticas.

## Significancia frente a utilidad temporal

La evaluación anual con origen móvil usa 2012–2025, entrena solo con años previos y calcula climatologías con el entrenamiento. Compara el modelo con predictor frente a los mismos controles sin ese predictor.

| Relación | Mejora de RMSE condicional |
|---|---:|
| El Niño → carbono peruano | +15,0 % |
| El Niño → clorofila OC-CCI de Chimbote | +13,6 % |
| El Niño → clorofila OC-CCI de Callao | +12,8 % |
| Mezcla → carbono, Pacífico Sur intermedio | +8,0 % |
| Mezcla → carbono, Pacífico Sur subtropical | +7,4 % |
| Mezcla → carbono, Bellingshausen | +2,1 % |
| Mezcla → pigmento/carbono peruano | +13,2 % |

Son evaluaciones **condicionales con el predictor conocido en el mes objetivo**, no pronósticos operativos ni mejoras demostradas sobre persistencia. No hay intervalos de incertidumbre para estas diferencias de RMSE; no debe afirmarse que sus mejoras son estadísticamente significativas.

Un contraejemplo importante: nitrato de la transición de Humboldt un mes antes frente a carbono (H29) es significativo (r = +0,515; q = 2,10 × 10⁻⁶), pero empeora el RMSE alrededor de 267 %. No se recomienda como predictor. Esto muestra por qué el p-valor no es suficiente para elegir la dirección del proyecto.

## Prioridades para continuar

1. **Mantener El Niño → ambiente local → carbono/pigmento peruano como línea principal.** Presentar los indicadores por separado y comprobar el modelo con nuevas observaciones y con evaluación verdaderamente prospectiva cuando existan.
2. **Desarrollar una comparación de mecanismos regionales**: Bellingshausen y Pacífico Sur responden a mezcla de manera distinta de Perú y Península. Esto mantiene una componente antártica con una pregunta que los datos sí permiten abordar, sin afirmar conexión directa.
3. **Añadir un apartado de pigmento frente a biomasa.** Mostrar el resultado modelado de clorofila/carbono y buscar posteriormente una validación con carbono satelital o in situ.
4. **Priorizar validación observacional de la mezcla**: extraer MLD y otros campos para las mismas cajas de MODIS/OC-CCI y ampliar las series NASA de otras zonas. Las asociaciones actuales entre campos CMEMS comparten estructura y forzamiento; esa validación falta.
5. **No ampliar indefinidamente la búsqueda de rezagos Antártida–Perú.** El contraste específico de carbono anterior dio q mínimo 0,1865. Estas asociaciones locales no lo sustituyen ni lo vuelven significativo.
6. **No extrapolar a anchoveta** sin una nueva prueba con biomasa observada y campañas armonizadas. Las relaciones actuales terminan en fitoplancton.

Un enfoque de producto posible es: **«Qué controla la biomasa y el color del océano: comparación del océano Austral, Pacífico Sur y Humboldt bajo El Niño»**. Debe distinguir en la interfaz datos satelitales y resultados modelados, explicar cuándo una asociación es estable y mostrar también dónde no aparece.

## Reproducción y artefactos

Desde `data_treatment`:

```bash
uv run python scripts/19_investigate_ecosystem_relationships.py
```

Salidas en `data/processed/analysis/ecosystem_relationships/`:

- `hypotheses_and_config.json`: lista completa, controles y hashes de fuentes.
- `coverage.csv` e `input_series.csv`: disponibilidad y series utilizadas.
- `all_results.csv`: 198 filas, 33 hipótesis por seis escenarios.
- `summary.csv`: resultados, sensibilidad y evaluación temporal por relación.
- `report.md`: tabla completa y limitaciones.
- `candidate_effects.png` y `.svg`: efectos e intervalos en los tres periodos para las asociaciones que pasan las comprobaciones.

Verificación automatizada:

```bash
uv run python -m unittest discover -s tests -v
```

Pasaron siete pruebas, incluidas extracción correcta de MLD, cobertura completa de Giovanni, control de una asociación espuria por ENSO, evaluación con entrenamiento previo, HAC calendario y sentido del rezago.

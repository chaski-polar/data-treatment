# 1c. Temporadas de pesca y cuotas (LMTCP) de anchoveta, zona norte-centro, 2016–2026

## Para qué sirve
Si la variable de respuesta (y_t) son **desembarques** (`1a`, `1b`), estos cambian por decisiones de gestión y no solo por el ambiente. Con esta tabla se puede marcar en el modelo cuándo hubo pesca abierta, cuándo hubo veda y cuál fue la cuota.

## Archivo
`temporadas_norte_centro_2016_2026.csv`: una fila por temporada (I = primera, abril–julio; II = segunda, noviembre–enero).

| Columna | Qué es |
|---|---|
| `temporada` | Año y temporada (I o II) |
| `inicio`, `fin` | Fechas (AAAA-MM-DD). Vacío = no confirmado |
| `cuota_lmtcp_t` | Límite Máximo Total de Captura Permisible, en toneladas. 0 = no hubo temporada |
| `norma_inicio`, `norma_cuota`, `norma_cierre` | Resolución que la autoriza, fija la cuota o la cierra |
| `como_se_obtuvo_inicio`, `como_se_obtuvo_cuota` | Si el dato se **leyó en la norma**, se **calculó** a partir de ella, salió de **prensa** o se copió **del Doc del equipo** sin volver a revisarlo |
| `fuente_principal`, `fuente_secundaria` | Enlaces |

## Cómo se obtuvo (01/11/2026)
1. **Normas oficiales:** se bajaron con `curl` de FAOLEX (base legal de la FAO, sin cuenta) las resoluciones de PRODUCE que ya estaban en el Doc del equipo, más otras que aparecieron en búsquedas web. Están en `normas_pdf/`. El texto se leyó con Python (PyMuPDF), buscando "Autorizar el inicio", "Límite Máximo" y "toneladas".
2. **Cuotas de las primeras temporadas 2016–2026:** nota de Infobae del 01/04/2026, que trae una lista año por año. Se leyó desde Chrome. Para 2017-I y 2019-I, esa lista coincide con la norma oficial.
3. **Resto:** búsquedas web (Andina, Oceana, Congreso, RPP, Baird Maritime, El Tiempo). Cada fila dice de dónde salió.
4. **Fechas "calculadas":** varias normas dicen "a partir del cuarto día hábil desde la publicación". Se contó desde la fecha de El Peruano que trae el PDF. En 2016-II el resultado (15/11) coincide con la prensa.

## Normas descargadas (`normas_pdf/`)
| Archivo | Norma | Qué dice |
|---|---|---|
| `per161191.pdf` | RM 440-2016-PRODUCE | Inicio 2016-II y cuota de 2,0 millones t |
| `per172066.pdf` | RM 173-2017-PRODUCE | Inicio 2017-I y cuota de 2,8 millones t |
| `per173253.pdf` | RM 306-2017-PRODUCE | **Zona sur**, 2017-II, 515 000 t (no entra en la tabla norte-centro) |
| `per173382.pdf` | RM 357-2017-PRODUCE | Fin de 2017-I (72 h después del 28/07/2017) |
| `per185351.pdf` | RM 504-2018-PRODUCE | Inicio 2018-II con tope provisional de 400 000 t |
| `per185370.pdf` | RM 509-2018-PRODUCE | Cuota 2018-II de 2 100 000 t |
| `per188268.pdf` | RM 162-2019-PRODUCE | Inicio 2019-I (04/05) y cuota de 2 100 000 t |
| `per193526.pdf` | RM 483-2019-PRODUCE | Inicio 2019-II (16/11) y cuota de 2 786 000 t |
| `per198877.pdf` | RM 383-2020-PRODUCE | Inicio 2020-II (12/11); **no trae la cuota** |
| `per201336.pdf` | RM 263-2020-PRODUCE | Fin de 2020-I (El Peruano, 06/08/2020) |

## Qué tan confiable es cada dato
- **Leído en la norma (alta):** 2016-II, 2017-I, 2018-II, 2019-I y 2019-II.
- **Del Doc del equipo, sin volver a revisar (media):** 2021-II, 2022-II, 2024-II y 2025-I. Las URL de las normas están en el CSV.
- **Prensa (media-baja):** 2017-II, 2018-I, 2020-I, 2020-II, 2021-I, 2022-I, 2024-I, 2025-II, 2026-I y 2026-II.
- **2023-II (1 682 000 t):** confirmado por prensa (Infobae, 02/11/2025: "1,68 millones"). Falta la norma oficial.

## Lo que falta
- Fechas de inicio y fin de 2018-I, 2020-I (inicio), 2021-I, 2022-I y 2023-II (2025-II empezó el 07/11/2025 según Infobae). También casi todas las fechas de cierre.
- Las normas oficiales de las cuotas que hoy salen de prensa.
- 1998–2015: no se buscó.
- **Zona sur:** no se armó (solo se bajó una norma de 2017).
- **Días de veda por mes:** no hay una lista oficial. Se pueden aproximar con estas fechas o con los meses de desembarque casi nulo de `1a`. Esa decisión le toca al equipo.
- **Esfuerzo pesquero:** no se buscó en esta ronda. Global Fishing Watch pide registro.

---

## Agregado (01/11/2026): temporadas 1997–2015 con días de pesca (Bouchon et al. 2018)
Archivo: `temporadas_norte_centro_1997_2015_bouchon.csv`

- **Fuente:** Bouchon M, Ñiquen M, Franco M, Ttito H. 2018. *Estadísticas de la pesquería pelágica en la costa peruana (1959-2015).* Inf Inst Mar Perú 45(4).
  - **Tabla 152:** "Cuotas, capturas y días operativos de pesca de anchoveta. Región Norte-Centro. Primer semestre 1965-2015" (p. 161 del PDF).
  - **Tabla 153:** lo mismo para el segundo semestre (p. 162).
  - El PDF ya está guardado en `..\1b_desembarques_1998_2002_bouchon\`.
- **Cómo se obtuvo:** las tablas vienen giradas (cada año es una columna). Se leyeron las palabras con PyMuPDF, agrupándolas por columna, y las filas de 1997–2015 se pasaron a mano al CSV.
- **Revisión:** en todas las filas con cuota y captura, `captura / cuota` da el `porcentaje_cuota` que trae el PDF (diferencia < 0,6 puntos).
- **Columnas:**
  - `periodo_original`: tal como está escrito en el PDF.
  - `dias_de_pesca`: días operativos de pesca.
  - `cuota_miles_t` y `captura_miles_t`: en **miles de toneladas**.
  - `porcentaje_cuota`.
  - `dispositivo_legal`: la norma.
  - `nota`.
  - "S/C" = sin cuota (régimen provisional). "Manejo biológico" = la tabla no trae datos.
- **Por qué sirve para el punto d (esfuerzo):** `dias_de_pesca` es una medida de **esfuerzo**. Antes de 2009 la temporada era una "carrera olímpica": la cuota se capturaba en pocos días (por ejemplo, 19 días en 2008-II). Desde **2009-I** rigen las cuotas por embarcación (LMCE) y los días de pesca suben (70–118). Ese cambio de régimen hay que tenerlo en cuenta si el y_t son desembarques.
- **Ojo:** en 2001-II la norma está impresa "349-200-1PE" (se anotó como 349-2001-PE). En 2000-I el número de la norma no se lee bien (solo aparece "556").
- **Con esto, cuotas y temporadas quedan cubiertas de 1997 a 2026:** 1997–2015 de Bouchon (este archivo) y 2016–2026 de `temporadas_norte_centro_2016_2026.csv`. Para 2016–2026 faltan los días de pesca.

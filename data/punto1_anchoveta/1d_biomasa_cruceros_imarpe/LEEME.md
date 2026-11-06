# 1d. Biomasa de anchoveta por crucero de IMARPE

## Por qué importa
El Doc recomienda usar la **biomasa acústica por crucero** como y_t, porque mide abundancia y no depende de las cuotas. Aquí hay **dos medidas distintas**. No conviene mezclarlas sin avisarlo:

| Medida | Qué es | Archivo | Años |
|---|---|---|---|
| **Biomasa desovante** | Solo los adultos que se reproducen | `original_tabla1_biomasa_desovante_1964_2020.csv` | 1964–2020 (96 observaciones) |
| **Biomasa total** | Toda la anchoveta que ve el crucero, incluidos los juveniles | `biomasa_total_cruceros.csv` | 1998, 2004 y 2018–2026, con huecos |

Ejemplo: en el crucero 1802-04, la biomasa desovante fue 8,006 millones t y la biomasa total norte-centro 10,86 millones t.

## A. Biomasa desovante 1964–2020 (serie larga, una sola fuente)
- **Fuente:** IMARPE, Oficio N° 683-2021-IMARPE/PCD (09/08/2021). Se lo envió a la Sociedad Nacional de Pesquería para la certificación MSC. Su anexo es el borrador "Evaluación de la anchoveta del stock norte-centro" (modelo SPiCT), y la serie está en su **Tabla 1** (p. 32 del PDF).
- PDF: https://fisheryprogress.org/sites/default/files/documents_actions/IMARPE_Of.%20N%20683-2021-IMARPE-PCD_Evaluaci%C3%B3n%20alternativa%20de%20anchoveta%20usando%20un%20modelo%20estoc%C3%A1stico.pdf (copia en `fuentes_pdf/IMARPE_Oficio683-2021_evaluacion_stock_norte_centro.pdf`).
- **Cómo se obtuvo (01/11/2026):** se descargó con `curl`. Luego `extraer_tabla1_of683.py` (Python + PyMuPDF) lee la Tabla 1 fila por fila. Salieron 96 filas seguidas, del n.° 1 al 96.
  - Para repetirlo: `python extraer_tabla1_of683.py fuentes_pdf/IMARPE_Oficio683-2021_evaluacion_stock_norte_centro.pdf salida.csv`
- **Columnas:**
  - `n_obs`, `fuente` (nombre del crucero, p. ej. "Cr. 1802-04").
  - `mes_decimal`: año + fracción, p. ej. 2018.25 ≈ abril.
  - `biomasa_desovante_millones_t`.
  - `par_alfa`, `par_beta`: relación longitud-peso del crucero.
  - `indice`: 1 a 4. El artículo separa la serie en 4 índices según la fuente y la estación del año, porque la capturabilidad cambia.
- **Cómo la calculó IMARPE** (según el texto del documento):
  - Desde 1985: abundancia por talla de cada crucero × curva de madurez (φ = 21,01; θ = 1,88) × relación talla-peso.
  - Antes de 1985: biomasa total × 0,855.
  - 1964–1971 no son cruceros, sino un "Análisis de cohortes".
- **Limitaciones:**
  - Termina en abril de 2020.
  - Es un **borrador** de artículo, no la versión publicada.
  - Hay 0 a 5 cruceros por año, en meses irregulares.
- **Revisión:** los n.° 1 a 96 están seguidos y cada fila tiene sus 7 campos. Los valores no se compararon uno por uno con el PDF: conviene revisar algunos al azar.

## B. Biomasa total 2018–2026
- La mayoría de las filas son las que ya tenía el **Doc del equipo** ("Lo que encontre"), con su enlace. **No las volví a revisar.**
- **Verificado en el PDF:** 2302-03 = 6,45 millones t y 2309-11 = 7,72 millones t.
  - Fuente: Castillo P.R., Cuadros G., Grados D., Valdez C., Pozada M., Cornejo M. & La Cruz L. (2025), *Distribución y biomasa de anchoveta y otros pelágicos, El Niño 2023, Región Norte de la Corriente de Humboldt.*
  - Copia: `fuentes_pdf/Castillo_et_al_2025_ElNino2023_biomasa.pdf`.
- **Actualizado el 01/11/2026 (segunda búsqueda):**
  - **2402-04 = 9,97 millones t.** Biomasa estimada por IMARPE con la que se fijó la cuota 2024-I, según Andina y Agraria; esta última cita la RM 000118-2024-PRODUCE. Es coherente: un 55 % más que el verano de 2023 (6,45).
  - **2502-04 = 10,9 millones t.** Nota oficial de PRODUCE en gob.pe (14/07/2025): "biomasa observada en abril", "una de las más altas desde 1996".
  - **2609-10 = 5,12 millones t.** Nota oficial de PRODUCE en gob.pe (16/10/2026). El 79 % son juveniles en número y el 65 % en peso.
  - **2602-04 ≈ 7,10 millones t, DERIVADO.** La nota de octubre de 2026 dice que 5,12 es un 27,9 % menor que el verano de 2026, así que 5,12 / 0,721 ≈ 7,10. **No es una cifra publicada.**
- **Siguen faltando:**
  - **2409-11:** no se encontró la cifra publicada.
  - **2509-11:** PRODUCE no publicó la biomasa (Infobae, 02/11/2025).
- **⚠️ Contradicción:** PRODUCE dijo en 2025 que 10,9 era "un 40 % superior a la del año pasado". Frente a 9,97 sería solo un 9 % más. Lo más probable es que comparara con el crucero de **invierno** de 2024, que entonces rondaría 7,8 millones t, pero no está confirmado. Por eso 2409-11 quedó vacío.
- Dónde buscar lo que falta: el repositorio de IMARPE, los "Informes correspondientes a oficios" de gob.pe/imarpe o las RM de cada temporada en El Peruano, que a veces citan la biomasa.
- **Cuidado con la cobertura:** algunas cifras son de toda la costa y otras solo norte-centro. Lo dice la columna `cobertura`.

## C. Stock sur
`stock_sur_cruceros.csv`: pocos datos, casi todos tomados del Doc. El de 2309-10 salió de un resumen de búsqueda y hay que confirmarlo.

## Lo que falta para cerrar el punto 1
1. Los cruceros 2409-11 y 2509-11, y la cifra publicada de 2602-04 (sección B).
2. Decidir si se usa la desovante (1964–2020), la total (2018–2026) o ambas. No cubren los mismos años con la misma medida, así que hay que empalmarlas o elegir una. Esa decisión le toca al equipo.

# 1b. Desembarques mensuales de anchoveta por puerto (IMARPE, Bouchon et al. 2018), 1998–2003

## Qué es
Toneladas de anchoveta desembarcadas por **mes y por puerto** (26 columnas: 24 puertos, 3 regiones y el total del Perú). Sirve para cubrir **1998–2002**, los años que no tiene la serie del BCRP (`1a`, que empieza en 2003). Se incluyó también 2003 para poder comparar las dos fuentes.

## Fuente
- **Bouchon M, Ñiquen M, Franco M, Ttito H. 2018.** *Estadísticas de la pesquería pelágica en la costa peruana (1959-2015).* Inf Inst Mar Perú 45(4): 397-562.
- Según el resumen del artículo, los datos vienen de los **muestreos de IMARPE** en el litoral.
- Las páginas de las tablas dicen: **"Cifras no oficiales - Para uso científico"**.
- PDF: https://repositorio.imarpe.gob.pe/bitstream/20.500.12958/3302/5/Inf%2045%204%20Bouchon.pdf
- Tablas usadas (página del PDF): Tabla 40 = 1998 (p. 49), 41 = 1999 (p. 50), 42 = 2000 (p. 51), 43 = 2001 (p. 52), 44 = 2002 (p. 53), 45 = 2003 (p. 54).

## Cómo se obtuvo (01/11/2026)
1. Se descargó el PDF con `curl` desde el enlace de arriba (7,4 MB, sin cuenta). Está guardado aquí: `original_Bouchon_2018_Inf45-4_IMARPE.pdf`.
2. Las tablas vienen **giradas** en la página: en las pares están giradas para un lado y en las impares para el otro. Tienen celdas vacías, así que copiar el texto en orden mezcla los meses.
3. `extraer_tablas_bouchon.py` (Python + PyMuPDF) lee la **posición** de cada número en la página. Primero ubica la columna de los meses (ENE…DIC, TOTAL) y la fila de los nombres de los puertos. Luego asigna cada número al puerto de su columna y al mes más cercano.
   - Para volver a correrlo: `python extraer_tablas_bouchon.py original_Bouchon_2018_Inf45-4_IMARPE.pdf salida.json`
4. Con ese resultado se armaron los dos CSV.

## Revisión hecha
- En los 6 años, los 12 meses de cada puerto suman su TOTAL anual (diferencias de 1–3 t por redondeo de la tabla original).
- En todos los meses, los puertos suman su región (Norte, Centro, Sur) y las 3 regiones suman el total del Perú.
- Matarani no tiene desembarques ningún año. Pucusana tampoco en 2000 y 2003, ni Salaverry en 2003. Esas celdas quedaron vacías en el original.

Totales anuales del Perú (t): 1998: 1 018 449 · 1999: 6 610 183 · 2000: 9 137 410 · 2001: 6 051 027 · 2002: 7 904 017 · 2003: 5 130 646.

## Archivos
| Archivo | Contenido |
|---|---|
| `original_Bouchon_2018_Inf45-4_IMARPE.pdf` | El PDF completo, tal como se descargó. |
| `original_tablas40a45_por_puerto_1998_2003.csv` | Las tablas 40–45 copiadas tal cual (puerto × mes, con la fila TOTAL de cada año). Celda vacía = vacía en el PDF. |
| `desembarques_anchoveta_mensual_1998_2003_por_departamento.csv` | Mismo dato agrupado por departamento, con las mismas columnas que `1a`. |
| `extraer_tablas_bouchon.py` | Programa que lee las tablas del PDF. |

Puertos agrupados por departamento (para que coincida con `1a`):

| Departamento | Puertos |
|---|---|
| Piura | Paita, Parachique |
| La Libertad | Chicama, Salaverry |
| Ancash | Chimbote, Samanco, Casma, Huarmey |
| Lima | Supe, Végueta, Huacho, Chancay, Callao, Pucusana |
| Ica | Tambo de Mora (T.MORA), Pisco |
| Arequipa | Atico, La Planchada, Matarani, Mollendo |
| Moquegua | Ilo |

`norte_centro_t` = Piura a Ica. `sur_t` = Arequipa + Moquegua. Coincide con "REG.N+C" y "REG.SUR" del PDF. Ojo: en el PDF, Huarmey está en la región **Centro**, aunque pertenece a Ancash.

## ⚠️ No es la misma serie que la del BCRP
Al comparar **2003**, que está en las dos fuentes:
- Bouchon (IMARPE) suma **5 130 646 t** y el BCRP (PRODUCE) **5 335 511 t**. Bouchon da un 3,8 % menos.
- Hay meses que no coinciden. Por ejemplo, en marzo de 2003 en La Libertad, el BCRP registra 63 502 t y Bouchon 0 t. En enero y febrero, Bouchon registra algo en Piura y el BCRP no.
- Son fuentes distintas: IMARPE hace muestreo y sus cifras son "no oficiales", mientras que PRODUCE da la estadística oficial de harina y aceite.

**Consecuencia:** si se juntan 1998–2002 (Bouchon) con 2003–2026 (BCRP), hay que **avisarlo en el modelo**, por ejemplo con una variable indicadora de la fuente o haciendo las pruebas con y sin esos años. Esa decisión le toca al equipo.

## Dato extra
El PDF trae las mismas tablas mensuales por puerto desde **1959 hasta 2015** (Tabla 1 en adelante). Si el equipo necesita una serie larga con una sola fuente, se puede correr el mismo programa sobre más páginas.

# 1a. Desembarques mensuales de anchoveta (BCRP), 2003-01 a 2026-06

## Qué es
Toneladas de anchoveta desembarcadas en puerto **para harina y aceite** (consumo humano indirecto), por mes y por departamento. Es **captura**, no abundancia: depende de cuotas, vedas y esfuerzo (ver `1c`).

## Fuente
- **Banco Central de Reserva del Perú (BCRP), BCRPData.** Cuadro "Desembarque de anchoveta para harina y aceite por departamento y puerto (toneladas)".
- Página: https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/desembarque-de-anchoveta-para-harina-y-aceite-por-departamento-y-puerto
- Al pie del cuadro dice "Fuente: Ministerio de la Producción" (PRODUCE). Última actualización de las series según la página: 16-09-2026.
- Series usadas (código BCRP → columna):

| Código | Serie | Columna |
|---|---|---|
| RD12917DM | Piura - Total Puertos | `piura_t` |
| RD12921DM | La Libertad - Total Puertos | `la_libertad_t` |
| RD12924DM | Ancash - Total Puertos | `ancash_t` |
| RD12930DM | Lima - Total Puertos | `lima_t` |
| RD12938DM | Ica - Total Puertos | `ica_t` |
| RD12941DM | Arequipa - Total Puertos | `arequipa_t` |
| RD12948DM | Moquegua - Total Puertos | `moquegua_t` |
| RD12950DM | Total | `total_t` |

## Cómo se descargó (01/11/2026)
1. Se pidió la API pública del BCRP (no pide cuenta):
   `https://estadisticas.bcrp.gob.pe/estadisticas/series/api/RD12917DM-RD12921DM-RD12924DM-RD12930DM-RD12938DM-RD12941DM-RD12948DM-RD12950DM/json/2003-1/2026-12/esp`
2. Con `curl` el sitio responde una página anti-bots ("Pardon Our Interruption"), así que la consulta se hizo **desde Chrome**, abriendo primero la página del cuadro y luego pidiendo esa misma URL de la API.
3. La respuesta trae 282 meses (Ene.2003 a Jun.2026; julio de 2026 en adelante aún no está publicado).
4. Se copió tal cual a `original_bcrp_api_2003-01_2026-06.csv` (mismos valores y decimales que la API; solo cambia el formato de JSON a CSV).

**Para repetirlo a mano:** en la página del cuadro, marcar las 8 series, elegir el rango 2003-1 a 2026-12 y descargar en Excel. Debe dar los mismos números.

## Archivos
| Archivo | Contenido |
|---|---|
| `original_bcrp_api_2003-01_2026-06.csv` | Dato original. Columna `periodo_bcrp` con el formato del BCRP (`Ene.2003`). |
| `desembarques_anchoveta_mensual_2003_2026.csv` | El mismo dato con fecha `AAAA-MM` y dos columnas calculadas. |

Columnas calculadas:
- `norte_centro_t` = Piura + La Libertad + Ancash + Lima + Ica (stock norte-centro, aprox. 4°–15° S).
- `sur_t` = Arequipa + Moquegua (stock sur).

## Revisión hecha
- Sin meses faltantes ni repetidos (282 seguidos).
- En los 282 meses, la suma de los 7 departamentos coincide con el `Total` del BCRP (diferencia < 2 t).
- Totales anuales (millones de t): 2003 5,34 · 2004 8,80 · 2005 8,63 · 2010 3,33 · 2013 4,75 · 2014 2,26 · 2017 3,17 · 2018 6,04 · 2023 1,99 · 2024 4,64 · 2025 4,61.
- El total de 2013 (4,75 millones t) coincide con la cifra de anchoveta "escrita a mano" de `analisis.py` / `analisis2.py` (4 754,1 miles de t), cuya fuente no estaba anotada. Muy probablemente salió de esta serie.

## Limitaciones
- Solo **anchoveta para harina y aceite**: no incluye la de consumo humano directo (pequeña en volumen).
- Por departamento de **desembarque**, no por zona de captura.
- El corte norte-centro/sur por departamento es aproximado (Ica cae cerca de los 15° S).
- Los últimos meses pueden ser preliminares.

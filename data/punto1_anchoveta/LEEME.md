# Punto 1: variable de respuesta (anchoveta)

Esta carpeta es el trabajo de Ariana para el **punto 1, "Variable respuesta (lo que bloquea todo)"**, del Doc "Desafio Antartica". Se armó el 01/11/2026. Está separada de `..\datos\`.

Cada subcarpeta tiene su `LEEME.md` con la fuente, el archivo original, cómo se descargó, qué se revisó y qué falta.

| Carpeta | Qué hay | Periodo | Estado |
|---|---|---|---|
| `1a_desembarques_mensuales_bcrp\` | Desembarques mensuales por departamento (BCRP / PRODUCE) | 2003-01 a 2026-06 | ✅ Completo |
| `1b_desembarques_1998_2002_bouchon\` | Desembarques mensuales por puerto (IMARPE, Bouchon et al. 2018) | 1998–2003 | ✅ Completo, pero **no es la misma fuente** que 1a (en 2003 da un 3,8 % menos) |
| `1c_cuotas_y_temporadas\` | Fechas, cuotas, capturas y días de pesca de cada temporada norte-centro, más 10 normas en PDF | 1997–2026 | ⚠️ 1997–2015 completo (Bouchon); en 2016–2026 faltan fechas y días de pesca, y algunas cifras salen de prensa |
| `1d_biomasa_cruceros_imarpe\` | Biomasa desovante por crucero (1964–2020) y biomasa total por crucero | 1964–2026 | ⚠️ Faltan 2409-11 y 2509-11; 2602-04 es un valor derivado |

## Resumen para el equipo
- **Biomasa (lo que recomienda el Doc como y_t):** hay una serie larga de biomasa **desovante** por crucero, 1964–2020 (IMARPE, Oficio 683-2021, Tabla 1, 96 cruceros). Las cifras de 2018–2026 son biomasa **total**, que es otra medida. Solo faltan los cruceros de invierno de 2024 y 2025.
- **Desembarques mensuales:** 1998–2026 completo, pero con dos fuentes (IMARPE hasta 2002 y PRODUCE desde 2003).
- **Gestión (cuotas, temporadas y días de pesca):** 1997–2026 armado. Sirve si el y_t son desembarques. Los días de pesca 1997–2015 son una medida de esfuerzo (punto d).
- **Dato útil:** la cifra de anchoveta "escrita a mano" que usaban `analisis.py` y `analisis2.py` (2013: 4 754,1 miles de t) coincide con el total anual del BCRP. Lo más probable es que venga de ahí.

## Herramientas usadas
- `curl` para PDFs y normas.
- Chrome para la API del BCRP, que bloquea las descargas automáticas.
- Python 3.12 con PyMuPDF para leer las tablas de los PDF.
- Búsquedas web para ubicar fuentes (cada dato dice de dónde salió).

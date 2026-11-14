# Ronda de tendencias en seis variables

Fecha: 14/11/2026. Script: `ronda_seis_variables.py`. Tabla completa: `data/tablas_pruebas_pendientes/ronda_seis_variables.csv` (162 pruebas). Salida de consola: `data/tablas_pruebas_pendientes/ronda_seis_variables_salida.txt`.

## Objetivo
Comprobar si otras variables, además de la clorofila, muestran una tendencia detectable. Las variables se eligieron por criterio físico antes de ver los resultados: nivel del mar, hielo marino antártico, temperatura superficial de serie larga, oxígeno y temperatura a 100-200 m, y viento costero.

## Método
1. Anomalías mensuales: se resta la climatología mensual de cada serie.
2. Media anual (mínimo 9 meses con dato por año).
3. Mann-Kendall (tau de Kendall) y pendiente de Sen; el intervalo del 95 % de Sen se calcula con el método de rangos de Gilbert.
4. Varios periodos de inicio por variable (completo, 1998, 2003, 2010, y 1979, 1980, 1990, 1950, 1900 cuando la serie lo permite).
5. Dos variantes: todos los años, y sin los años de El Niño extremo (1998, 2016, 2023).
6. FDR de Benjamini-Hochberg sobre las 162 pruebas. Las pruebas de una misma variable en distintos periodos no son independientes, así que el FDR es una guía y no una garantía.

## Fuentes
| Variable | Fuente | Archivo |
|---|---|---|
| Nivel del mar | Reanálisis GLORYS12 (`zos`, panel de conectividad, región Humboldt); mareógrafos PSMSL (Matarani, Talara, Chimbote, San Juan, Callao) | `drive_aaron/connectivity_panel_monthly.csv`; `datos/peru/nivel_mar_mareografos/` |
| Hielo marino antártico | NSIDC G02135, extensión mensual 1979-2026 | `datos/pesquerias/hielo_antartico_nsidc/` |
| TSM de serie larga | NOAA ERSST v5 (cajas 0-10°S 90-80°O y 18-10°S 80-70°O) | `datos/tendencias_largas/ersstv5_sst_mnmean.nc` |
| TSM satelital | Monitor de la web (cinco zonas) | `monitor_data.json` |
| Oxígeno y temperatura 100-200 m | Panel de conectividad (CMEMS, región Humboldt) | `connectivity_panel_monthly.csv` |
| Viento | Series de la web (`datos.js`), CCMP hasta 2018 y ERA5 después | `datos.js` |

## Resultados (pendiente de Sen por década, todos los años)
| Variable | Periodo | n | Pendiente/década (IC 95 %) | q (FDR) |
|---|---|---|---|---|
| Temperatura 100-200 m, Humboldt (°C) | 1998-2025 | 28 | +0,16 (0,04 a 0,28) | 0,052 (no significativo; al límite) |
| Temperatura 100-200 m, Humboldt (°C) | 2003-2025 | 23 | +0,26 (0,10 a 0,40) | 0,015 |
| Temperatura 100-200 m, Humboldt (°C) | 2010-2025 | 16 | +0,37 (0,04 a 0,57) | 0,104 (no significativo) |
| Nivel del mar GLORYS, Humboldt (m) | 1998-2025 | 28 | +0,026 (0,020 a 0,033) | 0,0001 |
| Nivel del mar GLORYS, Humboldt (m) | 2010-2025 | 16 | +0,027 (0,008 a 0,049) | 0,049 (al límite) |
| Hielo marino antártico (M km²) | 1979-2026 | 48 | −0,03 (−0,15 a 0,10) | 0,83 (no significativo) |
| Hielo marino antártico (M km²) | 1998-2026 | 29 | −0,43 (−0,61 a −0,07) | 0,046 (al límite) |
| Hielo marino antártico (M km²) | 2010-2026 | 17 | −1,16 (−1,71 a −0,49) | 0,018 |
| TSM ERSST norte-centro (°C) | 1900-2026 | 127 | +0,077 (0,042 a 0,111) | 0,0008 |
| TSM ERSST norte-centro (°C) | 1979-2026 | 48 | +0,04 (−0,12 a 0,20) | 0,74 (no significativo) |
| TSM ERSST norte-centro (°C) | 1998-2026 | 29 | +0,17 (−0,18 a 0,59) | 0,64 (no significativo) |
| TSM ERSST costa sur (°C) | 1900-2026 | 127 | +0,105 (0,071 a 0,141) | < 0,0001 |
| TSM ERSST costa sur (°C) | 1979-2026 | 48 | −0,03 (−0,16 a 0,10) | 0,85 (no significativo) |
| Oxígeno 100-200 m, Humboldt (mmol/m³) | 1998-2025 | 28 | +1,6 (−3,7 a 5,6) | 0,64 (no significativo) |
| Oxígeno 100-200 m, Humboldt (mmol/m³) | 2003-2025 | 23 | +5,4 (1,7 a 12,3) | 0,018 |
| TSM satelital, cinco zonas (°C) | 1998-2025, 2003-2025, 2010-2025 | 16-28 | −0,24 a +0,34 | todas ≥ 0,33 (no significativas) |

Sin los años de El Niño extremo (q con FDR sobre las 162 pruebas): siguen significativos la temperatura 100-200 m (desde 1999, q 0,028, y desde 2003, q 0,021), el nivel del mar GLORYS (desde 1999 y 2003; desde 2010 queda en q 0,052, no significativo), el hielo solo desde 2010 (q 0,039; desde 2003 pasa a q 0,060 y desde 1999 a q 0,142) y el oxígeno desde 2003 (q 0,018).

Nota de corrección (14/11/2026): una versión anterior de esta tabla traía valores q de la primera corrida (146 pruebas). Los valores actuales son los de `ronda_seis_variables.csv` (162 pruebas, 38 significativas con FDR 5 %). Los p y las pendientes no cambian. Con la corrección, la temperatura a 100-200 m desde 1998 ya no es significativa con FDR (q 0,052).

## Lectura
- **Nivel del mar GLORYS y temperatura 100-200 m**: son las dos tendencias más consistentes. La del nivel del mar se mantiene en los tres periodos (en 2010-2025 con q 0,049, al límite) y sin los años de El Niño desde 1999 y 2003. La de temperatura a 100-200 m es significativa desde 2003, está al límite desde 1998 (q 0,052) y deja de serlo desde 2010 (n=16).
- **Hielo marino, TSM de serie larga y oxígeno**: la significancia depende del año de inicio. El hielo cae desde 1998 pero no hay tendencia en 1979-2026; la TSM de ERSST sube desde 1900 o 1950 pero no desde 1979; el oxígeno solo es significativo desde 2003. Es el mismo comportamiento ya observado con la clorofila.
- **TSM satelital por zona (1998-2025)**: ninguna tendencia significativa.

## Advertencias
1. **Viento: resultado descartado.** La primera corrida dio caídas "significativas" en las cinco zonas, pero la rapidez del viento en Callao baja de ~6,1 m/s (2012-2016) a ~4,5 m/s (2017-2019) y vuelve a ~6,0 m/s desde 2020, lo que apunta a un cambio de fuente (CCMP termina en 2018). Se recortó a 1993-2016. En ese tramo solo la componente meridional de Chimbote y Callao baja de forma significativa (n=14 a 19); Paita, Pisco e Ilo no. No se considera un hallazgo.
2. **Mareógrafos.** Callao baja unos 1,3 cm/década desde 1970 (nivel relativo, que incluye movimiento vertical de la costa), pero entre 1998 y 2024 no hay tendencia significativa. No es comparable con la serie GLORYS.
3. **Reanálisis.** GLORYS12 y el panel de conectividad son productos de modelo con asimilación de datos, no observaciones directas. Las tendencias subsuperficiales pueden incluir deriva del modelo.
4. **Pruebas anuales.** Las medias anuales no incorporan corrección por autocorrelación; con n pequeño (14 a 17) los intervalos son anchos.
5. **Años excluidos.** El criterio (1998, 2016, 2023) es una elección y no se probó otro conjunto.

## Reproducir
Las rutas de entrada del script son absolutas (`D:/hackathon/NASA/...`); hay que ajustar la variable `R` al inicio. Requiere `numpy`, `pandas`, `scipy`, `xarray` y `netCDF4`. Ejecutar con `PYTHONIOENCODING=utf-8`.

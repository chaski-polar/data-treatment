# Pruebas posibles pendientes

Fecha: 13 de noviembre de 2026. Ninguna de estas pruebas se ha ejecutado todavía; las relaciones esperadas son hipótesis, no resultados.

## Criterio para aceptar un resultado

Casi toda correlación positiva en estas series comparte un factor común, El Niño. Por eso la relación fitoplancton → anchoveta (r = 0,78) no se considera robusta: depende de 1998. Una relación solo cuenta si cumple todo lo siguiente:

1. Sigue en pie después de controlar Niño 1+2 (correlación parcial).
2. Usa n efectivo para corregir la autocorrelación (Pyper y Peterman, 1998).
3. Pasa la corrección por pruebas múltiples (FDR, p_fdr < 0,05).
4. Se mantiene al quitar el año 1998.
5. Se mantiene al ajustar con un periodo y comprobar con otro (por ejemplo 1998-2014 y 2015-2025).

Si no se cumplen, se reporta como "no se encontró relación". Hasta ahora se hicieron más de 900 pruebas, así que cada prueba nueva aumenta la probabilidad de un hallazgo falso.

## A. Costa peruana

| # | Prueba | Relación esperada | Datos | Estado de los datos |
|---|---|---|---|---|
| A1 | Clorofila por zona → desembarques mensuales BCRP, desfase de 2 a 4 meses | Positiva | variables_mensuales.csv y punto1_anchoveta (BCRP 2003-2026) | Listos |
| A2 | Turbidez (Kd490) frente a clorofila y a oxígeno | Positiva | variables_mensuales.csv; oxígeno de CMEMS | Kd490 listo; oxígeno en descarga |
| A3 | Viento local ERA5 (sustituto de surgencia) frente a clorofila de cada zona | Positiva, con matices por zona | ERA5 solo mar, ya incorporado | Listos |
| A4 | Asimetría térmica (calor baja la clorofila cerca de −30 %/°C, frío casi no la modifica) usada como predicción de 2026 con El Niño en curso | Negativa con calor | Niño 1+2 PSL, clorofila local | Listos, hasta donde llegue la serie de 2026 |
| A5 | Nivel del mar frente a Perú como indicador adelantado de la clorofila (ondas Kelvin), desfase de 1 a 3 meses | Positiva | zos de CMEMS | En descarga |

Observaciones:
- A1: los desembarques dependen también de cuotas y vedas, no solo de la abundancia. Conviene controlar la temporada de pesca o usar las temporadas (cuota y días de pesca) como covariable.
- A2: Kd490 se deriva en parte de la misma observación de color del océano que la clorofila, de modo que parte de la correlación con clorofila es mecánica. El interés real está en la relación con el oxígeno.
- A3: el viento de Ilo en CCMP es sospechoso (r = −0,35 frente a ERA5); usar ERA5.

## B. Antártida y Pacífico Sur

Contexto: entre la Antártida y la costa peruana no salió nada que resistiera la corrección (H1a, H1b y H1e, más de 900 pruebas). El desfase de 3 a 4 años desapareció al quitar El Niño. Lo que sigue busca relaciones de la Antártida con otras variables, no un vínculo directo con la costa.

Pistas previas, sin control completo (pueden caer): SAM frente a clorofila de Rey Jorge (r = +0,50); hielo marino frente a jurel de Chile (r ≈ −0,55); clorofila de Rey Jorge frente a calamar argentino del año siguiente (r = +0,60).

| # | Prueba | Relación esperada | Datos | Estado de los datos |
|---|---|---|---|---|
| B1 | El Niño → Antártida: Niño 1+2 y ONI frente a hielo marino, SAM y clorofila de Rey Jorge, con desfases | A definir; es una teleconexión descrita en la literatura (Bellingshausen y Amundsen) | PSL, NSIDC G02135, clorofila local | Listos |
| B2 | SAM × El Niño: si el efecto del SAM sobre la clorofila cambia según la fase de El Niño | Interacción | Los mismos | Listos |
| B3 | Cadena con puente: hielo o SAM → temperatura o nutrientes del Pacífico Sur (40 a 45° S) → clorofila peruana, cada eslabón con su desfase | Positiva o negativa por eslabón | Variables satelitales del Pacífico Sur; nutrientes de CMEMS | Parcial |
| B4 | Corrientes de la zona de origen de Humboldt frente a temperatura y nutrientes del norte (no frente a clorofila) | A definir | Corrientes (hasta 2018) | Limitado |
| B5 | Hielo marino y SAM frente a otras especies de la FAO (jurel, calamar, merluza), con control de El Niño | A definir | FAO GlobalProduction 1950-2024, NSIDC | Listos |

Observaciones:
- B5: las capturas no son abundancia (las afectan cuotas y esfuerzo) y la serie anual tiene pocos puntos, de modo que la potencia estadística es baja.
- B4: las corrientes antárticas ya entraron como predictores en H1e sin resultado; las de Humboldt llegan solo hasta 2018.

## Viabilidad para probar ahora

Orden sugerido según datos disponibles, aporte al reto y riesgo de falso positivo.

| Prioridad | Prueba | Motivo |
|---|---|---|
| 1 | A4 Predicción 2026 con la asimetría | Datos listos; es el hallazgo más distintivo; permite una demostración en tiempo real |
| 2 | A1 Clorofila → desembarques mensuales | Datos listos; la serie mensual (más de 280 meses) tiene más potencia que la anual |
| 3 | B1 El Niño → Antártida | Datos listos; es el vínculo con más respaldo en la literatura |
| 4 | A3 Viento ERA5 frente a clorofila | Datos listos; interpretación física clara |
| 5 | A5 Nivel del mar como indicador adelantado | Alto valor si sale, pero depende de la descarga de CMEMS |
| 6 | B5 Otras especies de la FAO | Datos listos, pero poca potencia estadística |
| 7 | B2 SAM × El Niño | Se puede hacer con datos mensuales; riesgo de sobreajuste |
| 8 | A2 Kd490 frente a oxígeno | Útil solo con el oxígeno; con clorofila es en parte mecánica |
| 9 | B3 Cadena con puente | Muchos eslabones y pruebas; mayor riesgo de falso positivo |
| 10 | B4 Corrientes | Datos hasta 2018 y antecedentes negativos |

## Datos descargados para estas pruebas

CMEMS (cuenta gratuita de Copernicus Marine), caja del Perú (85° O a 70° O, 18,35° S a 3,38° S), descarga año por año en `datos/copernicus/anual/`:
- `ssh_AAAA.nc`: nivel del mar (zos), producto físico de reanálisis a 0,083°, mensual.
- `bgc_AAAA.nc`: clorofila, nitrato, fosfato, oxígeno y fitoplancton (chl, no3, po4, o2, phyc), 0 a 5 m, 0,25°, mensual.

Script: `datos/actualizacion_pagina/descargar_cmems_anual.py`. La descarga se hace por años porque pedir toda la serie de una vez agotó la memoria del equipo.

No se descargó Giovanni (MODIS-Aqua): requiere iniciar sesión con una cuenta Earthdata.

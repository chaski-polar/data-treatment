# Resultados de las pruebas pendientes (13 de noviembre de 2026)

Script: `pruebas_pendientes.py`. Tablas: `tablas/pendientes_A1…`, `A3…`, `A4…`, `B1…`. Solo datos locales (monitor mensual 1998-2026, desembarques BCRP 2003-2026, viento ERA5 sobre el mar).

Criterio de aceptación (ver `PRUEBAS_POSIBLES.md`): correlación parcial con Niño 1+2, n efectivo de Pyper y Peterman, FDR (p_fdr < 0,05), misma dirección sin 1998 y en las dos mitades del periodo.

## Resumen

| Prueba | Pruebas realizadas | Resultado |
|---|---|---|
| A4 Asimetría como predicción | 5 zonas × 2 periodos de comprobación | La asimetría no mejora a un modelo lineal fuera de muestra; 2026 no se puede comprobar todavía |
| A1 Clorofila → desembarques mensuales | 100 | Ninguna robusta |
| B1 El Niño → Antártida | 104 | Ninguna robusta |
| A3 Viento ERA5 → clorofila | 40 | Ninguna robusta |

Las tres relaciones (A1, B1, A3) se reportan como "no se encontró relación robusta". Ninguna supera la corrección por pruebas múltiples.

## A4. Asimetría térmica como predicción

Se ajustó clorofila (anomalía en %) frente a la anomalía de temperatura con tres modelos (sin modelo, lineal y asimétrico, con pendientes distintas para calor y frío) sobre 1998-2014 y se comprobó en 2015-2025.

- Con calor, la pendiente ajustada es negativa en todas las zonas: Chimbote −25,8 %/°C, Callao −26,3, Ilo −30,1, Pisco −18,2, Paita −6,0. Con frío es cercana a cero en Chimbote (−4,0) y Pisco (+4,5), pero no en Callao (−14,0) ni en Ilo (−14,6).
- Fuera de muestra, tanto el modelo lineal como el asimétrico reducen el error respecto a no usar modelo en Chimbote (de 38,0 a 33,1 y 33,4), Callao (de 41,8 a 38,7 y 39,2) e Ilo (de 55,6 a 52,9 y 52,4). En Paita no mejoran.
- El modelo asimétrico no supera al lineal de forma consistente (mejora de −1,4 % a +1,6 %). La asimetría describe los datos de ajuste, pero no aporta capacidad de predicción adicional.
- Para 2026 solo hay un mes de clorofila por zona (enero), insuficiente para evaluar la predicción.

Consecuencia: la asimetría debe presentarse como un patrón descriptivo (el efecto se concentra con calor), no como un predictor mejor que la relación lineal.

## A1. Clorofila → desembarques mensuales

Desembarques de anchoveta en escala log1p, sin estacionalidad, con la clorofila adelantada de 0 a 4 meses, con y sin control de Niño 1+2, para todos los meses y solo para los meses con pesca.

- Ninguna combinación pasa FDR. La más alta es Chimbote con 1 mes de adelanto, solo en meses con pesca: r = 0,24 (p_fdr = 0,07). Mantiene la dirección sin 1998 (la serie empieza en 2003, por lo que no hay 1998) y en las dos mitades, pero no es significativa.
- Los desembarques dependen de cuotas y vedas, que esta prueba no controla del todo.

## B1. El Niño → Antártida

Niño 1+2 y ONI frente a hielo marino, SAM y clorofila de Rey Jorge y de la Península Antártica, con adelantos de 0 a 12 meses.

- Ninguna combinación pasa FDR (p_fdr ≥ 0,95 en las más altas).
- La mayor es Niño 1+2 frente a hielo marino (r = −0,16, n efectivo 84): débil y no significativa.

## A3. Viento ERA5 → clorofila

Viento a favor de la surgencia (componente hacia el noroeste), sin estacionalidad, frente a la clorofila de cada zona, de 0 a 3 meses de adelanto.

- Ninguna combinación pasa FDR. Las más altas son Ilo con r ≈ −0,22 (p_fdr = 0,22): el signo es contrario a lo esperado y el viento de Ilo ya era dudoso.

## Qué se puede decir y qué no

- Sí: no se encontró relación robusta entre la clorofila y los desembarques mensuales, el viento local ni El Niño → Antártida, con el criterio indicado.
- No: no corresponde afirmar que la asimetría predice mejor que la relación lineal, ni sugerir un vínculo con la Antártida.
- Quedan sin probar B2, B3, B4, B5, A2 y A5 (esta última depende de la descarga de nivel del mar de CMEMS).

---

# Segunda tanda: A5, A2, B2, B3, B4 y B5

Script: `pruebas_pendientes_2.py`. Para las pruebas con nivel del mar, corrientes, oxígeno y nitrato se usó el panel de conectividad (`connectivity_panel_monthly.csv`, 1998-2025, seis regiones), que ya trae esas variables, así que no fue necesaria la descarga de CMEMS. Mismo criterio de aceptación.

| Prueba | Pruebas realizadas | Robustas |
|---|---|---|
| A5 Nivel del mar → clorofila | 50 | 10, todas sin controlar Niño 1+2; con control, 0 |
| A2 Kd490 → oxígeno y clorofila | 16 | 5, todas con la clorofila (relación mecánica) |
| B2 SAM × El Niño | 6 | 0 |
| B3 Cadena con puente | 240 (156 + 84) | 0, ninguna cadena completa |
| B4 Corrientes → temperatura y nitrato | 208 | 0 |
| B5 Otras especies de la FAO | 128 | 0 |

## A5. Nivel del mar frente a Perú → clorofila

- Sin controlar El Niño hay 10 combinaciones robustas: Callao (r = −0,28, sin adelanto), Chimbote (r = −0,40), y Paita con signo positivo a 3 y 4 meses de adelanto (r = +0,24).
- Al controlar Niño 1+2 no queda ninguna. El nivel del mar es, en lo esencial, otra manera de medir El Niño: sube cuando la clorofila baja, y la relación más fuerte ocurre sin adelanto (lo contrario de un indicador adelantado) y decae al aumentar el desfase.
- Paita (positivo con adelanto de 3 a 4 meses) cumple el criterio solo sin control de El Niño; no se debe presentar como relación independiente.
- Conclusión: no hay evidencia de que el nivel del mar anticipe la clorofila más allá de lo que ya explica El Niño.

## A2. Kd490 → oxígeno y clorofila

- Con la clorofila OC-CCI, r = 0,99 sin adelanto: es una relación mecánica (Kd490 se deriva de la misma observación del color del océano) y no es un resultado.
- Con el oxígeno del panel no hay relación robusta.

## B2. SAM × El Niño

Interacción SAM × Niño 1+2 sobre la clorofila de Rey Jorge, de la Península Antártica y el hielo marino, con Niño adelantado 0 y 6 meses, prueba por desplazamiento circular. Ninguna interacción es significativa (p_fdr entre 0,55 y 0,75).

## B3. Cadena con puente

- Eslabón 1 (SAM o hielo → temperatura, nitrato o clorofila del Pacífico Sur, 0 a 12 meses): 156 pruebas, ninguna robusta (p_fdr ≥ 0,57).
- Eslabón 2 (Pacífico Sur → clorofila de Chimbote y Callao, 0 a 6 meses): 84 pruebas, ninguna robusta (p_fdr ≥ 0,36).
- No hay ninguna cadena con los dos eslabones robustos.

## B4. Corrientes

Componentes de la corriente en la transición de Humboldt y el Pacífico Sur intermedio frente a temperatura y nitrato del Perú, con 0 a 12 meses de adelanto, con y sin control de El Niño. Ninguna es robusta. La mayor es la corriente zonal (uo) en la transición de Humboldt frente a la temperatura con 1 mes de adelanto: r = 0,29 (p_fdr = 0,057), sin pasar el umbral.

## B5. Otras especies de la FAO

Pota, jurel, sardina, concha, anchoveta de Chile y krill frente a hielo marino y SAM, con la tendencia lineal quitada y de 0 a 3 años de adelanto. Ninguna es robusta (p_fdr ≥ 0,39). Los coeficientes más altos son los que ya conocíamos (jurel del Perú y hielo r ≈ −0,65 a 2 años; pota y SAM r ≈ −0,55), pero con 24 a 26 años de datos y n efectivo de 15 a 23 no resisten la corrección por pruebas múltiples. No se pudo comprobar la consistencia por mitades porque cada mitad tiene muy pocos años.

## Balance de las pruebas

De unas 940 pruebas nuevas (A1, A3, A4, B1 a B5, A2, A5), solo dos grupos pasan el criterio: la relación mecánica Kd490–clorofila y el nivel del mar sin control de El Niño. En ambos casos no son hallazgos independientes. El resultado general es consistente con lo anterior: El Niño explica casi todo lo que se ve en la costa y no se encontró un vínculo antártico robusto.

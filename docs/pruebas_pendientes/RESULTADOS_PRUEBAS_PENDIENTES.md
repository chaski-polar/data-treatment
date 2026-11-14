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

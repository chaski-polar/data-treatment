# Seguimiento de pruebas

Registro de lo que se ha probado, con qué datos, qué resultó y en qué estado queda. Se actualiza cada vez que se corre algo nuevo. Fecha de la última actualización: 14 de noviembre de 2026.

Criterio de aceptación para relaciones entre variables: correlación parcial con Niño 1+2, n efectivo (Pyper y Peterman, 1998), FDR (p_fdr < 0,05), misma dirección sin 1998 y en las dos mitades del periodo. Para tendencias: Mann-Kendall con pendiente de Sen (p < 0,05), repetido con otro método, otra estación y otro periodo.

## 1. Pruebas de relación entre variables

| Id | Fecha | Prueba | Datos | Pruebas | Resultado | Estado |
|---|---|---|---|---|---|---|
| H1a, H1b | 08/11 | Fitoplancton antártico → fitoplancton peruano | OC-CCI, 50 desfases | 50 | 0 con FDR | Descartada |
| H1d | 08/11 | El Niño → clorofila peruana | Niño 1+2, clorofila por zona | — | Fuerte: r ≈ −0,47 en Chimbote y Callao | Confirmada |
| H1e | 08/11 | Ambiente austral (hielo, SAM, temperatura, corrientes) → clorofila y carbono peruano | Panel + índices | 180 | 0 con FDR | Descartada |
| H1c | 08/11 | Fitoplancton → anchoveta | Cruceros y RAM Legacy | — | Débil; depende de 1998 | No robusta |
| Reglas de asociación | 08/11 | Apriori (1998-2014 / 2015-2025) | Monitor mensual | 218 candidatas | Solo "mar cálido → clorofila baja" | Sin novedad |
| Profundidad y altimetría | 08/11 | Antártida y Pacífico Sur, superficie y profundidad | AVISO, panel | más de 600 | 0 con FDR; el desfase de 3-4 años era El Niño | Descartada |
| Asimetría | 08/11 | Calor baja la clorofila (−18 a −33 %/°C), frío no sube | Monitor | — | Patrón descriptivo, p ≈ 0,002 | Ver A4 |
| A1 | 13/11 | Clorofila → desembarques mensuales (BCRP) | 2003-2026 | 100 | 0 robustas; mejor: Chimbote +1 mes, r = 0,24, p_fdr = 0,07 | Sin relación robusta |
| A3 | 13/11 | Viento ERA5 → clorofila | 5 zonas | 40 | 0 robustas | Sin relación robusta |
| A4 | 13/11 | Asimetría como predicción (1998-2014 → 2015-2025) | Monitor | 5 zonas | El modelo asimétrico no mejora al lineal; 2026 solo tiene 1 mes de clorofila | Descriptiva, no predictiva |
| B1 | 13/11 | El Niño → Antártida (hielo, SAM, clorofila) | Monitor | 104 | 0 robustas | Sin relación robusta |
| A5 | 13/11 | Nivel del mar → clorofila | Panel (1998-2025) | 50 | 10 robustas solo sin controlar El Niño; con control, 0 | Es otra medida de El Niño |
| A2 | 13/11 | Kd490 → oxígeno y clorofila | Monitor, panel | 16 | Solo la relación mecánica con clorofila (r = 0,99) | Sin hallazgo |
| B2 | 13/11 | SAM × El Niño | Monitor | 6 | 0 | Sin relación |
| B3 | 13/11 | Cadena con puente (Antártida → Pacífico Sur → Perú) | Panel | 240 | 0; ninguna cadena completa | Sin relación |
| B4 | 13/11 | Corrientes → temperatura y nitrato | Panel | 208 | 0; mejor: uo en la transición de Humboldt, r = 0,29, p_fdr = 0,057 | Sin relación robusta |
| B5 | 13/11 | Hielo y SAM → otras especies (FAO) | FAO 1995-2024 | 128 | 0; coeficientes altos con n efectivo de 15 a 23 | Poca potencia |

Total de la tanda del 13/11: unas 900 pruebas. Con p < 0,05 sin corregir hay unas 150 (por azar se esperan unas 45); con FDR solo quedan la relación mecánica Kd490–clorofila y el nivel del mar sin control de El Niño.

Detalle: `RESULTADOS_PRUEBAS_PENDIENTES.md`. Hipótesis y viabilidad: `PRUEBAS_POSIBLES.md`. Tablas: `tablas/pendientes_*.csv`.

## 2. Tendencias (lo que pide el reto)

Script: `tendencias.py`. Tablas: `tablas/tendencias_resumen.csv` y `tablas/tendencias_sensibilidad_inicio.csv`.

Qué se calculó para cada serie: Mann-Kendall anual con pendiente de Sen (media del año, solo verano, solo invierno); Mann-Kendall estacional de Hirsch sobre la serie mensual; regresión mensual sin estacionalidad con n efectivo; sensibilidad al año de inicio.

Series usadas:
- Temperatura superficial: CRW v3.1 (NOAA), 1986-2025, 5 km; y ERSST v5 (NOAA), 1950-2025, malla de 2 grados.
- Clorofila: OC-CCI v6 (ESA), 1998-2025; y MODIS-Aqua (NASA, Giovanni) para Chimbote, 2003-2025.

### Resultados

1. **Clorofila peruana, sin tendencia anual significativa** en ninguna zona (OC-CCI 1998-2025, p entre 0,13 y 0,80). Con la prueba estacional mensual salen p < 0,05 en Chimbote, Pisco e Ilo, pero ese p no corrige la autocorrelación mensual y es demasiado optimista; con la regresión mensual y n efectivo ninguna es significativa (Ilo, p = 0,053, es la más cercana).
2. **Chimbote depende del producto y del periodo.** Con OC-CCI 2003-2025 la caída es significativa (p = 0,033); con OC-CCI 1998-2025 no (p = 0,23); con MODIS-Aqua 2003-2025 tampoco (p = 0,68). Los dos productos se parecen (r = 0,79 en 280 meses) pero MODIS-Aqua da valores más altos (media 3,29 frente a 2,27 mg/m³).
3. **Calentamiento antártico: no es robusto.**
   - Con CRW y periodo 1998-2025: Rey Jorge +0,18 °C por década (p = 0,002) y Península +0,16 (p = 0,030).
   - Con CRW y periodo 1986-2025 (40 años): Rey Jorge +0,02 (p = 0,64) y Península −0,01 (p = 0,76). Desaparece.
   - Con CRW desde 2005 o 2010: sin tendencia (p = 0,57 a 0,98).
   - Con ERSST sobre 1950-2025: Rey Jorge +0,06 (p < 0,001) y Península +0,03 (p = 0,003), pero con ERSST desde 1986 la pendiente es negativa (−0,08, p = 0,02) y desde 1998 casi nula (p = 0,80). Los dos productos no coinciden en el mismo periodo.
   - Conclusión: el resultado significativo de 1998-2025 se debe al periodo elegido y al producto, y no resiste una serie más larga ni otro conjunto de datos. Se reporta como no robusto.
4. **Temperatura peruana:** con CRW 1986-2025 no hay tendencia significativa en las zonas del norte y centro; Ilo muestra un descenso (anual p = 0,059; mensual con n efectivo p = 0,053). ERSST 1950-2025 sí da calentamiento (+0,10 a +0,16 °C por década, p < 0,05 en cuatro zonas), pero su malla de 2 grados no resuelve bien la costa con afloramiento.

### Cómo se debe presentar

Con la serie larga disponible, la afirmación sostenible es "no se detecta una tendencia significativa y robusta en la clorofila peruana, ni en la temperatura antártica, en el periodo de satélite". Un resultado que cambia de signo al mover el año de inicio es una advertencia metodológica válida para la herramienta (mostrar la sensibilidad al periodo).

## 3. Datos

| Dato | Ubicación | Estado |
|---|---|---|
| Clorofila MODIS-Aqua, Chimbote, 2002-07 a 2025-11 (Giovanni) | `datos/giovanni/chimbote_modisa_chl_mensual_2002-2025.csv` | Descargado |
| Clorofila MODIS-Aqua, Paita, 2002-07 a 2025-11 (Giovanni) | `datos/giovanni/paita_modisa_chl_mensual_2002-2025.csv` | Descargado (tardó unos 4 minutos) |
| Giovanni: Callao, Pisco, Ilo, Rey Jorge, Península | — | Pendiente. Cada zona tarda varios minutos. |
| ERSST v5 mensual 1854-2026 (NOAA PSL, 162 MB) | `datos/tendencias_largas/ersstv5_sst_mnmean.nc` | Descargado; no se sube al repositorio |
| CRW v3.1 (temperatura 1986-2025) | `datos/peru/variables_mensuales.csv` | Ya disponible |
| CMEMS año por año (nivel del mar, nutrientes) | `datos/copernicus/anual/` | Detenida: el panel de conectividad ya traía esas variables hasta 2025 |

Series más largas posibles: clorofila satelital continua no existe antes de 1997 (SeaWiFS), de modo que la clorofila no puede extenderse; la temperatura sí (CRW desde 1986, ERSST desde 1854, de modo que se puede usar desde 1950).

## 5. Enfoques nuevos (14/11)

Scripts: `enfoques_nuevos.py` (E1 a E3), `enfoque_adelanto.py` (E4), `enfoque_lluvia_paita.py` (E5). Tablas: `tablas/nuevos_E*.csv`.

| Id | Prueba | Resultado | Estado |
|---|---|---|---|
| E1 | Tendencia de los eventos extremos: meses por año con clorofila ≤ −30 % (1998-2025) y con temperatura ≥ +1 °C sobre 1986-2015 (1986-2025; +0,5 °C en la Antártida) | 14 pruebas; ninguna significativa con FDR (la más baja: Península, clorofila baja, p = 0,043 sin corregir, p_fdr = 0,58) | Sin tendencia |
| E2 | Tendencia de la fenología de la clorofila: amplitud estacional, valor y mes del pico anual | 21 pruebas; ninguna con FDR (Paita, valor del pico, p = 0,03 sin corregir) | Sin tendencia |
| E3 | Estudio de eventos de El Niño: relación entre la intensidad del pico y la caída de la clorofila, y recuperación | Solo 4 eventos con Niño 1+2 ≥ 1,5 °C (1998, 2015, 2023 y 2026, este último sin terminar): insuficiente | No concluyente |
| E4 | Capacidad de adelanto: Niño 1+2 y ONI frente a la clorofila, 0 a 8 meses | 135 pruebas, 24 robustas (ver abajo) | Un resultado nuevo |
| E5 | ¿La lluvia explica el hallazgo de Paita? (NASA POWER) | No: la relación sigue igual al quitar la lluvia | Sin explicación |
| E6 | Contraste de E4 con una segunda fuente: clorofila MODIS-Aqua (NASA, Giovanni), Paita, 2002-07 a 2025-11 | Misma dirección y forma, pero no significativa con FDR (r = +0,16 a +0,22 a 2-8 meses; p_fdr de 0,05 a 0,13) | E4 se debilita: candidato no confirmado |

### E4. Respuesta tardía en Paita–Sechura

- La clorofila de Paita–Sechura **sube** entre 2 y 8 meses después de un calentamiento de Niño 1+2, con el máximo a 5 meses: r = +0,36 (p_fdr < 0,001). Pasa FDR en todos los desfases de 2 a 8 meses, mantiene la dirección sin 1998 (r = +0,29) y en las dos mitades del periodo (+0,41 y +0,33), y al quitar un año cualquiera r se mantiene entre +0,29 y +0,39.
- Con desfase 0 no hay relación (r = +0,05). Es un efecto de rebote retrasado, no la caída simultánea que se ve en el centro de la costa.
- En las otras zonas el mismo desfase no repite el signo: Chimbote −0,22, Callao −0,18, Pisco +0,06, Ilo −0,08. Es un patrón del norte.
- Kd490 (turbidez) de Paita muestra el mismo patrón retrasado (r = +0,34 a 5 meses), de modo que el aumento no es exclusivo de la clorofila.
- ONI no aporta adelanto: al controlar Niño 1+2 simultáneo, ninguna zona pasa FDR (Ilo, r = +0,30, p_fdr = 0,08).

### E5. Lluvia (NASA POWER, Paita–Sechura)

- Niño 1+2 → lluvia: r = +0,40 sin desfase, como se espera.
- Lluvia → clorofila y Kd490: r negativa y sin desfase (−0,32 y −0,39). La lluvia no aumenta la clorofila al mismo tiempo.
- La relación Niño 1+2 → clorofila de Paita a 5 meses sigue igual (r = +0,355) al quitar la parte explicada por la lluvia. La escorrentía de los ríos no explica el hallazgo.
- Las hipótesis que quedan sin probar: recuperación tras el calentamiento (rebote de nutrientes y afloramiento), cambios en el algoritmo de color en aguas turbias y variación en la ventana de observación por nubosidad. Hace falta contrastarlo con otra fuente (clorofila MODIS-Aqua de Giovanni para Paita) antes de presentarlo como hallazgo.

### E6. Segunda fuente para Paita (MODIS-Aqua, Giovanni)

- Las anomalías de MODIS-Aqua y de OC-CCI en Paita se parecen (r = 0,63 en 280 meses).
- Con MODIS-Aqua la relación Niño 1+2 → clorofila de Paita mantiene el signo positivo y crece con el desfase (de +0,06 sin desfase a +0,22 a 8 meses), pero ninguna combinación pasa FDR (p_fdr entre 0,05 y 0,13; n efectivo ≈ 104).
- Con OC-CCI sobre el mismo periodo (2002-07 a 2025-11) el resultado sigue pasando FDR en los desfases de 3 a 8 meses, pero más débil que con la serie completa (r = +0,30 a 5 meses frente a +0,36), y en la primera mitad de ese periodo la correlación casi desaparece (+0,14 a 4 meses).
- Con la serie más corta (23 años) y otra fuente, el rebote no se confirma como significativo.

### Estado

E4 no se confirma con una segunda fuente independiente: la dirección se repite, pero la significancia no. Se presenta como pista, no como hallazgo. Con OC-CCI pasa el criterio; con MODIS-Aqua (NASA), no. Lo honesto es decir que depende del producto y del periodo, lo mismo que se ve en las tendencias.

### E7. Mecanismo físico de El Niño (cadena con mediación)

Script: `enfoque_mecanismo.py`. Panel de conectividad (región peru_humboldt, reanálisis CMEMS, 1998-2025) frente a Niño 1+2 y a la clorofila observada de Chimbote y Callao. 140 pruebas (eslabón A: 70; eslabón B: 80 con y sin control de Niño; capa de mezcla sin datos).

**Eslabón A, Niño 1+2 → variable del mar.** Es el resultado más fuerte hallado hasta ahora; todas pasan FDR, mantienen la dirección sin 1998 y en las dos mitades:

| Variable (región peru_humboldt) | Desfase | r | Lectura |
|---|---|---|---|
| Temperatura superficial | 0 meses | +0,84 | El mar se calienta con El Niño |
| Nivel del mar | 0 | +0,68 | Sube con El Niño |
| Temperatura a 100-200 m | 2 meses | +0,64 | La capa cálida se profundiza y llega con 2 meses de retraso |
| Oxígeno a 100-200 m | 0 | **+0,60** | **Aumenta** a esa profundidad: la capa sin oxígeno se hunde |
| Oxígeno superficial | 1 mes | −0,66 | Disminuye (agua más cálida) |
| Fosfato superficial | 2 meses | −0,54 | Menos nutriente en superficie |
| Clorofila (modelo) | 0 | −0,32 | Cae |
| Nitrato superficial | 0 | −0,20 | Baja, sin pasar FDR |

- Confirma con datos lo que se afirma en el juego y en la web: con El Niño la zona sin oxígeno se hunde. A 100-200 m el oxígeno sube (+0,60), no baja.
- Estos vínculos son conocidos en la literatura; aquí se confirman con las series propias, y el retraso de 2 meses de la temperatura profunda respecto a la superficie es una característica propia de los datos.

**Eslabón B, variable → clorofila de la costa central, con Niño 1+2 controlado.** Solo 2 de 80 pruebas son robustas (oxígeno a 100-200 m en Callao, r = −0,17; temperatura a 100-200 m en Chimbote, r = −0,24; ambas con p_fdr cerca de 0,04-0,05). Sin controlar El Niño hay 29 robustas. Es decir, ninguna de estas variables aporta información sobre la clorofila más allá de El Niño: el mecanismo se describe, pero con estos datos mensuales y regionales no se separa un mediador independiente.

Tablas: `tablas/nuevos_E7_eslabonA_nino_a_variable.csv`, `tablas/nuevos_E7_eslabonB_variable_a_clorofila.csv`.

## 4. Pendiente

- Repetir el análisis de tendencias con MODIS-Aqua (Giovanni) para las demás zonas y con la temperatura de MODIS-Aqua para la Antártida, como tercera fuente independiente.
- Usar OISST (NOAA, 1981-2026, 0,25 grados) como comparación de la temperatura antártica.
- Implementar en la web el panel de tendencias (Mann-Kendall y pendiente de Sen, con la sensibilidad al periodo).
- Pruebas aún sin hacer: predicción en tiempo real de El Niño 2026 y mapa de vulnerabilidad.

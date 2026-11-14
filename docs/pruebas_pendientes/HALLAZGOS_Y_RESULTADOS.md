# Hallazgos y resultados del análisis

Actualizado el 14 de noviembre de 2026. Resumen de todo lo probado con datos satelitales y de reanálisis (clorofila, temperatura, nivel del mar, oxígeno, nutrientes, viento, lluvia, hielo marino, índices climáticos, desembarques y capturas) entre 1998 y 2026. El detalle de cada prueba está en `repos/data-treatment/docs/pruebas_pendientes/SEGUIMIENTO_PRUEBAS.md` (copia de trabajo en `pruebas/fitoplancton/`).

## 1. Mensaje central

1. **El Niño es el factor que explica casi todo lo que cambia en la costa del Perú.** Calienta el mar, profundiza la capa cálida, hunde la zona sin oxígeno, reduce los nutrientes y la clorofila en superficie.
2. **No se encontró una relación robusta entre el océano Austral (Antártida) y el fitoplancton o la anchoveta del Perú.** Más de 1.100 pruebas, con corrección por pruebas múltiples, control de El Niño y comprobación sin 1998 y por mitades del periodo.
3. **No hay tendencias significativas y robustas en la clorofila** de ninguna zona entre 1998 y 2025. El calentamiento antártico que sale significativo en 1998-2025 no resiste una serie más larga ni otro producto.
4. Un resultado "no significativo" también es un resultado: el reto lo dice expresamente.

## 2. Criterio de aceptación (el mismo en todas las pruebas)

- Correlación parcial controlando Niño 1+2.
- n efectivo de Pyper y Peterman (1998) para la autocorrelación.
- FDR (p_fdr < 0,05) por familia de pruebas.
- Misma dirección sin el año 1998 y en las dos mitades del periodo.
- Para tendencias: Mann-Kendall con pendiente de Sen, repetido con otro método, otra estación y otro periodo.

## 3. Resultados robustos

### 3.1 El Niño y la clorofila de la costa

- Niño 1+2 frente a la clorofila: r ≈ −0,47 en Chimbote y Callao.
- En meses con Niño 1+2 ≥ +1 °C la clorofila cae cerca de 45 % en Chimbote y Callao, 20 a 23 % en Pisco e Ilo, y casi nada en Paita–Sechura.
- **Asimetría (descriptiva):** con calor la clorofila baja entre −18 y −30 % por °C (Chimbote −25,8, Callao −26,3, Ilo −30,1, Pisco −18,2; Paita −6,0); con frío el cambio es cercano a cero en Chimbote y Pisco, pero no en Callao e Ilo (−14). **No es un predictor mejor que una relación lineal**: ajustando con 1998-2014 y comprobando en 2015-2025 el modelo asimétrico mejora al lineal entre −1,4 % y +1,6 %. Presentarla como un patrón observado, no como una predicción.
- La costa central (Chimbote, Callao) es la más vulnerable.

### 3.2 Cadena física de El Niño (Niño 1+2 → variable del mar; panel del Perú, reanálisis CMEMS, 1998-2025)

| Variable | Desfase | r |
|---|---|---|
| Temperatura superficial | 0 meses | +0,84 |
| Nivel del mar | 0 | +0,68 |
| Temperatura a 100–200 m | 2 meses | +0,64 |
| Oxígeno a 100–200 m | 0 | +0,60 |
| Oxígeno superficial | 1 mes | −0,66 |
| Fosfato superficial | 2 meses | −0,54 |
| Clorofila (modelo) | 0 | −0,32 |
| Nitrato superficial | 0 | −0,20 (no pasa FDR) |

- A 100–200 m el oxígeno **sube** con El Niño: la capa sin oxígeno se hunde. La temperatura profunda se calienta con 2 meses de retraso respecto a la superficie.
- Son vínculos conocidos en la literatura, confirmados con las series propias. Todos pasan FDR y mantienen la dirección sin 1998 y en las dos mitades.
- Con El Niño controlado, ninguna de estas variables explica la clorofila por separado (2 de 80 pruebas): el mecanismo se describe, pero no se separa un mediador independiente.
- Niño 1+2 → lluvia en Paita–Sechura (NASA POWER): r = +0,40 sin desfase.
- El nivel del mar es otra manera de medir El Niño: no anticipa la clorofila (la relación es más fuerte sin desfase, y desaparece al controlar Niño 1+2).

## 4. Tendencias (lo que pide el reto)

Promedios anuales, Mann-Kendall y pendiente de Sen. Cálculo mensual con n efectivo como comprobación.

| Serie | Periodo | Tendencia por década | p |
|---|---|---|---|
| Clorofila, cinco zonas peruanas (OC-CCI, ESA) | 1998-2025 | entre −0,17 y +0,15 mg/m³ | 0,13 a 0,80: ninguna significativa |
| Clorofila, Rey Jorge | 1998-2025 | +0,04 | 0,072 |
| Clorofila, Chimbote, OC-CCI | 2003-2025 | −0,31 | 0,033 |
| Clorofila, Chimbote, MODIS-Aqua (NASA) | 2003-2025 | −0,14 | 0,68 |
| Temperatura, Rey Jorge, CRW | 1998-2025 | +0,18 °C | 0,002 |
| Temperatura, Rey Jorge, CRW | 1986-2025 | +0,02 °C | 0,64 |
| Temperatura, Península Antártica, CRW | 1998-2025 | +0,16 °C | 0,030 |
| Temperatura, Península Antártica, CRW | 1986-2025 | −0,01 °C | 0,76 |
| Temperatura, Rey Jorge, ERSST (2°) | 1986-2025 | −0,08 °C | 0,02 (signo contrario) |

- Un resultado que cambia de signo o de significancia al mover el año de inicio o el producto **no es robusto**. Es el mensaje metodológico principal.
- Los extremos (meses con clorofila muy baja o con mar cálido) y la fenología (amplitud, valor y mes del pico) tampoco muestran tendencias significativas.
- La prueba estacional de Hirsch sobre series mensuales da p muy bajos porque no corrige la autocorrelación mensual; no usarla como evidencia.

## 5. Pistas sin confirmar

- **Rebote tardío en Paita–Sechura:** la clorofila sube entre 2 y 8 meses después de un calentamiento de Niño 1+2 (máximo a 5 meses, r = +0,36 con OC-CCI). No depende de 1998 ni de la lluvia. Con MODIS-Aqua (NASA, Giovanni) mantiene el signo, pero no es significativa (r = +0,16 a +0,22, p_fdr 0,05 a 0,13). Presentar solo como pista.
- Hielo marino frente al jurel de Chile (r ≈ −0,55), clorofila de Rey Jorge frente al calamar argentino del año siguiente (r = +0,60), SAM frente a clorofila de Rey Jorge (r = +0,50): no resisten FDR con n efectivo bajo.

## 6. Lo que no se encontró

- Fitoplancton antártico → fitoplancton peruano (50 desfases, 0 con FDR).
- Ambiente austral (hielo, SAM, temperatura, corrientes) → clorofila y carbono peruanos (180 pruebas, 0).
- Antártida y Pacífico Sur en superficie y profundidad, altimetría, reglas de asociación, cadena con puente (240 pruebas), corrientes (208), El Niño → Antártida (104), SAM × Niño (6): ninguna robusta. La pista de 3 a 4 años de desfase era el ciclo de El Niño.
- Clorofila → desembarques mensuales (100 pruebas), viento ERA5 → clorofila (40): ninguna robusta.
- Fitoplancton → anchoveta y El Niño → anchoveta: dependen del crucero de 1998 (9 a 12 cruceros usables).
- Kd490 → clorofila es una relación mecánica (r = 0,99), no un resultado.

## 7. Fuentes de datos (citar todas)

- Clorofila: OC-CCI v6 (ESA); **MODIS-Aqua L3m CHL v2022.0 (NASA, vía Giovanni)** para Chimbote y Paita, 2002-2025.
- Temperatura: Coral Reef Watch v3.1 (NOAA), 1986-2025; ERSST v5 (NOAA PSL), 1854-2026.
- Reanálisis y modelos: CMEMS (nivel del mar, oxígeno, nitrato, fosfato, corrientes); ERA5 (viento).
- **NASA POWER** (lluvia, temperatura del aire, radiación).
- Hielo marino: NSIDC G02135. Índices: Niño 1+2, ONI y SAM de NOAA PSL.
- Pesca: BCRP (desembarques mensuales 2003-2026), IMARPE (biomasa por crucero), FAO GlobalProduction 2026.1, anuarios de PRODUCE, GBIF.
- Métodos citados: Pyper y Peterman (1998); Benjamini y Hochberg (FDR); Mann-Kendall y Theil-Sen; Hirsch et al. (estacional). Recursos del reto: Giovanni, artículo de series de tiempo con clorofila SeaWiFS, y los dos artículos sobre pruebas de tendencia y significancia.

## 8. Correspondencia con el reto "Be an Earth System Trend Detective!"

| Elemento del reto | Cómo se cubre |
|---|---|
| Identificar variables | Clorofila, temperatura superficial y, en el explorador, salinidad, nutrientes, oxígeno, viento, hielo, índices climáticos |
| Datos de una región | 5 zonas del Perú y 2 de la Antártida; el usuario elige |
| Serie de tiempo visualizada | Panel de tendencias y monitor mensual |
| Tasa de cambio y prueba de significancia | Panel de tendencias: Mann-Kendall y pendiente de Sen, veredicto de significancia y sensibilidad al año de inicio |
| Definiciones sencillas, ejemplos guiados | Definición de cada variable y tres ejemplos en el panel |
| Datos NASA | MODIS-Aqua (Giovanni) y NASA POWER, además de ESA y NOAA |

## 9. Archivos

- Registro completo: `SEGUIMIENTO_PRUEBAS.md`; hipótesis: `PRUEBAS_POSIBLES.md`; resultados: `RESULTADOS_PRUEBAS_PENDIENTES.md` (todo en `docs/pruebas_pendientes/` del repositorio de análisis).
- Scripts y tablas: `docs/pruebas_pendientes/*.py` y `data/tablas_pruebas_pendientes/*.csv`.
- Series de Giovanni: `data/giovanni/`.

# Contexto del trabajo de análisis (13 y 14 de noviembre de 2026)

Qué se hizo, con qué datos y qué resultó. Es la entrada para quien retome el análisis. El detalle de cada prueba está en `SEGUIMIENTO_PRUEBAS.md`; las cifras ordenadas para la web, en `HALLAZGOS_Y_RESULTADOS.md` (carpeta de guías del proyecto).

## 1. Punto de partida

La pregunta del proyecto es cómo se asocian los cambios del fitoplancton antártico con la vida marina del Perú. El reto elegido es "Be an Earth System Trend Detective!", que pide una herramienta para elegir variables, visualizar su serie de tiempo en una región y probar si el cambio es estadísticamente significativo. Una tendencia no significativa es un resultado válido.

Antes de estas jornadas ya se había probado que la Antártida no se relaciona con el fitoplancton ni con la anchoveta del Perú (más de 900 pruebas), que El Niño 1+2 explica la clorofila de la costa y que no hay tendencias significativas en 1998-2025.

## 2. Qué se hizo

1. **Lista de pruebas posibles** con criterio de aceptación y viabilidad (`PRUEBAS_POSIBLES.md`).
2. **Primera tanda** (A1, A3, A4, B1): clorofila frente a desembarques mensuales, viento ERA5, asimetría como predicción, El Niño frente a la Antártida (`pruebas_pendientes.py`).
3. **Segunda tanda** (A2, A5, B2 a B5): nivel del mar, Kd490 y oxígeno, SAM × El Niño, cadena con puente en el Pacífico Sur, corrientes y otras especies de la FAO (`pruebas_pendientes_2.py`).
4. **Tendencias** con Mann-Kendall anual y estacional, pendiente de Sen, regresión mensual con n efectivo y sensibilidad al año de inicio, con series largas de temperatura (CRW 1986-2025 y ERSST v5 1950-2025) y clorofila MODIS-Aqua de NASA (`tendencias.py`).
5. **Enfoques nuevos**: eventos extremos y fenología (`enfoques_nuevos.py`), capacidad de adelanto de El Niño (`enfoque_adelanto.py`), lluvia en Paita (`enfoque_lluvia_paita.py`), contraste de Paita con MODIS-Aqua (`enfoque_paita_modis.py`), mecanismo físico (`enfoque_mecanismo.py`).
6. **Capacidad predictiva** con origen móvil y comprobación con 2026 (`prediccion_validacion.py`).
7. **Tendencia por celda** con los mapas de la web y tres años de inicio (`mapa_tendencias.py`).

## 3. Datos usados y descargados

- Descargados de Giovanni (NASA, MODIS-Aqua L3m CHL v2022.0, mensual, 4 km, 2002-07 a 2025-11): Chimbote y Paita (`data/giovanni/`). El periodo completo tarda unos 4 minutos por zona.
- ERSST v5 (NOAA PSL), 162 MB, fuera del repositorio.
- Locales: monitor mensual 1998-2026 (clorofila OC-CCI, temperatura CRW, índices), panel de conectividad (reanálisis CMEMS, 1998-2025), NASA POWER, ERA5, BCRP, FAO.
- No se usó la descarga año por año de CMEMS: el panel de conectividad ya traía nivel del mar, nitrato, oxígeno y corrientes hasta 2025.

## 4. Resultados

Criterio de aceptación: correlación parcial con Niño 1+2, n efectivo (Pyper y Peterman), FDR, misma dirección sin 1998 y en las dos mitades del periodo. Para tendencias: Mann-Kendall con Sen, repetido con otro método, estación y periodo.

### 4.1 Lo que resiste

- **Cadena física de El Niño** (Niño 1+2 → variable del mar, panel del Perú): temperatura superficial r = +0,84; nivel del mar +0,68; temperatura a 100–200 m +0,64 con 2 meses de retraso; oxígeno a 100–200 m +0,60 (sube: la capa sin oxígeno se hunde); oxígeno superficial −0,66; fosfato superficial −0,54; clorofila (modelo) −0,32. Son vínculos conocidos, confirmados con las series propias. Con El Niño controlado ninguna de estas variables explica la clorofila por separado.
- **Niño 1+2 → lluvia en Paita:** r = +0,40.
- **Capacidad predictiva** (anomalía mensual de clorofila, origen móvil 2010-2025): mejora de +5 % a +17 % sobre no usar modelo a 1 mes, y casi nada a 3 meses; supera siempre a la persistencia (+9 % a +31 %). Con 2026 (7 meses): sigue bien la observada en Callao (r = 0,84), Chimbote (0,77), Pisco (0,91) y Paita (0,64); falla en Ilo (observada −45 %, predicha −8 %). No es un pronóstico de El Niño.

### 4.2 Lo que no resiste

- Más de 1.100 pruebas en total sin relación robusta entre la Antártida y el Perú; la relación entre clorofila y desembarques mensuales, el viento y El Niño frente a la Antártida tampoco pasan la corrección.
- El nivel del mar solo se relaciona con la clorofila si no se controla El Niño: es otra medida de El Niño, no un indicador adelantado.
- Kd490 frente a clorofila (r = 0,99) es una relación mecánica.
- La asimetría térmica (calor baja la clorofila entre −18 y −30 % por °C, frío casi no la modifica) describe los datos, pero no predice mejor que una relación lineal.

### 4.3 Tendencias

- Clorofila de las cinco zonas peruanas (OC-CCI, 1998-2025): ninguna tendencia significativa con promedios anuales (p entre 0,13 y 0,80).
- Temperatura de Rey Jorge y de la Península Antártica: significativa de 1998 a 2025 (+0,18 y +0,16 °C por década; p = 0,002 y 0,030), pero con 40 años (1986-2025) desaparece (+0,02 y −0,01; p = 0,64 y 0,76), y con ERSST sobre el mismo periodo la pendiente cambia de signo. **No es robusto.**
- Chimbote depende del producto y del periodo: OC-CCI 2003-2025 da caída significativa (p = 0,033), MODIS-Aqua 2003-2025 no (p = 0,68).
- Eventos extremos y fenología de la clorofila: sin tendencia.
- **Tendencia por celda** (mapas de la web, Mann-Kendall con FDR entre celdas, 1998-2025): en clorofila, 32 % de las celdas significativas desde 1998 (1.781 suben y 108 bajan), 8 % desde 2003 y casi ninguna desde 2012. En temperatura, 2 % desde 1998 (38 de 39 suben) y ninguna desde 2012. Es decir, cuanto más reciente el inicio, menos tendencia; el aumento de clorofila desde 1998 depende en buena medida de que el primer año de la serie es el más bajo. Las celdas vecinas no son independientes, de modo que la corrección FDR es optimista.

### 4.4 Pistas sin confirmar

- **Rebote tardío en Paita–Sechura:** la clorofila sube entre 2 y 8 meses después de un calentamiento de Niño 1+2 (máximo a 5 meses, r = +0,36 con OC-CCI). No depende de 1998 ni de la lluvia. Con MODIS-Aqua mantiene el signo pero no pasa la corrección (r = +0,16 a +0,22; p_fdr de 0,05 a 0,13).

## 5. Mensaje para la presentación

1. El Niño explica casi todo lo que se ve en la costa: calienta el mar, profundiza la capa cálida, hunde la zona sin oxígeno y reduce nutrientes y clorofila.
2. No se encontró un vínculo robusto entre la Antártida y el Perú.
3. Un resultado que cambia al mover el año de inicio o el producto de datos no es una tendencia robusta: es el mensaje metodológico de la herramienta de tendencias.

## 6. Trabajo de la web asociado

- En `main` del repositorio de la web: panel de tendencias (Mann-Kendall, pendiente de Sen y sensibilidad al año de inicio).
- Rama `prediccion-validacion` de la web: sección de capacidad predictiva (pendiente de integrar).
- Pendiente: mapa de tendencia por celda; ampliaciones del panel (intervalo de confianza, modo de preguntas, glosario, comparación de fuentes), cadena física de El Niño, actualización de los textos de hallazgos y de fuentes (indicadas en `PROMPT_CODEX_WEB.md`).

## 7. Pendiente de análisis

- Giovanni de Callao, Pisco, Ilo, Rey Jorge y la Península, para comprobar tendencias con una fuente NASA en todas las zonas.
- Temperatura de MODIS-Aqua y OISST (NOAA, 1981-2026) como comparaciones de la temperatura antártica.
- Predicción de El Niño 2026 hacia adelante y mapa de vulnerabilidad por zona.

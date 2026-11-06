# Articulación de fuentes de datos hacia un público (Space Apps 2026)

Estado: borrador del 11 de octubre de 2026. Todo lo marcado **(de memoria)** no está verificado. Confirmar con el enunciado oficial de "Bailando con los SAR" (sale el 28 de octubre).

## 1. La idea en una línea

Cruzar **lluvia** (NASA POWER) con **respuesta del radar** (NISAR GCOV) y **vigor de la vegetación** (NDVI/EVI) para decirle a alguien concreto **cómo está cambiando el estado de su zona** y qué decisión puede tomar con eso. Es monitoreo, no pronóstico.

La parte técnica se resuelve con los granules. Lo que falta es responder: **¿para quién, y qué decide esa persona con lo que ve?**

## 2. Qué aporta cada fuente (y qué no)

| Fuente | Qué mide | Qué puedes decirle al público | Qué NO puedes decir |
|---|---|---|---|
| NASA POWER | Lluvia diaria por punto, grilla gruesa | "Esta zona recibió más o menos lluvia que de costumbre" | Cuánto llovió en una chacra concreta |
| NISAR GCOV | Retrodispersión del radar (humedad + estructura + rugosidad) | "La señal indica más o menos agua en superficie que en la fecha anterior" | Humedad del suelo exacta; diagnóstico de una parcela |
| NDVI/EVI (MODIS/VIIRS) **(de memoria)** | Vigor y verdor de la vegetación, 250 m a 1 km | "La vegetación de la zona está respondiendo o no" | Rendimiento o pérdida de cosecha |
| DSWx-S1 / INDECI | Agua superficial detectada; reportes de emergencia | Contexto: "aquí hubo desborde reportado" | Causa del desborde |

Regla para comparar fechas NISAR: misma pista, mismo cuadro, misma polarización.

## 3. Cadena de articulación

```
Pregunta del usuario
   -> Decisión que puede tomar
      -> Señal que la informa (lluvia, radar, verdor)
         -> Salida simple (estado por zona + incertidumbre)
            -> Validación con una persona real
```

Si una fuente no cambia la decisión de nadie, sobra en el producto.

## 4. Candidatos a objetivo X

Elegir **uno**. Los públicos son hipótesis, no hechos.

### A. Exceso de agua en zona ribereña (Ucayali)
- **Pregunta:** ¿dónde se acumula agua después de lluvias fuertes?
- **Público posible:** gobierno local o defensa civil, comunidades ribereñas **(hipótesis)**.
- **Decisión:** priorizar alerta, vigilancia o ayuda.
- **Señal:** lluvia acumulada + cambio de retrodispersión (L-band ve agua bajo vegetación) + DSWx-S1 de contexto.
- **Ventaja:** Pucallpa tuvo 57 días de lluvia (327,8 mm) en el periodo analizado, hay señal que mirar.
- **Riesgo:** pocas fechas por pista y cuadro (umbral que fijaste: 8). Sin eventos de inundación confirmados en el periodo NISAR, la validación es débil.

### B. Condición de cultivos por zona (Tumbes/Piura o Ucayali)
- **Pregunta:** ¿cómo está respondiendo la vegetación a la lluvia reciente?
- **Público posible:** técnicos agrarios, cooperativas, juntas de regantes **(hipótesis)**.
- **Decisión:** dónde enviar asistencia técnica o qué zonas revisar primero.
- **Señal:** lluvia + radar + NDVI/EVI (EVI en selva densa, porque NDVI se satura).
- **Riesgo:** parcelas pequeñas contra píxeles grandes. Sirve para zonas, no para agricultores individuales. No hay datos de cosecha para validar.

### C. Déficit de lluvia en el altiplano (Titicaca)
- **Pregunta:** ¿qué zonas llevan menos lluvia y respuesta de humedad de lo esperable?
- **Público posible:** técnicos agrarios regionales **(hipótesis)**.
- **Señal:** lluvia + radar (polarización SHSH disponible) + nivel del lago (G-REALM/DAHITI/Hydroweb) como contexto.
- **Riesgo:** no hay producto fiable de heladas; en Puno llovió poco en el periodo (53,4 mm), así que la señal puede ser débil.

Mi recomendación provisional: **A** si quedan 8 o más fechas comparables en Ucayali; **B** como capa extra o plan alternativo.

## 5. Parte del público: qué validar antes del hackatón

Objetivo: una o dos conversaciones cortas (15 a 20 minutos) con alguien del público elegido. Fuentes de contacto posibles **(de memoria, verificar)**: agencias agrarias regionales, municipalidades, ONGs de la zona, universidades locales, docentes.

Preguntas útiles:
1. ¿Qué decisión toma hoy cuando llueve mucho o poco? ¿Con qué información?
2. ¿Qué fuentes usa ya (SENAMHI, reportes, WhatsApp, observación directa)?
3. ¿Qué le haría confiar o desconfiar de una herramienta así?
4. ¿Con qué frecuencia necesita la información? (NISAR repite cada 12 días.)
5. ¿En qué formato la usaría: mapa, mensaje, informe corto?

Qué hacer con las respuestas: si la persona no puede nombrar una decisión que cambie, el objetivo X está mal elegido.

## 6. Salida pensada para ese público

- Un mapa por zona con un estado simple: **más húmedo / normal / más seco** que lo habitual, con su incertidumbre visible.
- Una frase en lenguaje llano por zona (sin "retrodispersión", sin "dB").
- Fecha del dato y qué fuente lo respalda.
- Aviso explícito: "indicador de monitoreo, no pronóstico ni diagnóstico".

## 7. Qué no prometer

- Pronóstico de inundaciones o de cosechas.
- Humedad del suelo exacta (SME2 no está del todo calibrado).
- Información por parcela o por agricultor.
- Conclusiones de causalidad con unas pocas fechas: presentar como exploración.

## 8. Plan

| Cuándo | Qué |
|---|---|
| Hasta el 28 de octubre | Contar fechas comparables por pista/cuadro/polarización; abrir un granule con `h5py`; serie en dB sobre una ventana pequeña; 1 conversación con alguien del público |
| 28 de octubre | Leer el enunciado completo: ¿exige NISAR?, ¿qué se puede preparar antes?, criterios de evaluación |
| 14 y 15 de noviembre | Cruce final, salida simple, demo con datos reales, presentación centrada en el público y la decisión |

## 9. Decisiones pendientes

- [ ] Elegir objetivo X (A, B o C).
- [ ] Elegir el público concreto y una persona con quien validar.
- [ ] Confirmar con el enunciado oficial el alcance y las reglas de preparación previa.
- [ ] Verificar los nombres y datos marcados **(de memoria)**.
- [ ] Decidir qué capa de contexto se añade (NDVI/EVI o DSWx-S1), una sola.

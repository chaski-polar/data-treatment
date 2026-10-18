# Hallazgos: ruta B (clorofila/fitoplancton) · NASA Space Apps 2026

Fecha de corte: 17 de octubre de 2026. Hackatón: 14-15 de noviembre. Los enunciados completos con datasets salen el 28 de octubre.
"(de memoria)" = no verificado. "(hipótesis)" = inferencia mía, sin comprobar.

---

## 1. Resumen ejecutivo

- La hipótesis inicial (la clorofila de las bahías de cultivo peruanas cambió de forma detectable entre 2003 y 2022) **no tiene soporte en los datos**: Sechura, Samanco, Paracas, Pisco y las bahías del norte salen sin tendencia significativa.
- Hay una **señal sugerente, no confirmada**, en la costa sur-central (San Juan de Marcona, Chala, Ico/Atico: la clorofila baja) y posible aumento en el extremo sur (Ilo, Tacna). **No sobrevive a la corrección por probar 22 sitios.**
- La idea "mapa de tendencias de clorofila" ya está cubierta por servicios públicos; solo tiene espacio si se enfoca en una pregunta local o una decisión concreta.
- Los datos y el método funcionan (cobertura ≥ 90 % sobre agua en casi todas las cajas). Falta definir un público objetivo con una decisión real.

---

## 2. ¿Ya existe un servicio público?

Sí, para el producto genérico:

- **Copernicus Marine (UE):** mapa global de tendencia de clorofila-a a 4 km desde 1997, con descomposición estacional + tendencia + residuo y solo tendencias con p < 0,05.
- **NOAA CoastWatch:** producto diario de anomalía de clorofila VIIRS a 4 km.
- **IMARPE (Perú):** monitorea clorofila con MODIS (4 km, diario) y anomalías de temperatura superficial; su página en UN-SPIDER lo vincula con la amenaza de floraciones algales nocivas.
- NASA Giovanni y Worldview permiten series y mapas de clorofila sin programar (de memoria).

**Consecuencia:** presentar solo un mapa de tendencias con prueba de significancia sería reimplementar algo existente.

---

## 3. Target posible

**Productores de concha de abanico (maricultura) y gestores de bahías** (Sechura y similares).

- Un resumen de política del ZMT (Leibniz) sobre mareas rojas en Perú recoge impactos en Sechura: pérdida de producción por falta de oxígeno, cierres, menos ingresos, deudas y pérdida de empleo.
- Estrategias discutidas por productores: cambiar fechas de cosecha, cultivos suspendidos y monitoreo transparente; se quejaron de la comunicación insuficiente del monitoreo.
- IMARPE y SANIPES ya vigilan fitoplancton potencialmente tóxico en sitios de acuicultura. Tu herramienta complementaría, no reemplazaría.
- Una tesis chilena encontró relación positiva entre veneno paralizante, clorofila y coeficiente de atenuación en datos MODIS, pero con datos de otro país/método y usando promedios de 8 días por las nubes.

**Límites a declarar:** clorofila alta no equivale a marea roja tóxica; no es sistema de alerta; el píxel de 4 km puede ser grueso para bahías pequeñas.

**Otros targets (más débiles):** gestores públicos (lejanos, difíciles de validar); investigadores/campañas antárticas (pequeño y probablemente cubierto por productos europeos).

**Pendiente central:** definir una decisión concreta, en una frase: *"[Quién] decide [qué] y mi herramienta le muestra [qué variable], para que [cambie qué]"*. No tiene nada que ver con conectar un LLM; es un ejercicio de definición de usuario. Validar con 2-3 conversaciones (productores, SANIPES, IMARPE).

---

## 4. Datos y acceso

- El dataset `erdMH1chlamday_R2022SQ` ("Chlorophyll-a, Aqua MODIS, NPP, L3SMI, Global, 4km, R2022 SQ, 2003-present, mensual") existe en `coastwatch.pfeg.noaa.gov`. En `coastwatch.noaa.gov/erddap` solo vi IDs de otro tipo (`noaacw…`) (hipótesis: otro ERDDAP que no aloja los `erdMH1…`).
- **Fuente que sí funcionó:** `https://oceanwatch.pifsc.noaa.gov/erddap/griddap/aqua_chla_monthly_2018_0`, variable `chlor_a`, 238 pasos de tiempo, malla 4320 × 8640, cubre 2003-2022 (producto R2018, no el reprocesado más reciente).
- Hay que confirmar el 28 de octubre si un dataset alojado por NOAA cuenta como "dato NASA" (los datos originales son MODIS-Aqua, NASA/GSFC OBPG).
- Mi entorno no tiene red hacia esos servidores: todos los análisis reales los corriste tú.

---

## 5. Resultados en las bahías de cultivo (MODIS-Aqua mensual 2003-2022)

Cobertura medida solo sobre píxeles de agua; control de calidad: un mes entra si ≥ 25 % de píxeles tienen dato.

| Bahía | Píxeles de agua | Cobertura | Tendencia (%/año) | p ajustado | Píxeles significativos (FDR) |
|---|---|---|---|---|---|
| Sechura | 112 | 96 % | -0,40 [-1,49, +0,69] | 0,554 | 0 |
| Samanco | 77 | 92 % | -0,22 [-1,55, +1,15] | 0,802 | 0 |
| Paracas | 63 | 94 % | -0,52 [-1,37, +0,40] | 0,422 | 0 |

- Primera versión (v1): sin tendencia en las tres (p = 0,28 a 0,81). v2 (máscara de agua, p ajustado por autocorrelación lag-1, extremos, mapa por píxel con FDR) lo confirma.
- Un mes "extremo" (anomalía > 1 SD) equivale a ~1,5-1,7 veces la clorofila normal de ese mes (Sechura +0,197 log10; Samanco +0,238; Paracas +0,173).
- Con 19-20 observaciones por mes calendario, las diferencias entre meses en el "calendario de riesgo" caben dentro del ruido de muestreo (~±8 puntos): no es interpretable.
- Los intervalos descartan cambios grandes (Sechura: unos 20 años a -1,5 %/año serían ~-25 %), pero no cambios moderados.

---

## 6. Barrido de 22 cajas a lo largo de la costa

Cobertura ≥ 87 % en casi todas, salvo Callao/Lima (55 %), Lurín/Chilca (50 %), Supe/Huacho (79 %) e Ico/Atico (72 %).

### Cajas con p ajustado < 0,05 en la tendencia media

| Zona | Tendencia (%/año) | p ajustado | Cambio acumulado aprox. en 19,3 años |
|---|---|---|---|
| Chala | -2,56 | 0,004 | -39 % |
| Ico/Atico | -2,20 | 0,010 | -35 % |
| San Juan de Marcona | -1,20 | 0,032 | -21 % |
| Pimentel | +1,02 | 0,041 | +22 % |

Casi significativas: Ilo (+1,60; p = 0,073), Yarada/Tacna (+1,63; p = 0,081), Callao/Lima (-1,76; p = 0,082). El resto, sin cambio (p = 0,14 a 0,90).

### Por qué no se puede afirmar todavía

1. **Pruebas múltiples:** con Benjamini-Hochberg sobre los 22 sitios, ninguno pasa (Chala necesita p < 0,0023 y tiene 0,004; Ico necesita < 0,0045 y tiene 0,0096). Con Bonferroni (umbral 0,0023) tampoco. Aun así, obtener ≥ 4 resultados con p < 0,05 entre 22 por azar puro ocurre solo ~2 % de las veces.
2. **Cajas diminutas:** 7-9 píxeles de agua en las del sur; los píxeles vecinos no son independientes, así que "7 de 9 significativos" cuenta como una sola región.
3. **Los extremos no son evidencia aparte:** si baja la anomalía media, baja mecánicamente la frecuencia de meses > +1 SD. Además la serie anual es discreta con muchos empates (intervalos burdos, límites en "-0,00").
4. **Pacasmayo (extremos, p = 0,034):** probablemente azar; su tendencia media no es significativa.
5. **Costa pegada:** a 4 km de la costa pueden mezclarse agua turbia, bordes de tierra y correcciones atmosféricas; posible artefacto o deriva del sensor en el producto R2018 (de memoria).
6. **Ilo y Tacna:** el p ingenuo es significativo (0,016) pero el ajustado no (0,07-0,08).

### Sitios poco fiables

- **Callao/Lima y Lurín/Chilca:** faltan datos justo en invierno (septiembre: 3 y 4 meses con dato en 19 años; de memoria, nubosidad costera). Sus tendencias, y los 5 píxeles "que bajan" en Callao, no son fiables.
- **Chancay:** 0 píxeles de agua (la caja cae en tierra); corregir coordenadas.

### Patrón geográfico

Norte (Tumbes-Chimbote): sin cambio claro; sur-central (Marcona-Chala-Ico/Atico): baja; extremo sur (Ilo, Tacna): sube sin llegar a significativo. Sería una historia de tendencias opuestas, que es lo que el desafío B menciona, pero hay que confirmarla.

---

## 7. Controles para volverlo defendible

1. **Cajas mar adentro** (50-150 km) a la altura de Marcona-Chala-Ico: si también bajan, es cambio regional; si solo baja la franja costera, sospechar artefacto.
2. **Sensibilidad:** repetir sin 2015-2017 (El Niño costero) y con distintos años de inicio.
3. **Otra versión o sensor:** `erdMH1chlamday_R2022SQ` (reprocesado) y, si es posible, VIIRS (NASA).
4. **Extender a 2023-2026** (producto NRT o `earthaccess` con `MODISA_L3m_CHL`).
5. **Corrección global:** barrido por píxel de toda la franja con FDR sobre el dominio completo; existe un método específico para significancia de campos espaciales (de memoria, atribuido a Wilks).
6. **Declarar** que las cajas fueron elegidas por ti y el análisis se profundizó donde salió algo: es exploración, no prueba.

Otras vías si la tendencia no se sostiene: correlacionar la anomalía de clorofila con anomalía de temperatura superficial (SST NASA) para explicar variabilidad; o pivotar a la ruta A.

---

## 8. Ruta A (NISAR) · estado

Sin cambios respecto al contexto inicial: monitor de respuesta del terreno (NISAR GCOV + lluvia NASA POWER + NDVI/EVI) en Tumbes/Piura, Titicaca o Ucayali. Umbral fijado: al menos 8 fechas comparables (misma pista, cuadro y polarización); ningún granule NISAR (~1,4 GB cada uno) descargado ni abierto todavía. Mi lectura (sin verificar con búsqueda): menor riesgo de "ya existe", mayor riesgo técnico.

---

## 9. Decisión sugerida

Quedan ~11 días hasta el 28 de octubre y ~4 semanas hasta el hackatón.

- **Seguir con B** solo si los controles mantienen la señal del sur-central.
- **Pasar a A** si se desvanece (lo aprendido en datos NASA, pruebas estadísticas e incertidumbre es transferible).
- **En paralelo:** definir el usuario con 2-3 conversaciones. No cambiar de target hasta que la señal pase los controles.
- No conozco los criterios del jurado; los enunciados del 28 de octubre aclararán si un resultado en gran parte nulo puntúa bien.

---

## 10. Archivos generados en la conversación

- `revisar_modisa_bahias.py` (v1): cobertura y tendencia por caja.
- `revisar_modisa_bahias_v2.py`: máscara de agua, p ajustado por autocorrelación, extremos, calendario, mapa por píxel con FDR; salidas `modisa_v2_<sitio>.png` y `modisa_v2_resumen.csv`. Probado solo con datos sintéticos.
- Propuesta pendiente: v3 con cajas mar adentro, sin 2015-2017, comparación entre versiones del producto y corrección global entre sitios.

---

## 11. Fuentes consultadas (paráfrasis, no citas)

- Copernicus Marine, indicador de tendencia de clorofila: https://data.marine.copernicus.eu/product/OMI_HEALTH_CHL_GLOBAL_OCEANCOLOUR_trend/description
- NOAA CoastWatch, anomalía de clorofila VIIRS: https://coastwatch.noaa.gov/erddap/info/noaacwNPPVIIRSchlanomdifDaily/index.html
- IMARPE, clorofila (UN-SPIDER): https://un-spider.org/es/enlaces-y-recursos/fuentes-de-datos/clorofila-instituto-del-mar-del-peru-imarpe
- ZMT, resumen de política sobre floraciones algales nocivas en Perú: https://www.leibniz-zmt.de/images/content/pdf/Policy_Briefs/2025_01_Policy_Brief_HABs_in_Peru_ZMT_Spanish.pdf
- Tesis chilena sobre veneno paralizante y datos MODIS: https://repositorio.usm.cl/handle/123456789/77236
- Fitoplancton potencialmente tóxico en sitios de acuicultura peruanos: https://repositorio.upch.edu.pe/entities/publication/db9b0206-11bf-4cc2-98fe-9416527e4a32/full
- ERDDAP, dataset `erdMH1chlamday_R2022SQ`: https://coastwatch.pfeg.noaa.gov/erddap/griddap/erdMH1chlamday_R2022SQ.graph

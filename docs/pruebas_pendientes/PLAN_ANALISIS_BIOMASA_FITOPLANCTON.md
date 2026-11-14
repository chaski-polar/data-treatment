# Plan: biomasa fitoplanctónica Antártida–Humboldt

Fecha: 14 de noviembre de 2026. Estado: implementado y ejecutado localmente.

Comando desde `data_treatment`:

```bash
uv run python scripts/18_test_phytoplankton_carbon_connectivity.py
```

Primera corrida: 12 contrastes estimables con 312 meses cada uno (2000–2025),
ninguno significativo con FDR; p FDR mínimo = 0,186487. No se obtuvo evidencia
suficiente para rechazar H0 bajo esta especificación. Tres p-valores originales
son menores de 0,05, pero no sobreviven a la corrección de la familia.
Las cuatro pruebas automatizadas pasaron, incluida la equivalencia numérica
de la covarianza HAC con statsmodels en series sin huecos y una referencia
independiente con distancias calendario en series con huecos.

Implementación: también se incluyen efectos fijos de mes calendario como
controles. La climatología se recalcula dentro de cada muestra alineada.

## Antecedentes verificados

- `SEGUIMIENTO_PRUEBAS.md`, H1e, registra 180 pruebas de ambiente austral frente a clorofila y carbono peruano, con cero resultados robustos. En esta copia no se encontró el script ni la tabla de resultados de H1e; no se puede recuperar su p-valor específico ni afirmar que contrastó `phyc` antártico frente a `phyc` peruano.
- `scripts/14_fit_experiment_b_monitor.py` y `data/processed/models/experiment_b_monitor.json` contienen B2, que incorpora carbono fitoplanctónico. Su respuesta es biomasa interpolada de anchoveta y su evaluación es predictiva, no un contraste Antártida–Humboldt.
- `analysis_r/04_exploratory_models.R` prepara `phyc_z`, pero las fórmulas principales A/B/C utilizan `chl_z`; definir una columna no equivale a probarla.
- Se revisaron 52 CSV no vacíos de resultados en `data/tablas_pruebas_pendientes/` y `analysis_r/data/`. Las referencias a carbono encontradas corresponden a columnas de paneles de entrada, no a resultados de un contraste explícito entre regiones.

## Pregunta e hipótesis

¿La concentración de carbono fitoplanctónico antártica presenta asociación con la de Humboldt peruano, simultánea o con retraso, una vez controlados ENSO, estacionalidad y tendencia?

Para cada región y rezago:

- H0: el coeficiente asociado a la biomasa fitoplanctónica antártica es cero, condicionado a los controles.
- H1: ese coeficiente es distinto de cero (contraste bilateral).

Esto evalúa asociación entre concentraciones modeladas; no transporte de organismos, causalidad ni respuesta de anchoveta.

## Script propuesto

Ruta: `scripts/18_test_phytoplankton_carbon_connectivity.py`.

Entradas locales, mediante argumentos CLI:

- `--panel`: `data/processed/tables/connectivity_panel_monthly.csv`.
- `--nino12`: `data/nino12.long.anom.csv`, normalizando el encabezado y el marcador -99.99.
- `--output`: `data/processed/analysis/phytoplankton_carbon_connectivity/`.
- Periodo principal 1998–2025; semilla y configuración registradas.

No necesita NetCDF originales, credenciales ni Colab para el contraste mensual regional.

## Diseño principal, fijado antes de ajustar

1. Respuesta: `phyc` de `peru_humboldt`, banda `surface_0_5m`.
2. Predictores: `phyc` de `peninsula_antarctica` y `bellingshausen`, analizados por separado.
3. Rezagos: 0, 3, 6, 12, 18 y 24 meses. Un rezago positivo significa que la Antártida precede a Perú.
4. Familia principal: 12 contrastes (dos regiones por seis rezagos), conservando todos los resultados.
5. Usar `phyc` del producto CMEMS, no el carbono calculado con una razón clorofila:carbono constante. Conservar mmol C/m³ y añadir mg C/m³ como unidad de presentación.
6. Reindexar por meses calendario; comprobar unicidad región/fecha/banda, cobertura, finitud, variación y valores físicamente inválidos. No interpolar faltantes ni unir los meses separados como si fueran contiguos.
7. Calcular anomalías por mes calendario y estandarizarlas con referencia documentada. Registrar que la agregación original es mediana espacial del promedio de niveles de profundidad; no es biomasa integrada por área o columna de agua.
8. Construir primero los rezagos sobre el calendario completo. Usar una ventana común para comparar los 12 contrastes, descontando los primeros 24 meses. Documentar las exclusiones adicionales.

## Estadística

Modelo por región r y rezago k:

`phyc_Peru_anom(t) = intercepto + beta * phyc_Antartida_anom(t-k) + ENSO(t) + ENSO(t-k) + tendencia(t) + error(t)`

- En k=0 incluir ENSO una sola vez. Comprobar rango y colinealidad de la matriz; un ajuste singular se marca como no estimable.
- Inferencia principal: regresión lineal con errores estándar HAC/Newey–West, ancho de 12 meses fijado de antemano. Requiere añadir `statsmodels` como dependencia al implementar.
- Reportar beta estandarizado, IC del 95 %, p bilateral HAC y correlación parcial descriptiva. Calcular la correlación parcial residualizando ambas variables ya alineadas contra la misma matriz de controles.
- Ajustar los 12 p-valores con Benjamini–Hochberg (FDR); usar `p_fdr < 0.05` como umbral de detección dentro de esta familia.
- No usar directamente el p de Pearson para observaciones independientes sobre meses autocorrelacionados. Incluir diagnósticos de residuos y sensibilidad HAC a 6 y 24 meses.
- Calcular rezagos antes de excluir 1998 o dividir el periodo; recalcular controles y ajustes en cada subconjunto.

## Sensibilidad y alcance

- Repetir sin 1998 y por dos mitades temporales, reportando signo, efecto e incertidumbre. Consistencia de signo sola no confirma robustez.
- Comparar con Spearman y con `chl` como análisis secundarios; mantener sus familias de pruebas identificadas y corregidas, sin utilizarlas para rescatar un resultado principal negativo.
- Las bandas subsuperficiales, otras regiones y otros rezagos quedan para una ampliación explícita; no buscar retrospectivamente el menor p-valor.
- Comparaciones entre campos del mismo modelo CMEMS no constituyen validación observacional independiente. La comprobación con carbono satelital NASA sería una etapa posterior.

## Salidas

- `input_audit.json`: cobertura, unidades, duplicados, exclusiones, procedencia y hashes SHA-256 de entradas.
- `aligned_panel.csv`: meses y variables efectivamente usados.
- `primary_results.csv`: región, banda, rezago, n, beta, IC, correlación parcial, p HAC, p FDR y diagnóstico.
- `sensitivity_results.csv`: resultados sin 1998, por mitades y con otros anchos HAC.
- `analysis_config.json`: periodo, referencia climatológica, controles, métodos, umbrales, versiones y semilla si hay remuestreo.
- `report.md`: conclusión automática con los valores reales y límites de interpretación.

## Regla para concluir

- Ningún contraste con p FDR < 0.05: «No se obtuvo evidencia suficiente para rechazar H0 en los 12 contrastes especificados».
- Contraste significativo: identificar región, rezago, efecto e intervalo; si depende de periodo o especificación temporal, describirlo como asociación sensible.
- Si persiste en las sensibilidades: «Asociación exploratoria consistente con las comprobaciones realizadas», sin afirmar causalidad ni validación independiente.
- Si los datos o diagnósticos no permiten inferencia fiable: «No concluyente», con la causa registrada.

El p-valor no es la probabilidad de que H0 sea verdadera. No se escogerá un único p mínimo para representar toda la hipótesis Antártida–Humboldt.

## Verificación al implementar

- Serie sintética con calendario y rezago conocido para comprobar la dirección temporal.
- Meses faltantes y duplicados para comprobar que no se desplazan fechas ni se multiplican observaciones.
- Serie constante o matriz singular para comprobar la salida no estimable.
- Conversión mmol a mg para comprobar invariancia de correlaciones y p-valores.
- Comprobación numérica de HAC y FDR contra las funciones de referencia, y corrida reproducible completa con los datos locales.

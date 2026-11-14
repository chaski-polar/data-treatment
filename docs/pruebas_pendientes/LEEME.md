# Pruebas pendientes (13/11/2026)

**Reporte principal:** [Reporte consolidado de resultados](REPORTE_CONSOLIDADO_RESULTADOS.md),
con resumen inicial de relaciones interesantes, métodos, resultados históricos,
correcciones de la ronda de tendencias y anexos completos de las pruebas recientes.

- `SEGUIMIENTO_PRUEBAS.md`: registro de todo lo probado y su estado (se actualiza).
- `tendencias.py`: tendencias (Mann-Kendall, Sen, serie larga).
- `PRUEBAS_POSIBLES.md`: hipótesis, criterio de aceptación y viabilidad.
- `RESULTADOS_PRUEBAS_PENDIENTES.md`: resultados de A1, A3, A4 y B1.
- `pruebas_pendientes.py` y `pruebas_pendientes_2.py`: scripts (el segundo usa también el panel de conectividad). Lee el monitor mensual (`monitor_data.json`), `datos.js` de la web (viento ERA5) y los desembarques BCRP de `punto1_anchoveta`; las rutas al inicio del archivo son locales y deben ajustarse.
- Tablas completas en `data/tablas_pruebas_pendientes/`.

## Investigación de relaciones ecológicas (14/11/2026)

Resultados y prioridades en `INVESTIGACION_RELACIONES_ECOLOGICAS.md`.
La exploración incluye 33 contrastes con FDR global, controles, sensibilidades
temporales y evaluación condicional por años. Recupera la capa de mezcla desde
`surface_2d`; el análisis E7 anterior la buscaba en otra banda y la descartaba.

```bash
uv run python scripts/19_investigate_ecosystem_relationships.py
```

Salidas: `data/processed/analysis/ecosystem_relationships/` (tablas completas,
configuración y hashes, informe y gráfico de efectos). Es una exploración
retrospectiva; los resultados entre campos CMEMS requieren validación externa.

## Contraste con biomasa fitoplanctónica (carbono CMEMS)

Desde la raíz de `data_treatment`, con las entradas locales ya disponibles:

```bash
uv run python scripts/18_test_phytoplankton_carbon_connectivity.py
```

El script compara `phyc` superficial de Península Antártica y Bellingshausen
con Humboldt peruano en seis rezagos (12 contrastes). Controla Niño 1+2,
tendencia y mes calendario; utiliza HAC/Newey–West y corrección FDR.
No descarga datos ni requiere Colab. `uv run` instala las dependencias del proyecto.

Si las entradas están en otro directorio:

```bash
uv run python scripts/18_test_phytoplankton_carbon_connectivity.py \
  --panel /ruta/connectivity_panel_monthly.csv \
  --nino12 /ruta/nino12.long.anom.csv \
  --output /ruta/resultados
```

Las salidas predeterminadas están en
`data/processed/analysis/phytoplankton_carbon_connectivity/`:
`report.md`, `primary_results.csv`, `sensitivity_results.csv`,
`aligned_panel.csv`, `input_audit.json` y `analysis_config.json`.
Una nueva ejecución reemplaza estas salidas; usa `--output` para conservar corridas separadas.

El reporte distingue significancia de estabilidad y limita la conclusión a
asociaciones entre campos del mismo modelo. Los intervalos son individuales,
y el p FDR corrige cada familia predefinida de 12 contrastes.
El plan completo está en `PLAN_ANALISIS_BIOMASA_FITOPLANCTON.md`.

Verificación del script:

```bash
uv run python -m unittest discover -s tests -p 'test_phytoplankton_carbon_connectivity.py'
```

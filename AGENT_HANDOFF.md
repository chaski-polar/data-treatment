# AGENT HANDOFF — NASA Hackathon / Monitor Anchoveta

Fecha de esta sesión: 2026-11-02  
Repositorio: `data_treatment`  
Último commit funcional del pipeline: `85d8711 feat(data): generate experiment C panel`

## Objetivo del proyecto

El proyecto tiene dos usos relacionados:

1. Monitorizar y apoyar predicciones de corto plazo sobre condiciones oceanográficas, productividad y anchoveta peruana.
2. Alimentar un apartado de videojuego que simula múltiples escenarios con las ecuaciones del proyecto. El videojuego puede usar variables interpoladas/estimadas, pero deben conservar una marca de calidad distinta a las observaciones.

La página web muestra el monitor sobre un globo 3D. El tutorial/videojuego conserva su lógica narrativa y sus escenarios hardcodeados cuando corresponde; la sustitución por datos reales se aplica al monitor y a las partes compatibles del flujo de datos, no a la jugabilidad.

## Hallazgos sobre la página web

- El monitor de condiciones se muestra en la interfaz asociada al globo 3D y en la barra inferior de información.
- La biomasa de anchoveta puede mostrarse como observada durante ventanas de crucero y como interpolada entre observaciones. La interpolación no debe presentarse como medición.
- El mapa de fitoplancton/clorofila-a requiere una grilla espacial, no solamente una mediana regional mensual. El pipeline de `data_treatment` ya genera esa grilla en JSON para que la página filtre/coloree las celdas visibles.
- La clorofila del monitor procede del producto `chl` de CMEMS BGC/reanálisis. Es diferente de una capa satelital independiente como OC-CCI, aunque OC-CCI puede seguir usándose como fuente adicional de comparación.
- Los valores del tutorial del hielo a la anchoveta y la parte de videojuego no deben asumirse como datos observados: la narrativa/jugabilidad puede seguir hardcodeada mientras el monitor usa las salidas reales.

## Fuentes y datos confirmados

Caja regional principal del mar peruano:

```text
longitud: -85.0 a -70.0 °O
latitud:  -18.35 a -3.38 °S
```

Fuentes principales ya contempladas por el pipeline:

- CMEMS físico: temperatura (`thetao`) y salinidad (`so`).
- CMEMS BGC: clorofila (`chl`), nitrato (`no3`), fosfato (`po4`), oxígeno (`o2`) y carbono fitoplanctónico (`phyc`).
- OC-CCI: clorofila independiente vía ERDDAP, cuando el archivo está disponible.
- NOAA/PSL: PDO y otros índices existentes en el proyecto.
- IGP/ENFEN: ICEN.
- NOAA/CPC: Niño 1+2.
- IMARPE: biomasa de cruceros, por intervalos de fecha.

### Zooplancton CMEMS

Durante la investigación del catálogo se corrigieron dos errores de especificación:

- El dataset histórico válido es `cmems_mod_glo_bgc_my_0.083deg-lmtl_P1D-i`, no `...PT1D-i`.
- El catálogo devolvió la versión disponible `202511`; la versión `202211` no existe para ese dataset.

El catálogo también mostró el dataset secundario `cmems_mod_glo_bgc_my_0.083deg-lmtl-Fphy_P1D-i`, pero no se usa para la biomasa de zooplancton.

Datasets descargados/configurados:

```text
Histórico:
cmems_mod_glo_bgc_my_0.083deg-lmtl_P1D-i
versión: 202511
variable: zooc
periodo configurado: 1998-01-01 a 2025-12-31

Operativo:
cmems_mod_glo_bgc-plankton_anfc_0.25deg_P1M-m
variable: zooc
periodo configurado: 2023-12-01 a 2026-08-31
```

Archivos locales generados, ignorados por Git mediante `data/`:

- `data/raw/copernicus/zooplankton_hindcast_1998-01-01_2025-12-31.nc`
- `data/raw/copernicus/zooplankton_operational_2023-12-01_2026-08-31.nc`

Características observadas:

- Hindcast: diario, grilla `180 x 181`, `zooc` en `g m-2`, contenido integrado.
- Operativo: mensual, grilla `60 x 61`, cuatro niveles superficiales, `zooc` en `mmol m-3`.
- No se concatenan directamente porque tienen diferente resolución, unidad y definición vertical.

## Implementación realizada

### `scripts/01_download_data.py`

Ahora descarga por separado el zooplancton histórico y operativo. El histórico usa explícitamente `dataset_version="202511"`. Se conservan archivos NetCDF independientes y se agregan al manifiesto.

La descarga operativa solicita 0–5 m. El producto devuelve varios niveles dentro de esa ventana; el constructor toma la primera capa para representar la disponibilidad superficial de alimento.

Prueba de configuración realizada:

```bash
.venv/bin/python scripts/01_download_data.py \
  --source copernicus \
  --start 1998-01-01 \
  --end 2026-08-31 \
  --dry-run
```

Resultado: las ventanas históricas y operativas se resolvieron correctamente.

### `scripts/04_build_real_panel.py`

Se añadieron:

- `--zooplankton-hindcast` y `--zooplankton-operational` para sobreescribir rutas.
- `--experiment-c` para generar el panel F-Z-A.
- Lectura mensual espacial de `zooc` sin cargar innecesariamente la grilla completa.
- Conversión canónica de zooplancton a `mg C m-2`:
  - `g C m-2` → `mg C m-2` multiplicando por 1000.
  - `mmol C m-3` → `mg C m-2` usando carbono molar `12.0107` e integración aproximada de 5 m.
- Armonización del producto operativo al hindcast mediante la mediana de la razón durante el solapamiento.
- Conservación de `zooplankton_source`, `zooplankton_conversion` y `zooplankton_harmonization_factor`.
- Uso automático de `biomass_total_t_interpolated` al activar C si no se solicitó antes.
- JSON con metadatos de estados, unidades, fuentes y calidad.

El panel del Experimento C usa:

```text
F = phytoplankton_carbon   [mg C m-3]
Z = zooplankton             [mg C m-2]
A = biomass_anchoveta       [t]
```

Importante: F y Z no están en la misma unidad por volumen. El panel es adecuado para monitorización exploratoria y simulación, pero no debe llamarse calibración científica validada sin una definición vertical/observacional más sólida.

### `scripts/12_check_experiment_c.py`

El archivo por defecto cambió de `panel_peru_monthly.csv` a:

```text
data/processed/tables/experiment_c_panel.csv
```

El validador requiere al menos 24 observaciones completas de F, Z y A.

### Documentación

`docs/metodologia.md` ahora documenta los datasets de zooplancton, la unión hindcast-operativo y la generación del panel C.

## Salidas verificadas

Comando ejecutado:

```bash
.venv/bin/python scripts/04_build_real_panel.py --experiment-c
```

Salidas relevantes:

- `data/processed/tables/experiment_c_panel.csv`
- `data/processed/tables/experiment_c_panel.json`
- `data/processed/tables/monitoring_series_ab.csv`
- `data/processed/tables/monitoring_series_ab.json`
- `data/processed/tables/monitoring_grid_chlorophyll.json`
- `data/processed/tables/panel_quality_report.csv`

Resultados de la ejecución:

- 344 meses en el panel C.
- 280 meses con F-Z-A completos.
- 23 meses con biomasa observada.
- 257 meses con biomasa interpolada.
- 64 meses sin biomasa disponible.
- Zooplancton: 336 meses provenientes del hindcast y 8 del producto operativo.

Calidades registradas:

```text
zooplankton_model + biomass_observed       23
zooplankton_model + biomass_interpolated  257
zooplankton_model + biomass_missing        64
```

Verificación ejecutada:

```bash
.venv/bin/python scripts/12_check_experiment_c.py
```

Salida:

```text
Experimento C: 280 observaciones completas disponibles
```

También pasaron:

```bash
.venv/bin/python -m py_compile \
  scripts/01_download_data.py \
  scripts/04_build_real_panel.py \
  scripts/12_check_experiment_c.py
git diff --check
```

## Limitaciones conocidas

1. El zooplancton usado es modelado CMEMS, no una serie de observaciones directas de zooplancton.
2. La armonización del producto operativo es pragmática: usa el solapamiento hindcast-operativo, no una calibración biológica independiente.
3. La integración de `mmol C m-3` a `mg C m-2` usa aproximadamente 5 m; debe revisarse si el modelo requiere otra profundidad efectiva.
4. Se selecciona la primera capa operativa, aunque el producto ofrece varios niveles superficiales.
5. La biomasa interpolada solo es válida entre observaciones y no extrapola. Está destinada al monitor/videojuego, no a tratarse como observación en el ajuste.
6. No se debe mezclar biomasa con desembarques sin modelar explícitamente el esfuerzo pesquero, cuotas, vedas y cambios de fuente.
7. F y Z tienen unidades verticales distintas (`m-3` frente a `m-2`); las ecuaciones del Experimento C deben adaptarse antes de interpretar parámetros o tasas.
8. La salida de grilla de clorofila está cuantizada en escala logarítmica y comprimida; la página web debe decodificar `gzip + Base64` según el campo `encoding.decode`.
9. Los archivos bajo `data/` están ignorados por Git y no forman parte del commit. Deben regenerarse o conservarse localmente.

## Siguientes pasos recomendados

1. Conectar `experiment_c_panel.json` al monitor de `pagina-web` y mostrar una etiqueta clara cuando A sea interpolada.
2. Usar `monitoring_grid_chlorophyll.json` para colorear la capa espacial del globo por mes seleccionado.
3. Añadir en la página una leyenda que distinga clorofila CMEMS/reanálisis de OC-CCI.
4. Implementar una función de decodificación de la grilla y comprobar orientación latitud/longitud, especialmente si el renderer invierte el eje Y.
5. Definir la profundidad efectiva de Z de acuerdo con las ecuaciones del videojuego y mantener la conversión documentada.
6. Si se busca calibración, incorporar observaciones de zooplancton/fracciones de tamaño y validar contra una ventana temporal reservada.
7. Revisar la parte matemática del modelo C para integrar correctamente resolución diaria/mensual y unidades F-Z-A.

## Estado Git

Commit de implementación:

```text
85d8711 feat(data): generate experiment C panel
```

`graphify-out/` permanece sin seguimiento y no fue incluido. No se incluyeron credenciales, NetCDF ni salidas grandes en Git.

# Pipeline de conectividad oceanográfica

Este pipeline añade una capa regional al procesamiento peruano existente. No
reemplaza las descargas ni los paneles de los Experimentos A y B.

## Regiones

Las cajas están definidas en `src/nasahackaton/config.py`:

- Península Antártica.
- Mar de Bellingshausen.
- Pacífico Sur intermedio.
- Pacífico Sur subtropical.
- Transición hacia Humboldt.
- Humboldt peruano.

## Descarga CMEMS

La descarga se realiza con:

```bash
.venv/bin/python scripts/07_download_connectivity.py \
  --start 1998-01-01 \
  --end 2025-12-01 \
  --physics-max-depth 1000 \
  --bgc-max-depth 500
```

El script genera tres NetCDF por región:

```text
physics_3d_monthly.nc
physics_surface_monthly.nc
biogeochemistry_monthly.nc
```

También genera `connectivity_download_manifest.json`, que registra dataset,
variables, caja, profundidad, fechas, estado y SHA-256.

Antes de descargar se puede inspeccionar el plan:

```bash
.venv/bin/python scripts/07_download_connectivity.py --dry-run
```

## Construcción del panel

```bash
.venv/bin/python scripts/11_build_connectivity_panel.py
```

La salida es:

```text
data/processed/tables/connectivity_panel_monthly.csv
```

Cada fila representa una región, fecha y banda vertical. Las variables tienen
además columnas `_anom`, calculadas como anomalías respecto al promedio del
mismo mes dentro del periodo disponible.

Si todavía no existe una descarga regional nueva para `peru_humboldt`, el
constructor puede usar explícitamente los archivos peruanos ya existentes:

```bash
.venv/bin/python scripts/11_build_connectivity_panel.py \
  --legacy-peru-input data/raw/copernicus
```

Ese fallback no crea datos antárticos ni subsuperficiales; solo permite probar
el panel con datos reales ya disponibles.

## Validación de descargas

Antes de utilizar el panel, validar que cada NetCDF contiene las variables,
fechas, coordenadas y profundidades esperadas:

```bash
.venv/bin/python scripts/12_validate_connectivity.py
```

El reporte se guarda en
`data/processed/tables/connectivity_quality_report.json`. Las regiones que
todavía no tienen descargas se marcan como `missing`; no se rellenan con el
dominio peruano.

## Fuentes complementarias

Hielo marino espacial NSIDC/Earthdata:

```bash
.venv/bin/python scripts/08_download_sea_ice.py \
  --start 1998-01-01 \
  --end 2025-12-31
```

Corrientes superficiales OSCAR/PO.DAAC:

```bash
.venv/bin/python scripts/09_download_oscar.py \
  --start 1998-01-01 \
  --end 2025-12-31
```

Ambos comandos admiten `--dry-run`. NSIDC G02202 representa concentración de
hielo en una grilla polar; OSCAR representa corrientes superficiales y no debe
interpretarse como transporte subsuperficial o AAIW.

## Interpretación

Los campos CMEMS son productos de reanálisis/modelo. Las anomalías regionales
permiten estudiar asociaciones, gradientes y rezagos, pero no prueban por sí
solas transporte directo de agua ni causalidad biológica.

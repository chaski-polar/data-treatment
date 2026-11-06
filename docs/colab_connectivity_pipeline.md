# Ejecución en Google Colab

El pipeline completo está en `scripts/13_full_connectivity_pipeline.py`. Colab es
útil para descargar los NetCDF grandes usando la red de Google y guardar los
archivos en Google Drive. No es necesario subir esos NetCDF al repositorio ni a la
aplicación web: para la aplicación normalmente basta con el panel CSV, los
reportes y las figuras agregadas.

## 1. Preparar el entorno

```python
from google.colab import drive
drive.mount('/content/drive')

!git clone <URL_DEL_REPOSITORIO> /content/nasahackathon
%cd /content/nasahackathon/data_treatment

!pip install -q copernicusmarine earthaccess xarray netcdf4 h5netcdf pandas scipy
```

Si el repositorio exige una versión de Python no disponible en Colab, se puede
usar el código fuente directamente:

```python
import sys
sys.path.insert(0, '/content/nasahackathon/data_treatment/src')
```

## 2. Autenticación

```python
import copernicusmarine
copernicusmarine.login()       # usuario y contraseña de Copernicus Marine

import earthaccess
earthaccess.login(persist=True)  # cuenta Earthdata de NASA
```

Las credenciales no deben escribirse en el notebook ni guardarse en Git.

## 3. Revisar antes de descargar

```bash
!python scripts/13_full_connectivity_pipeline.py --mode inventory
```

El inventario queda en
`data/processed/tables/connectivity_file_inventory.json`, ordenado de mayor a
menor tamaño. Este paso permite continuar una descarga parcial sin volver a
descargar archivos existentes.

## 4. Descargar

Para la corrida completa:

```bash
!python scripts/13_full_connectivity_pipeline.py \
  --mode download \
  --start 1998-01-01 \
  --end 2025-12-01 \
  --physics-max-depth 1000 \
  --bgc-max-depth 500
```

La ejecución también descarga los productos CMEMS peruanos heredados usados por
los experimentos existentes en `data/raw/copernicus/`. Para omitir esa descarga
redundante se puede añadir `--skip-legacy-copernicus`.

Para una primera corrida de menor tamaño:

```bash
!python scripts/13_full_connectivity_pipeline.py \
  --mode download \
  --regions peninsula_antarctica bellingshausen south_pacific_intermediate \
  --start 1998-01-01 \
  --end 2025-12-01 \
  --physics-max-depth 500 \
  --bgc-max-depth 100 \
  --skip-ice --skip-oscar
```

Los NetCDF se guardan bajo `data/raw/`. Para conservarlos entre sesiones, ubica
el repositorio o mueve `data/raw` a una carpeta de Drive. El espacio local de
Colab es temporal.

## 5. Procesar y validar

```bash
!python scripts/13_full_connectivity_pipeline.py --mode process --skip-ice --skip-oscar
```

Salidas principales:

- `data/processed/tables/connectivity_panel_monthly.csv`
- `data/processed/tables/connectivity_pipeline_report.md`
- `data/processed/tables/connectivity_file_inventory.json`
- `data/processed/tables/connectivity_quality_report.json`

El procesamiento reduce primero cada NetCDF a promedios espaciales y bandas de
profundidad; no carga el archivo multidimensional completo en memoria. Las
regiones o meses faltantes se reportan como faltantes y no se interpolan
automáticamente.

## 6. Qué subir a la aplicación

Subir el panel CSV y los reportes. Mantener los NetCDF grandes en Drive u otro
almacenamiento de objetos y servir solo agregados o subconjuntos bajo demanda.
El archivo de biomasa de anchoveta debe conservarse separado de los campos
ambientales y unirse únicamente mediante una clave temporal/espacial documentada.

# Guía completa para ejecutar ANCHOVETA 360 en Google Colab

Esta guía usa `scripts/13_full_connectivity_pipeline.py` para descargar,
procesar y validar los datos de conectividad oceanográfica.

El repositorio contiene el código y los insumos pequeños. No contiene los
productos grandes que se generan o descargan durante la ejecución:

```text
data_treatment/data/raw/connectivity/   # CMEMS regional, varios GB
data_treatment/data/raw/copernicus/     # CMEMS peruano heredado
data_treatment/data/raw/woa23/          # climatología WOA23
data_treatment/data/processed/          # salidas generadas por los scripts
```

## 1. Montar Google Drive

Drive es necesario porque el almacenamiento local de Colab se borra cuando la
sesión termina.

```python
from google.colab import drive
drive.mount('/content/drive')
```

Se recomienda conservar el proyecto en una carpeta de Drive, por ejemplo:

```text
MyDrive/ANCHOVETA360/
```

## 2. Clonar el repositorio

Si el repositorio es público:

```bash
!git clone <URL_DEL_REPOSITORIO> /content/ANCHOVETA360
```

Si es privado, autentícate primero con GitHub o usa un token. Después:

```python
%cd /content/ANCHOVETA360
```

Los datos pequeños incluidos en el repositorio quedarán automáticamente en sus
rutas originales, por ejemplo:

```text
data_treatment/data/biomasa_cruceros.csv
data_treatment/data/raw/noaa/
data_treatment/data/raw/era5/
data_treatment/data/raw/igp/
```

## 3. Instalar dependencias

```bash
!pip install -q copernicusmarine earthaccess xarray netcdf4 h5netcdf pandas scipy requests \
  "fsspec==2025.12.0" "gcsfs==2025.12.0"
```

La versión fija de `fsspec` evita el conflicto con `gcsfs` y `datasets`, que ya
vienen instalados en Colab. Ejecuta esta celda antes de importar
`copernicusmarine`, `earthaccess` o `xarray`.

No es necesario ejecutar `pip install -e .`; el notebook puede utilizar
directamente el código fuente del proyecto:

```python
import sys
sys.path.insert(0, '/content/ANCHOVETA360/data_treatment/src')
```

## 4. Autenticar las APIs

Copernicus Marine:

```python
import copernicusmarine
copernicusmarine.login()
```

Earthdata/NASA:

```python
import earthaccess
earthaccess.login(persist=True)
```

No escribas las contraseñas en el notebook ni las subas al repositorio.

## 5. Preparar datos grandes existentes en Drive

Si ya descargaste archivos en Drive, cópialos al proyecto de Colab conservando
la estructura:

```bash
!mkdir -p data_treatment/data/raw/connectivity data_treatment/data/raw/copernicus
!cp -r /content/drive/MyDrive/ANCHOVETA360/data/raw/connectivity/* data_treatment/data/raw/connectivity/ 2>/dev/null || true
!cp -r /content/drive/MyDrive/ANCHOVETA360/data/raw/copernicus/* data_treatment/data/raw/copernicus/ 2>/dev/null || true
```

Si los archivos todavía no existen, el pipeline los descargará. No uses
`--force` salvo que quieras reemplazar archivos válidos.

## 6. Revisar el inventario

```bash
!python data_treatment/scripts/13_full_connectivity_pipeline.py --mode inventory
```

El inventario se escribe en:

```text
data_treatment/data/processed/tables/connectivity_file_inventory.json
```

La tabla está ordenada de mayor a menor tamaño y diferencia archivos
descargados, faltantes y disponibles pero no cubiertos por el orquestador.

## 7. Primera descarga pequeña de prueba

Antes de descargar todas las regiones, prueba con tres regiones y menor
profundidad:

```bash
!python data_treatment/scripts/13_full_connectivity_pipeline.py \
  --mode download \
  --regions peninsula_antarctica bellingshausen south_pacific_intermediate \
  --start 1998-01-01 \
  --end 2025-12-01 \
  --physics-max-depth 500 \
  --bgc-max-depth 100 \
  --skip-ice \
  --skip-oscar \
  --skip-legacy-copernicus
```

Esta prueba verifica credenciales, catálogo y espacio disponible sin descargar
todos los productos auxiliares.

## 8. Descarga completa recomendada

Cuando la prueba funcione:

```bash
!python data_treatment/scripts/13_full_connectivity_pipeline.py \
  --mode download \
  --start 1998-01-01 \
  --end 2025-12-01 \
  --physics-max-depth 1000 \
  --bgc-max-depth 500
```

Esta ejecución descarga:

1. CMEMS físico 3D y superficial en `data_treatment/data/raw/connectivity/`.
2. CMEMS biogeoquímico en `data_treatment/data/raw/connectivity/`.
3. Productos CMEMS peruanos heredados en `data_treatment/data/raw/copernicus/`.
4. Hielo NSIDC, salvo que se indique `--skip-ice`.
5. Corrientes OSCAR, salvo que se indique `--skip-oscar`.

Para G02202, si CMR/Earthaccess no devuelve granules aunque las credenciales
sean correctas, `08_download_sea_ice.py` usa automáticamente el índice HTTPS
oficial de NOAA@NSIDC y descarga los NetCDF mensuales del hemisferio sur. Esto
evita que un resultado vacío termine en `earthaccess.download([])`.

Para omitir los productos peruanos heredados se añade:

```bash
--skip-legacy-copernicus
```

Para omitir NSIDC y OSCAR durante una primera corrida se añade:

```bash
--skip-ice --skip-oscar
```

El script conserva los archivos existentes y registra cada solicitud en los
manifiestos. Si una descarga se interrumpe, vuelve a ejecutar el mismo comando;
los archivos completos serán omitidos automáticamente.

## 9. Procesar y validar

Después de la descarga:

```bash
!python data_treatment/scripts/13_full_connectivity_pipeline.py \
  --mode process \
  --skip-ice \
  --skip-oscar
```

Se generan:

```text
data_treatment/data/processed/tables/connectivity_panel_monthly.csv
data_treatment/data/processed/tables/connectivity_pipeline_report.md
data_treatment/data/processed/tables/connectivity_file_inventory.json
data_treatment/data/processed/tables/connectivity_quality_report.json
```

El procesamiento reduce primero cada NetCDF a promedios espaciales y bandas de
profundidad. No carga el archivo multidimensional completo en memoria. Los
meses o regiones faltantes se reportan; no se rellenan automáticamente.

## 10. Guardar las salidas en Drive

Como `data_treatment/data/processed/` está excluida del repositorio, copia los resultados a
Drive si quieres conservarlos:

```bash
!mkdir -p /content/drive/MyDrive/ANCHOVETA360/processed
!cp -r data_treatment/data/processed/* /content/drive/MyDrive/ANCHOVETA360/processed/
```

## 11. Qué debe utilizar la aplicación

La aplicación no debería cargar directamente los NetCDF de varios gigabytes.
Conviene servir:

```text
connectivity_panel_monthly.csv
connectivity_quality_report.json
connectivity_pipeline_report.md
```

Los NetCDF deben permanecer en Drive o en almacenamiento de objetos. La
biomasa de anchoveta debe mantenerse identificada como respuesta biológica y
unirse al panel ambiental solo mediante fecha, región y definición de biomasa
documentadas.

## 12. Comprobación final

```bash
!python data_treatment/scripts/13_full_connectivity_pipeline.py --mode inventory
!du -sh data_treatment/data/raw/* data_treatment/data/processed 2>/dev/null
```

Antes de cerrar la sesión, confirma que el panel y los reportes fueron copiados
a Drive. El almacenamiento temporal de Colab no debe considerarse permanente.

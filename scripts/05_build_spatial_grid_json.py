"""Construye un JSON multivariable de datos oceanográficos por píxel.

El script está pensado para ejecutarse en Google Colab después de descargar los
datos con ``scripts/02_download_experiment_b.py``. Procesa una variable a la vez
para no cargar todos los NetCDF en memoria y usa la grilla CMEMS BGC de 0,25°
como grilla común. OSCAR no forma parte de este flujo.

Salidas principales:

* ``spatial_grid_multivariable.json``: metadatos, capas espaciales codificadas
  como float32+gzip+Base64 y series regionales de ``monitor_data.json``.
* ``spatial_grid_multivariable.json.gz``: la misma salida comprimida para subir
  o servir desde un almacenamiento web.
* ``spatial_grid_quality.csv``: cobertura, unidades, rangos y archivos usados.

Las capas espaciales conservan el orden ``time, latitude, longitude``. Los
valores faltantes se representan con ``NaN`` dentro del bloque binario y no se
rellenan ni se extrapolan.
"""

from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd
import xarray as xr


LOG = logging.getLogger("build_spatial_grid_json")
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "raw"
DEFAULT_OUTPUT = ROOT / "data" / "processed" / "spatial"
DEFAULT_MONITOR = ROOT / "src" / "nasahackaton" / "monitor_data.json"

# Caja del sistema de Humboldt peruano utilizada por los scripts de descarga.
DEFAULT_BBOX = {"west": -85.0, "south": -18.35, "east": -70.0, "north": -3.38}

Transform = Callable[[xr.DataArray], xr.DataArray]


def _identity(data: xr.DataArray) -> xr.DataArray:
    return data


def _divide(value: float) -> Transform:
    def transform(data: xr.DataArray) -> xr.DataArray:
        return data / value

    return transform


def _multiply(value: float) -> Transform:
    def transform(data: xr.DataArray) -> xr.DataArray:
        return data * value

    return transform


def _specs(input_dir: Path) -> list[dict[str, Any]]:
    """Especificaciones de variables; una fuente puede producir varias capas."""
    specs = [
        # CMEMS BGC.
        {"id": "chlorophyll_cmems", "file": input_dir / "copernicus/biogeochemistry_b.nc", "candidates": ("chl",), "unit": "mg m-3", "source": "CMEMS BGC", "transform": _identity, "depth": True},
        {"id": "nitrate", "file": input_dir / "copernicus/biogeochemistry_b.nc", "candidates": ("no3", "nitrate"), "unit": "mmol m-3", "source": "CMEMS BGC", "transform": _identity, "depth": True},
        {"id": "phosphate", "file": input_dir / "copernicus/biogeochemistry_b.nc", "candidates": ("po4", "phosphate"), "unit": "mmol m-3", "source": "CMEMS BGC", "transform": _identity, "depth": True},
        {"id": "oxygen_mmol_m3", "file": input_dir / "copernicus/biogeochemistry_b.nc", "candidates": ("o2", "oxygen"), "unit": "mmol m-3", "source": "CMEMS BGC", "transform": _identity, "depth": True},
        {"id": "oxygen_ml_l", "file": input_dir / "copernicus/biogeochemistry_b.nc", "candidates": ("o2", "oxygen"), "unit": "ml l-1", "source": "CMEMS BGC", "transform": _divide(44.66), "depth": True, "derived_from": "oxygen_mmol_m3"},
        {"id": "phytoplankton_carbon_mmol_c_m3", "file": input_dir / "copernicus/biogeochemistry_b.nc", "candidates": ("phyc", "phytoplankton_carbon"), "unit": "mmol C m-3", "source": "CMEMS BGC", "transform": _identity, "depth": True},
        {"id": "phytoplankton_carbon_mg_c_m3", "file": input_dir / "copernicus/biogeochemistry_b.nc", "candidates": ("phyc", "phytoplankton_carbon"), "unit": "mg C m-3", "source": "CMEMS BGC", "transform": _multiply(12.0107), "depth": True, "derived_from": "phytoplankton_carbon_mmol_c_m3"},
        # CMEMS física, corrientes y nivel del mar.
        {"id": "sst", "file": input_dir / "copernicus/physics_b.nc", "candidates": ("thetao", "sst", "temperature"), "unit": "degC", "source": "CMEMS physics", "transform": _identity, "depth": True},
        {"id": "salinity", "file": input_dir / "copernicus/physics_b.nc", "candidates": ("so", "salinity"), "unit": "PSU", "source": "CMEMS physics", "transform": _identity, "depth": True},
        {"id": "current_u", "file": input_dir / "copernicus/currents_b.nc", "candidates": ("uo", "u", "current_u"), "unit": "m s-1", "source": "CMEMS currents", "transform": _identity, "depth": True},
        {"id": "current_v", "file": input_dir / "copernicus/currents_b.nc", "candidates": ("vo", "v", "current_v"), "unit": "m s-1", "source": "CMEMS currents", "transform": _identity, "depth": True},
        {"id": "sea_level", "file": input_dir / "copernicus/ssh_b.nc", "candidates": ("zos", "ssh", "sea_level"), "unit": "m", "source": "CMEMS SSH", "transform": _identity, "depth": False},
        # OC-CCI y NASA Ocean Color.
        {"id": "chlorophyll_occci", "file": input_dir / "ocean_color/chlorophyll_occci.nc", "candidates": ("chlor_a", "chlorophyll", "chl"), "unit": "mg m-3", "source": "ESA OC-CCI v6", "transform": _identity, "depth": False},
        {"id": "kd490", "file": input_dir / "ocean_color/kd490_occci.nc", "candidates": ("kd_490", "kd490", "k490"), "unit": "m-1", "source": "ESA OC-CCI v6", "transform": _identity, "depth": False},
        # ERA5: los nombres varían según el conversor usado por CDS.
        {"id": "wind_u", "file": input_dir / "era5/wind_monthly.nc", "candidates": ("u10", "10m_u_component_of_wind", "u_component_of_wind"), "unit": "m s-1", "source": "ERA5", "transform": _identity, "depth": False},
        {"id": "wind_v", "file": input_dir / "era5/wind_monthly.nc", "candidates": ("v10", "10m_v_component_of_wind", "v_component_of_wind"), "unit": "m s-1", "source": "ERA5", "transform": _identity, "depth": False},
    ]
    nasa_dir = input_dir / "ocean_color" / "nasa"
    for variable_id, candidates, unit in (
        ("par", ("par", "PAR"), "Einstein m-2 day-1"),
        ("poc", ("poc", "POC"), "mg C m-3"),
        ("kd490_nasa", ("kd490", "k490", "kd_490"), "m-1"),
    ):
        files = sorted(nasa_dir.glob("*.nc")) if nasa_dir.exists() else []
        matching = [path for path in files if variable_id.replace("_nasa", "").upper() in path.name.upper()]
        if matching:
            specs.append({"id": variable_id, "files": matching, "candidates": candidates, "unit": unit, "source": "NASA Ocean Color", "transform": _identity, "depth": False})
    return specs


def _coord_name(ds: xr.Dataset, names: tuple[str, ...]) -> str | None:
    for name in names:
        if name in ds.coords or name in ds.dims:
            return name
    return None


def _find_variable(ds: xr.Dataset, candidates: tuple[str, ...]) -> str | None:
    for name in candidates:
        if name in ds.data_vars:
            return name
    normalized = {name.lower().replace("_", ""): name for name in ds.data_vars}
    for candidate in candidates:
        key = candidate.lower().replace("_", "")
        if key in normalized:
            return normalized[key]
    return None


def _subset_bbox(data: xr.DataArray, lat: str, lon: str, bbox: dict[str, float]) -> xr.DataArray:
    """Recorta independientemente de si las coordenadas están ascendentes."""
    lat_values = np.asarray(data[lat].values)
    lon_values = np.asarray(data[lon].values)
    lat_slice = slice(bbox["south"], bbox["north"]) if lat_values[0] < lat_values[-1] else slice(bbox["north"], bbox["south"])
    lon_slice = slice(bbox["west"], bbox["east"]) if lon_values[0] < lon_values[-1] else slice(bbox["east"], bbox["west"])
    return data.sel({lat: lat_slice, lon: lon_slice})


def _prepare_dataarray(ds: xr.Dataset, variable: str, spec: dict[str, Any], bbox: dict[str, float]) -> xr.DataArray:
    data = ds[variable]
    lat = _coord_name(ds, ("latitude", "lat", "y"))
    lon = _coord_name(ds, ("longitude", "lon", "x"))
    if not lat or not lon:
        raise ValueError(f"{variable}: no se encontraron coordenadas latitud/longitud")
    data = _subset_bbox(data, lat, lon, bbox)
    if spec.get("depth") and "depth" in data.dims:
        data = data.sel(depth=slice(0, 5)).mean("depth", skipna=True)
    time = _coord_name(ds, ("time", "valid_time", "date"))
    if not time or time not in data.dims:
        raise ValueError(f"{variable}: no se encontró una dimensión temporal")
    data = spec["transform"](data)
    data = data.rename({lat: "latitude", lon: "longitude", time: "time"})
    data = data.transpose("time", "latitude", "longitude")
    # Evita duplicar meses cuando una fuente tiene más de una observación mensual.
    dates = pd.to_datetime(data.time.values).to_period("M").to_timestamp().values
    data = data.assign_coords(time=dates).groupby("time").mean("time", skipna=True)
    return data.sortby("time").sortby("latitude").sortby("longitude")


def _target_grid(data: xr.DataArray) -> tuple[np.ndarray, np.ndarray]:
    lat = np.asarray(data.latitude.values, dtype=float)
    lon = np.asarray(data.longitude.values, dtype=float)
    return lat, lon


def _regrid(data: xr.DataArray, target_lat: np.ndarray, target_lon: np.ndarray) -> xr.DataArray:
    if np.array_equal(data.latitude.values, target_lat) and np.array_equal(data.longitude.values, target_lon):
        return data
    return data.interp(latitude=target_lat, longitude=target_lon, method="linear")


def _encode(data: np.ndarray) -> tuple[str, str]:
    values = np.asarray(data, dtype=np.float32)
    raw = np.ascontiguousarray(values).tobytes()
    compressed = gzip.compress(raw, compresslevel=9)
    return base64.b64encode(compressed).decode("ascii"), hashlib.sha256(raw).hexdigest()


def _layer_payload(data: xr.DataArray, spec: dict[str, Any], target_lat: np.ndarray, target_lon: np.ndarray) -> dict[str, Any]:
    values = np.asarray(data.values, dtype=np.float32)
    encoded, checksum = _encode(values)
    valid = np.isfinite(values)
    return {
        "variable_id": spec["id"],
        "name": spec["id"],
        "unit": spec["unit"],
        "source": spec["source"],
        "derived_from": spec.get("derived_from"),
        "depth": {"min_m": 0, "max_m": 5} if spec.get("depth") else None,
        "time": [pd.Timestamp(value).strftime("%Y-%m") for value in data.time.values],
        "grid": {
            "shape": [int(len(target_lat)), int(len(target_lon))],
            "data_order": ["time", "latitude", "longitude"],
            "latitude": [round(float(value), 6) for value in target_lat],
            "longitude": [round(float(value), 6) for value in target_lon],
        },
        "encoding": {
            "dtype": "float32",
            "byte_order": "little-endian",
            "compression": "gzip",
            "base64": True,
            "missing": "NaN",
            "decode": "gzip+base64 -> Float32Array",
        },
        "statistics": {
            "n_total": int(values.size),
            "n_valid": int(valid.sum()),
            "valid_fraction": round(float(valid.mean()), 6),
            "min": None if not valid.any() else float(np.nanmin(values)),
            "max": None if not valid.any() else float(np.nanmax(values)),
        },
        "sha256_raw_float32": checksum,
        "data_gzip_base64": encoded,
    }


def _monitor_series(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"source": str(path), "records": [], "warning": "monitor_data.json no existe"}
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = payload.get("records", [])
    spatial_names = {"lat", "latitude", "lon", "longitude"}
    scalar_records = []
    for row in records:
        scalar_records.append({key: value for key, value in row.items() if key not in spatial_names})
    return {
        "source": str(path),
        "period": payload.get("period"),
        "records": scalar_records,
        "notes": "Series regionales, índices y biomasa; no representan valores por píxel.",
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    input_dir = args.input_dir
    specs = _specs(input_dir)
    layers: list[dict[str, Any]] = []
    data_arrays: dict[str, xr.DataArray] = {}
    quality: list[dict[str, Any]] = []
    target_lat: np.ndarray | None = None
    target_lon: np.ndarray | None = None

    for spec in specs:
        paths = spec.get("files", [spec["file"]])
        missing = [path for path in paths if not path.exists()]
        if missing:
            quality.append({"variable_id": spec["id"], "status": "missing_file", "file": ";".join(map(str, missing))})
            LOG.warning("No existe(n) %s; se omite %s", ", ".join(map(str, missing)), spec["id"])
            continue
        try:
            pieces = []
            variable_names = []
            for path in paths:
                with xr.open_dataset(path, chunks=None) as ds:
                    variable = _find_variable(ds, spec["candidates"])
                    if variable is None:
                        continue
                    variable_names.append(variable)
                    pieces.append(_prepare_dataarray(ds, variable, spec, args.bbox).load())
            if not pieces:
                raise ValueError(f"no se encontró ninguna variable candidata {spec['candidates']}")
            data = xr.concat(pieces, dim="time").groupby("time").mean("time", skipna=True).sortby("time")
            if target_lat is None:
                target_lat, target_lon = _target_grid(data)
            data = _regrid(data, target_lat, target_lon).load()
            data_arrays[spec["id"]] = data
            layer = _layer_payload(data, spec, target_lat, target_lon)
            layers.append(layer)
            quality.append({
                "variable_id": spec["id"], "status": "ok", "file": ";".join(map(str, paths)),
                "source_variable": ";".join(sorted(set(variable_names))), "n_time": len(layer["time"]),
                **layer["statistics"],
            })
            LOG.info("%s: %s meses, %.1f%% válidos", spec["id"], len(layer["time"]), 100 * layer["statistics"]["valid_fraction"])
        except Exception as exc:  # una fuente ausente no debe impedir las demás capas
            quality.append({"variable_id": spec["id"], "status": "error", "file": str(path), "error": str(exc)})
            LOG.exception("No se pudo procesar %s", spec["id"])

    # Derivadas vectoriales: se calculan solo cuando ambos componentes existen.
    for output_id, left_id, right_id, unit, source in (
        ("current_speed", "current_u", "current_v", "m s-1", "CMEMS currents"),
        ("wind_speed", "wind_u", "wind_v", "m s-1", "ERA5"),
    ):
        if left_id not in data_arrays or right_id not in data_arrays:
            continue
        data = np.hypot(data_arrays[left_id], data_arrays[right_id]).astype("float32")
        spec = {"id": output_id, "unit": unit, "source": source, "derived_from": f"{left_id},{right_id}"}
        data_arrays[output_id] = data
        layer = _layer_payload(data, spec, target_lat, target_lon)
        layers.append(layer)
        quality.append({"variable_id": output_id, "status": "ok", "file": "derived", "source_variable": spec["derived_from"], **layer["statistics"]})

    if target_lat is None or target_lon is None:
        raise RuntimeError("No se pudo construir ninguna capa espacial")

    return {
        "schema_version": "2.0",
        "generated_at": pd.Timestamp.now(tz="UTC").isoformat(),
        "region": {"code": "peru_humboldt", "bbox": args.bbox},
        "grid": {
            "shape": [int(len(target_lat)), int(len(target_lon))],
            "latitude": [round(float(value), 6) for value in target_lat],
            "longitude": [round(float(value), 6) for value in target_lon],
            "data_order": ["time", "latitude", "longitude"],
        },
        "excluded_sources": [{"name": "OSCAR", "reason": "No se descarga por defecto por tamaño y costo de almacenamiento."}],
        "layers": layers,
        "regional_timeseries": _monitor_series(args.monitor_data),
        "quality_report": quality,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--monitor-data", type=Path, default=DEFAULT_MONITOR)
    parser.add_argument("--bbox", type=float, nargs=4, metavar=("WEST", "SOUTH", "EAST", "NORTH"), default=tuple(DEFAULT_BBOX.values()))
    parser.add_argument("--no-gzip-copy", action="store_true", help="no escribe la copia .json.gz")
    parser.add_argument("--log-level", default="INFO", choices=("DEBUG", "INFO", "WARNING", "ERROR"))
    args = parser.parse_args()
    args.bbox = dict(zip(("west", "south", "east", "north"), args.bbox))
    logging.basicConfig(level=getattr(logging, args.log_level), format="%(levelname)s %(message)s")

    payload = build(args)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir / "spatial_grid_multivariable.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    if not args.no_gzip_copy:
        with gzip.open(str(output) + ".gz", "wt", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, separators=(",", ":"))
    pd.DataFrame(payload["quality_report"]).to_csv(args.output_dir / "spatial_grid_quality.csv", index=False)
    print(f"JSON: {output}")
    print(f"Capas espaciales: {len(payload['layers'])}")
    print(f"Reporte: {args.output_dir / 'spatial_grid_quality.csv'}")


if __name__ == "__main__":
    main()

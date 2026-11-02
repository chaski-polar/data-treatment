"""Descarga de una sola ejecución para los datos del Experimento B.

Fuentes incluidas:
* CMEMS: física, corrientes, SSH y biogeoquímica.
* OC-CCI/OceanWatch: clorofila y Kd490 vía ERDDAP.
* NASA Ocean Color: PAR, Kd490 y POC vía Earthdata.
* ERA5: viento mensual vía CDS API.

No descarga zooplancton: no existe aquí un producto histórico automático y
homogéneo que pueda tratarse como equivalente a las variables CMEMS.
Las credenciales se leen de las configuraciones normales de cada cliente.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any

import copernicusmarine
import earthaccess
import pandas as pd
import requests

from nasahackaton.config import PERU_OCEAN, PROJECT_ROOT

LOG = logging.getLogger("download_experiment_b")
CMEMS_BGC = "cmems_mod_glo_bgc_my_0.25deg_P1M-m"
CMEMS_PHY = "cmems_mod_glo_phy_my_0.083deg_P1M-m"
OCCCI_SERVER = "https://oceanwatch.pifsc.noaa.gov/erddap"
OCCCI_CHL = "esa-cci-chla-monthly-v6-0"
# Kd490 mensual global. Las versiones v5/8-day anteriores quedaron
# obsoletas en OceanWatch; mantenerlas solo como fallback histórico.
OCCCI_KD_CANDIDATES = (
    "esa-cci-kd-monthly-v6-0",
    "aqua_kd490_monthly_2018_0",
    "esa-cci-kd-8d-v6-0",
    "esa-cci-kd-8d-v5-0",
)
NASA_SHORT_NAMES = {
    "par": ("MODISA_L3m_PAR",),
    "kd490": ("MODISA_L3m_KD490", "MODISA_L3m_KD490_NRT"),
    "poc": ("MODISA_L3m_POC", "MODISA_L3m_POC_NRT"),
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default="1998-01-01")
    parser.add_argument("--end", default="2026-08-01")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "data/raw")
    parser.add_argument("--force", action="store_true", help="reemplaza archivos existentes")
    parser.add_argument("--skip-cmems", action="store_true")
    parser.add_argument("--skip-occci", action="store_true")
    parser.add_argument("--skip-nasa", action="store_true")
    parser.add_argument("--skip-era5", action="store_true")
    parser.add_argument("--nasa-limit", type=int, default=0, help="0 = todos los granules encontrados")
    return parser.parse_args()


def _target(path: Path, force: bool) -> Path | None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size and not force:
        LOG.info("Existe, se conserva: %s", path)
        return None
    return path


def _bounds() -> dict[str, float]:
    return {
        "minimum_longitude": PERU_OCEAN.west,
        "maximum_longitude": PERU_OCEAN.east,
        "minimum_latitude": PERU_OCEAN.south,
        "maximum_latitude": PERU_OCEAN.north,
    }


def download_cmems(output: Path, start: str, end: str, force: bool) -> list[dict[str, Any]]:
    """Descarga BGC, física/corrientes y SSH en archivos separados."""
    records: list[dict[str, Any]] = []
    requests_to_make = [
        ("biogeochemistry_b.nc", CMEMS_BGC, ["chl", "no3", "po4", "o2", "phyc"]),
        ("physics_b.nc", CMEMS_PHY, ["thetao", "so"]),
        ("currents_b.nc", CMEMS_PHY, ["uo", "vo"]),
        ("ssh_b.nc", CMEMS_PHY, ["zos"]),
    ]
    for filename, dataset_id, variables in requests_to_make:
        path = _target(output / "copernicus" / filename, force)
        if path is None:
            continue
        LOG.info("CMEMS %s: %s", variables, dataset_id)
        try:
            request: dict[str, Any] = {
                "dataset_id": dataset_id,
                "variables": variables,
                "start_datetime": start,
                "end_datetime": end,
                "output_filename": str(path),
                **_bounds(),
            }
            if variables != ["zos"]:
                request.update(minimum_depth=0, maximum_depth=5)
            copernicusmarine.subset(**request)
            records.append({"source": "CMEMS", "dataset_id": dataset_id, "variables": variables, "path": str(path)})
        except Exception as exc:  # dataset catalogs can change independently
            path.unlink(missing_ok=True)
            LOG.error("CMEMS falló para %s: %s", variables, exc)
            records.append({"source": "CMEMS", "dataset_id": dataset_id, "variables": variables, "error": str(exc)})
    return records


def _erddap_variables(dataset_id: str) -> list[str]:
    url = f"{OCCCI_SERVER}/info/{dataset_id}/index.json"
    response = requests.get(url, timeout=90)
    response.raise_for_status()
    payload = response.json()
    rows = payload.get("table", {}).get("rows", [])
    columns = payload.get("table", {}).get("columnNames", [])
    return [row[columns.index("Variable Name")] for row in rows if "Variable Name" in columns]


def _find_erddap_dataset_and_variable(candidates: tuple[str, ...], patterns: tuple[str, ...]) -> tuple[str, str]:
    for dataset_id in candidates:
        try:
            variables = _erddap_variables(dataset_id)
        except requests.RequestException:
            continue
        for variable in variables:
            normalized = variable.lower().replace("_", "")
            if any(pattern in normalized for pattern in patterns):
                return dataset_id, variable
    raise RuntimeError(f"No se encontró producto ERDDAP para {candidates} con {patterns}")


def download_occci(output: Path, start: str, end: str, force: bool) -> list[dict[str, Any]]:
    """Descarga recortes OC-CCI; el servidor devuelve NetCDF vía ERDDAP."""
    from nasahackaton.sources.noaa import erddap_griddap_nc

    records: list[dict[str, Any]] = []
    products = [
        ("chlorophyll_occci.nc", (OCCCI_CHL,), ("chlor_a", "chlorophyll"), "chlor_a"),
        ("kd490_occci.nc", OCCCI_KD_CANDIDATES, ("kd490", "k490", "kd_490"), None),
    ]
    for filename, datasets, patterns, requested_variable in products:
        path = _target(output / "ocean_color" / filename, force)
        if path is None:
            continue
        try:
            dataset_id, variable = (
                (datasets[0], requested_variable)
                if requested_variable is not None
                else _find_erddap_dataset_and_variable(datasets, patterns)
            )
            ds = erddap_griddap_nc(
                OCCCI_SERVER,
                dataset_id,
                variable,
                time_start=start,
                time_end=end,
                lat_max=PERU_OCEAN.north,
                lat_min=PERU_OCEAN.south,
                lon_min=PERU_OCEAN.west,
                lon_max=PERU_OCEAN.east,
                lat_stride=10,
                lon_stride=10,
            )
            ds.to_netcdf(path)
            ds.close()
            records.append({"source": "OC-CCI/ERDDAP", "dataset_id": dataset_id, "variable": variable, "path": str(path)})
        except Exception as exc:
            path.unlink(missing_ok=True)
            LOG.error("OC-CCI falló para %s: %s", filename, exc)
            records.append({"source": "OC-CCI/ERDDAP", "file": filename, "error": str(exc)})
    return records


def download_nasa_ocean_color(output: Path, start: str, end: str, limit: int) -> list[dict[str, Any]]:
    """Busca y descarga composiciones NASA Ocean Color con Earthdata."""
    results: list[dict[str, Any]] = []
    earthaccess.login(persist=True)
    box = PERU_OCEAN.as_tuple()
    target_dir = output / "ocean_color" / "nasa"
    target_dir.mkdir(parents=True, exist_ok=True)
    for product, short_names in NASA_SHORT_NAMES.items():
        found = []
        selected_short_name = None
        for short_name in short_names:
            found = earthaccess.search_data(
                short_name=short_name,
                bounding_box=box,
                temporal=(start, end),
            )
            if found:
                selected_short_name = short_name
                break
        if not found:
            LOG.error("NASA Ocean Color: no se encontraron granules para %s", product)
            results.append({"source": "NASA Ocean Color", "product": product, "error": "sin resultados"})
            continue
        selected = found if limit == 0 else found[:limit]
        paths = earthaccess.download(selected, str(target_dir))
        results.append({
            "source": "NASA Ocean Color",
            "product": product,
            "short_name": selected_short_name,
            "granules": len(paths),
            "path": str(target_dir),
        })
        LOG.info("NASA %s: %s granules descargados", product, len(paths))
    return results


def download_era5(output: Path, start: str, end: str, force: bool) -> list[dict[str, Any]]:
    """Descarga viento mensual ERA5 para la caja peruana."""
    import cdsapi

    path = _target(output / "era5" / "wind_monthly.nc", force)
    if path is None:
        return []
    dates = pd.date_range(start, end, freq="MS")
    request = {
        "product_type": "monthly_averaged_reanalysis",
        "variable": ["10m_u_component_of_wind", "10m_v_component_of_wind"],
        "year": sorted({str(date.year) for date in dates}),
        "month": [f"{month:02d}" for month in sorted({date.month for date in dates})],
        "time": "00:00",
        "data_format": "netcdf",
        "area": [PERU_OCEAN.north, PERU_OCEAN.west, PERU_OCEAN.south, PERU_OCEAN.east],
    }
    LOG.info("ERA5: solicitando viento mensual")
    try:
        cdsapi.Client().retrieve("reanalysis-era5-single-levels-monthly-means", request, str(path))
        return [{"source": "ERA5/CDS", "dataset_id": "reanalysis-era5-single-levels-monthly-means", "path": str(path)}]
    except Exception as exc:
        path.unlink(missing_ok=True)
        LOG.error("ERA5 falló: %s", exc)
        return [{"source": "ERA5/CDS", "error": str(exc)}]


def main() -> None:
    args = _parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args.output.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, Any]] = []
    if not args.skip_cmems:
        manifest.extend(download_cmems(args.output, args.start, args.end, args.force))
    if not args.skip_occci:
        manifest.extend(download_occci(args.output, args.start, args.end, args.force))
    if not args.skip_nasa:
        manifest.extend(download_nasa_ocean_color(args.output, args.start, args.end, args.nasa_limit))
    if not args.skip_era5:
        manifest.extend(download_era5(args.output, args.start, args.end, args.force))
    manifest_path = args.output / "experiment_b_download_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    errors = sum("error" in item for item in manifest)
    LOG.info("Manifest guardado en %s; errores: %d", manifest_path, errors)
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

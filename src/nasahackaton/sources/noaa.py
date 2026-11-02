"""Clientes HTTP/ERDDAP para índices y campos NOAA (PDO, WOA, ocean colour)."""

from __future__ import annotations

import io
import re
from pathlib import Path

import pandas as pd
import requests
import xarray as xr

PDO_ERDDAP_CSV = (
    "https://oceanview.pfeg.noaa.gov/erddap/tabledap/cciea_OC_PDO.csv"
)
PDO_PSL_ASCII = "https://psl.noaa.gov/pdo/data/pdo.timeseries.ersstv5.data"

WOA23_HTTP = "https://www.ncei.noaa.gov/data/oceans/woa/WOA23/DATA"
# Códigos WOA: n=nitrato, p=fosfato, i=silicato; MM=00 anual, 01–12 mensual.
WOA_VARS = {
    "nitrate": ("nitrate", "n", "n_an"),
    "phosphate": ("phosphate", "p", "p_an"),
    "silicate": ("silicate", "i", "i_an"),
}

DEFAULT_TIMEOUT = 90


def fetch_pdo(
    start: str | None = None,
    end: str | None = None,
    *,
    source: str = "erddap",
) -> pd.Series:
    """Índice PDO mensual (NOAA).

    ``source='erddap'`` usa el tabledap CCIEA en oceanview (CSV).
    ``source='psl'`` parsea el ASCII ERSSTv5 de NOAA PSL.
    """
    if source == "psl":
        series = _pdo_from_psl()
    else:
        series = _pdo_from_erddap(start=start, end=end)
    if start is not None:
        series = series[series.index >= pd.Timestamp(start)]
    if end is not None:
        series = series[series.index <= pd.Timestamp(end)]
    return series.rename("PDO")


def _pdo_from_erddap(
    start: str | None = None,
    end: str | None = None,
) -> pd.Series:
    params = ["time", "PDO"]
    query = ",".join(params)
    constraints: list[str] = []
    if start:
        constraints.append(f"&time>={pd.Timestamp(start).strftime('%Y-%m-%d')}")
    if end:
        constraints.append(f"&time<={pd.Timestamp(end).strftime('%Y-%m-%d')}")
    url = f"{PDO_ERDDAP_CSV}?{query}{''.join(constraints)}"
    response = requests.get(url, timeout=DEFAULT_TIMEOUT)
    response.raise_for_status()
    frame = pd.read_csv(io.StringIO(response.text), skiprows=[1])
    frame["time"] = pd.to_datetime(frame["time"], utc=True).dt.tz_localize(None)
    return frame.set_index("time")["PDO"].astype(float).sort_index()


def _pdo_from_psl() -> pd.Series:
    response = requests.get(PDO_PSL_ASCII, timeout=DEFAULT_TIMEOUT)
    response.raise_for_status()
    rows: list[tuple[pd.Timestamp, float]] = []
    for line in response.text.splitlines():
        parts = line.split()
        if len(parts) < 13:
            continue
        if not re.fullmatch(r"\d{4}", parts[0]):
            continue
        year = int(parts[0])
        for month, raw in enumerate(parts[1:13], start=1):
            value = float(raw)
            # PSL rellena faltantes con valores extremos tipo -99.99
            if value < -90:
                continue
            rows.append((pd.Timestamp(year=year, month=month, day=1), value))
    if not rows:
        raise ValueError("No se pudieron parsear valores PDO del ASCII PSL")
    return pd.Series(dict(rows), dtype=float).sort_index()


def erddap_griddap_nc(
    server: str,
    dataset_id: str,
    variable: str,
    *,
    time_start: str,
    time_end: str,
    lat_max: float,
    lat_min: float,
    lon_min: float,
    lon_max: float,
    lat_stride: int = 10,
    lon_stride: int = 10,
    timeout: int = DEFAULT_TIMEOUT,
) -> xr.Dataset:
    """Descarga un recorte NetCDF vía ERDDAP griddap (lat descendente típica)."""
    base = server.rstrip("/")
    # Muchos productos ocean colour usan longitud 0–360.
    if lon_min < 0 and lon_max < 0:
        lon0, lon1 = lon_min + 360.0, lon_max + 360.0
    else:
        lon0, lon1 = lon_min, lon_max
    t0 = pd.Timestamp(time_start).strftime("%Y-%m-%dT12:00:00Z")
    t1 = pd.Timestamp(time_end).strftime("%Y-%m-%dT12:00:00Z")
    query = (
        f"{variable}"
        f"[({t0}):1:({t1})]"
        f"[({lat_max}):{lat_stride}:({lat_min})]"
        f"[({lon0}):{lon_stride}:({lon1})]"
    )
    url = f"{base}/griddap/{dataset_id}.nc?{query}"
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return xr.open_dataset(io.BytesIO(response.content))


def woa23_monthly_path(
    nutrient: str,
    month: int,
    cache_dir: Path,
) -> Path:
    """Ruta local cacheada del NetCDF mensual WOA23 (1°)."""
    if nutrient not in WOA_VARS:
        raise KeyError(f"Nutriente desconocido: {nutrient}")
    if not 1 <= month <= 12:
        raise ValueError("month debe estar entre 1 y 12")
    folder, code, _ = WOA_VARS[nutrient]
    name = f"woa23_all_{code}{month:02d}_01.nc"
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    target = cache_dir / name
    if target.exists() and target.stat().st_size > 0:
        return target
    url = f"{WOA23_HTTP}/{folder}/netcdf/all/1.00/{name}"
    response = requests.get(url, timeout=DEFAULT_TIMEOUT)
    response.raise_for_status()
    target.write_bytes(response.content)
    return target


def woa23_box_mean(
    nutrient: str,
    month: int,
    *,
    south: float,
    north: float,
    west: float,
    east: float,
    cache_dir: Path,
    depth_m: float = 0.0,
) -> float:
    """Media espacial de la climatología WOA23 (micromol/kg) en una caja."""
    path = woa23_monthly_path(nutrient, month, cache_dir)
    _, _, var_name = WOA_VARS[nutrient]
    with xr.open_dataset(path, decode_times=False) as ds:
        field = ds[var_name]
        if "depth" in field.dims:
            field = field.sel(depth=depth_m, method="nearest")
        if "time" in field.dims:
            field = field.isel(time=0)
        box = field.sel(lat=slice(south, north), lon=slice(west, east))
        return float(box.mean(skipna=True).load())

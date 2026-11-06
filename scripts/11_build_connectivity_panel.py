"""Construye un panel mensual regional a partir de las descargas CMEMS."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

from nasahackaton.config import CONNECTIVITY_REGIONS


BANDS = {
    "surface_0_5m": (0.0, 5.0),
    "subsurface_100_200m": (100.0, 200.0),
    "intermediate_200_500m": (200.0, 500.0),
    "deep_reference_500_1000m": (500.0, 1000.0),
}


def _reduce_spatial(da: xr.DataArray) -> xr.DataArray:
    dims = [name for name in ("latitude", "longitude", "lat", "lon") if name in da.dims]
    return da.median(dim=dims, skipna=True) if dims else da


def _read_file(path: Path, region: str, kind: str) -> pd.DataFrame:
    # No cargar el NetCDF completo: los archivos 3-D pueden pesar varios GB.
    # Se reduce primero por profundidad y espacio, y solo se carga la serie
    # temporal regional resultante.
    with xr.open_dataset(path) as ds:
        rows: list[pd.DataFrame] = []
        for name, da in ds.data_vars.items():
            if "time" not in da.dims:
                continue
            if "depth" not in da.dims:
                reduced = _reduce_spatial(da).load().to_series()
                frame = reduced.rename(name).to_frame()
                frame["depth_band"] = "surface_2d"
                rows.append(frame)
                continue
            for band, (minimum, maximum) in BANDS.items():
                selected = da.sel(depth=slice(minimum, maximum))
                if selected.sizes.get("depth", 0) == 0:
                    continue
                reduced = _reduce_spatial(selected.mean("depth", skipna=True)).load().to_series()
                frame = reduced.rename(name).to_frame()
                frame["depth_band"] = band
                rows.append(frame)
    if not rows:
        return pd.DataFrame()
    result = pd.concat(rows, axis=0).reset_index(names="date")
    result["date"] = pd.to_datetime(result["date"]).dt.to_period("M").dt.to_timestamp()
    result["region"] = region
    result["source_kind"] = kind
    return result


def _merge_region(region_dir: Path, region: str, legacy_peru_dir: Path | None = None) -> pd.DataFrame:
    frames = []
    for filename, kind in (
        ("physics_3d_monthly.nc", "cmems_physics_3d"),
        ("physics_surface_monthly.nc", "cmems_physics_surface"),
        ("biogeochemistry_monthly.nc", "cmems_biogeochemistry"),
    ):
        path = region_dir / filename
        if not path.exists() and region == "peru_humboldt" and legacy_peru_dir is not None:
            legacy_names = {
                "physics_3d_monthly.nc": "physics_b.nc",
                "physics_surface_monthly.nc": "ssh_b.nc",
                "biogeochemistry_monthly.nc": "biogeochemistry_b.nc",
            }
            path = legacy_peru_dir / legacy_names[filename]
        if path.exists():
            frames.append(_read_file(path, region, kind))
    if not frames:
        return pd.DataFrame()
    combined = pd.concat(frames, ignore_index=True)
    value_columns = [c for c in combined.columns if c not in {"date", "depth_band", "region", "source_kind"}]
    keys = ["date", "region", "depth_band"]
    values = combined.groupby(keys, as_index=False)[value_columns].first()
    provenance = combined.groupby(keys, as_index=False)["source_kind"].agg(
        lambda values: "|".join(sorted(set(values.dropna())))
    )
    return values.merge(provenance, on=keys, how="left")


def _add_anomalies(panel: pd.DataFrame) -> pd.DataFrame:
    value_columns = [c for c in panel.columns if c not in {"date", "region", "depth_band"}]
    value_columns = [c for c in value_columns if pd.api.types.is_numeric_dtype(panel[c])]
    for column in value_columns:
        climatology = panel.groupby(["region", "depth_band", panel["date"].dt.month])[column].transform("mean")
        panel[f"{column}_anom"] = panel[column] - climatology
    return panel


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/raw/connectivity"))
    parser.add_argument(
        "--legacy-peru-input",
        type=Path,
        default=Path("data/raw/copernicus"),
        help="Usa los NetCDF peruanos existentes como fallback explícito para peru_humboldt.",
    )
    parser.add_argument("--output", type=Path, default=Path("data/processed/tables/connectivity_panel_monthly.csv"))
    args = parser.parse_args()

    frames = [_merge_region(args.input / region, region, args.legacy_peru_input) for region in CONNECTIVITY_REGIONS]
    panel = pd.concat([frame for frame in frames if not frame.empty], ignore_index=True)
    if panel.empty:
        raise SystemExit("No hay NetCDF regionales disponibles; ejecuta 07_download_connectivity.py primero.")
    panel = _add_anomalies(panel.sort_values(["region", "depth_band", "date"]).reset_index(drop=True))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    panel.to_csv(args.output, index=False)
    print(f"Panel: {args.output} ({len(panel)} filas, {len(panel.columns)} columnas)")


if __name__ == "__main__":
    main()

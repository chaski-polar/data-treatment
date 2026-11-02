"""Acceso a datos de fitoplancton (carbono) desde Copernicus Marine Data Store.

Dataset: cmems_mod_glo_bgc-pft_anfc_0.25deg_P1D-m
Variable: phyc (Total Phytoplankton Carbon) en mmol C/m³
Resolución: 0.25° (~27 km), diario
"""

from __future__ import annotations

from pathlib import Path

import copernicusmarine
import numpy as np
import pandas as pd
import xarray as xr

from nasahackaton.config import BoundingBox, PERU_OCEAN

# Conversión: mmol C/m³ → mg C/m³
# Masa molar del carbono = 12.01 g/mol
MMOL_TO_MG_C = 12.01


def load_phytoplankton_carbon_copernicus(
    start: str = "2026-10-01",
    end: str = "2026-10-31",
    box: BoundingBox = PERU_OCEAN,
    *,
    depth_m: float = 0.5,
    method: str = "subset",
) -> xr.DataArray:
    """Carga carbono de fitoplancton (phyc) de Copernicus Marine.

    Args:
        start: Fecha inicio (YYYY-MM-DD)
        end: Fecha fin (YYYY-MM-DD)
        box: Caja geográfica
        depth_m: Profundidad en metros (superficie ~0.5)
        method: 'subset' (descarga NetCDF) o 'open_dataset' (lazy loading)

    Returns:
        DataArray con phyc en mmol C/m³
    """
    if method == "subset":
        output_path = Path("data") / f"phytoplankton_carbon_{start}_{end}.nc"
        copernicusmarine.subset(
            dataset_id="cmems_mod_glo_bgc-pft_anfc_0.25deg_P1D-m",
            variables=["phyc"],
            start_datetime=f"{start}T00:00:00",
            end_datetime=f"{end}T23:59:59",
            minimum_longitude=box.west,
            maximum_longitude=box.east,
            minimum_latitude=box.south,
            maximum_latitude=box.north,
            minimum_depth=depth_m,
            maximum_depth=depth_m,
            output_filename=str(output_path),
        )
        ds = xr.open_dataset(output_path)
        return ds["phyc"]

    else:  # open_dataset
        ds = copernicusmarine.open_dataset(
            dataset_id="cmems_mod_glo_bgc-pft_anfc_0.25deg_P1D-m"
        )
        phyc = ds["phyc"].sel(
            time=slice(start, end),
            longitude=slice(box.west, box.east),
            latitude=slice(box.south, box.north),
        )
        phyc_surface = phyc.sel(depth=depth_m, method="nearest")
        return phyc_surface


def phytoplankton_carbon_to_mg_c(phyc_mmol: xr.DataArray | np.ndarray) -> xr.DataArray | np.ndarray:
    """Convierte mmol C/m³ a mg C/m³."""
    return phyc_mmol * MMOL_TO_MG_C


def phytoplankton_carbon_timeseries(
    start: str = "2026-10-01",
    end: str = "2026-10-31",
    box: BoundingBox = PERU_OCEAN,
    *,
    aggregation: str = "median",
) -> pd.Series:
    """Serie temporal mensual de carbono de fitoplancton (mg C/m³).

    Args:
        aggregation: 'median', 'mean', o 'max' para agregación espacial

    Returns:
        Serie temporal con índice de fechas
    """
    phyc = load_phytoplankton_carbon_copernicus(start, end, box, method="open_dataset")
    phyc_mg = phytoplankton_carbon_to_mg_c(phyc)

    if aggregation == "median":
        values = phyc_mg.median(dim=("latitude", "longitude"), skipna=True)
    elif aggregation == "mean":
        values = phyc_mg.mean(dim=("latitude", "longitude"), skipna=True)
    elif aggregation == "max":
        values = phyc_mg.max(dim=("latitude", "longitude"), skipna=True)
    else:
        raise ValueError(f"aggregation debe ser 'median', 'mean' o 'max', got {aggregation}")

    series = values.to_series()
    series.index = pd.to_datetime(series.index).to_period("D").to_timestamp()
    return series.rename("phyto_carbon_mg_m3")


def main() -> None:
    """Prueba rápida de la API."""
    print("Probando subset (descarga)...")
    phyc = load_phytoplankton_carbon_copernicus(
        "2026-10-20", "2026-10-25", method="subset"
    )
    print(f"Shape: {phyc.shape}")
    print(f"Rango mmol/m³: {float(phyc.min()):.2f} - {float(phyc.max()):.2f}")
    print(f"Rango mg C/m³: {float(phytoplankton_carbon_to_mg_c(phyc).min()):.2f} - {float(phytoplankton_carbon_to_mg_c(phyc).max()):.2f}")

    print("\nProbando open_dataset (lazy loading)...")
    series = phytoplankton_carbon_timeseries("2026-10-20", "2026-10-25")
    print(series)


if __name__ == "__main__":
    main()

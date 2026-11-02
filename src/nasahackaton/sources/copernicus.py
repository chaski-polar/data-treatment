"""Acceso canónico a los reanálisis históricos de Copernicus Marine.

La investigación histórica usa productos ``*_my_*`` (multiyear/reanalysis).
Los productos ``*_anfc_*`` son operativos y no deben mezclarse con la serie
histórica sin documentar el cambio de producto.
"""

from __future__ import annotations

from pathlib import Path

import copernicusmarine
import xarray as xr

from nasahackaton.config import BoundingBox, PERU_OCEAN, PROJECT_ROOT

PHYSICS_MONTHLY = "cmems_mod_glo_phy_my_0.083deg_P1M-m"
BIOGEOCHEMISTRY_MONTHLY = "cmems_mod_glo_bgc_my_0.25deg_P1M-m"
PHYSICS_DAILY = "cmems_mod_glo_phy_my_0.083deg_P1D-m"
BIOGEOCHEMISTRY_DAILY = "cmems_mod_glo_bgc_my_0.25deg_P1D-m"


def _bounds(box: BoundingBox) -> dict[str, float]:
    return {
        "minimum_longitude": box.west,
        "maximum_longitude": box.east,
        "minimum_latitude": box.south,
        "maximum_latitude": box.north,
    }


def open_monthly_ocean(
    start: str,
    end: str,
    *,
    box: BoundingBox = PERU_OCEAN,
    physics: tuple[str, ...] = ("thetao", "so"),
    biogeochemistry: tuple[str, ...] = ("chl", "no3", "po4", "si", "o2", "phyc"),
    surface_depth: tuple[float, float] = (0.0, 5.0),
) -> xr.Dataset:
    """Abre una extracción lazy y la combina en una sola tabla espacial."""
    common = {
        **_bounds(box),
        "start_datetime": start,
        "end_datetime": end,
        "minimum_depth": surface_depth[0],
        "maximum_depth": surface_depth[1],
    }
    datasets = []
    if physics:
        datasets.append(
            copernicusmarine.open_dataset(
                dataset_id=PHYSICS_MONTHLY,
                variables=list(physics),
                **common,
            )
        )
    if biogeochemistry:
        datasets.append(
            copernicusmarine.open_dataset(
                dataset_id=BIOGEOCHEMISTRY_MONTHLY,
                variables=list(biogeochemistry),
                **common,
            )
        )
    if not datasets:
        raise ValueError("Debe solicitar al menos una variable")
    return xr.merge(datasets, compat="override")


def subset_monthly_ocean(
    start: str,
    end: str,
    *,
    output_path: Path | None = None,
    box: BoundingBox = PERU_OCEAN,
    variables: tuple[str, ...] = ("thetao", "so"),
    surface_depth: tuple[float, float] = (0.0, 5.0),
) -> Path:
    """Descarga un subconjunto mensual NetCDF para conservarlo en ``data/raw``."""
    target = output_path or PROJECT_ROOT / "data" / "raw" / "copernicus" / f"ocean_{start}_{end}.nc"
    target.parent.mkdir(parents=True, exist_ok=True)
    physics_names = {"thetao", "so"}
    if set(variables) & physics_names and set(variables) - physics_names:
        raise ValueError(
            "Copernicus subset recibe un producto por solicitud; "
            "separa variables físicas y biogeoquímicas antes de descargar."
        )
    dataset_id = PHYSICS_MONTHLY if set(variables) <= physics_names else BIOGEOCHEMISTRY_MONTHLY
    copernicusmarine.subset(
        dataset_id=dataset_id,
        variables=list(variables),
        **_bounds(box),
        start_datetime=start,
        end_datetime=end,
        minimum_depth=surface_depth[0],
        maximum_depth=surface_depth[1],
        output_filename=str(target),
    )
    return target


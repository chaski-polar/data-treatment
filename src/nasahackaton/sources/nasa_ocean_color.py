"""Descarga y lectura de productos NASA Ocean Color."""

from __future__ import annotations

from pathlib import Path

import earthaccess
import xarray as xr

from nasahackaton.config import BoundingBox, PERU_OCEAN, PROJECT_ROOT

MODIS_CHL = "MODISA_L3m_CHL"


def search_modis_chlorophyll(
    start: str,
    end: str,
    *,
    box: BoundingBox = PERU_OCEAN,
) -> list:
    """Busca composiciones MODIS-Aqua de clorofila-a."""
    earthaccess.login(persist=True)
    return earthaccess.search_data(
        short_name=MODIS_CHL,
        temporal=(start, end),
        bounding_box=box.as_tuple(),
    )


def load_local_chlorophyll(
    data_dir: Path | str = PROJECT_ROOT / "data_chl",
    *,
    box: BoundingBox = PERU_OCEAN,
) -> xr.DataArray:
    """Carga archivos L3 mensuales locales y los concatena por tiempo."""
    paths = sorted(Path(data_dir).glob("AQUA_MODIS.*.nc"))
    if not paths:
        raise FileNotFoundError(f"No hay archivos MODIS en {data_dir}")
    arrays = []
    for path in paths:
        with xr.open_dataset(path) as dataset:
            data = dataset["chlor_a"].sortby("lat").sel(
                lat=slice(box.south, box.north),
                lon=slice(box.west, box.east),
            ).load()
        date = path.name.split(".")[1][:8]
        arrays.append(data.expand_dims(time=[date]))
    return xr.concat(arrays, dim="time").rename("chlorophyll_a")


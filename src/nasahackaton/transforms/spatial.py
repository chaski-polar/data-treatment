"""Agregaciones espaciales explícitas para productos gridded."""

from __future__ import annotations

import xarray as xr


def surface(data: xr.DataArray, maximum_depth: float = 5.0) -> xr.DataArray:
    """Selecciona la capa más superficial o promedia hasta ``maximum_depth``."""
    if "depth" not in data.dims:
        return data
    return data.sel(depth=slice(0, maximum_depth)).mean("depth", skipna=True)


def spatial_series(data: xr.DataArray, method: str = "median") -> xr.DataArray:
    """Reduce latitud/longitud conservando el eje temporal."""
    dimensions = [d for d in ("latitude", "longitude", "lat", "lon") if d in data.dims]
    if not dimensions:
        return data
    if method == "mean":
        return data.mean(dimensions, skipna=True)
    if method == "median":
        return data.median(dimensions, skipna=True)
    raise ValueError("method debe ser 'mean' o 'median'")


"""Compatibilidad con las funciones históricas del proyecto.

Los nuevos experimentos deben importar desde ``sources`` y ``analysis``.
"""

from __future__ import annotations

from pathlib import Path

from nasahackaton.analysis.raster import (
    inspect_water_files as open_with_rasterio,
    water_coverage as _analyze_water_coverage,
    water_files as _extract_water_files,
    plot_water_layer as _plot_raster_data,
)
from nasahackaton.sources.earthdata import download_dswx as download_earthaccess_data
from nasahackaton.sources.power import fetch_daily


def power(lat: float, lon: float, start: str, end: str, params: str = "RH2M,PRECTOTCORR,T2M,WS2M"):
    """Alias histórico de :func:`nasahackaton.sources.power.fetch_daily`."""
    return fetch_daily(lat, lon, start, end, params)


def main() -> None:
    files = sorted(Path("data").glob("*.tif"))
    print(f"Archivos totales: {len(files)}")
    open_with_rasterio(files)


if __name__ == "__main__":
    main()

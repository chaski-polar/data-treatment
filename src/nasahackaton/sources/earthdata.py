"""Consultas y descargas de productos NASA mediante Earthaccess."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import earthaccess


def login() -> None:
    """Inicia sesión usando la configuración persistida de Earthdata."""
    earthaccess.login(persist=True)


def search_nisar(
    bounding_box: tuple[float, float, float, float],
    temporal: tuple[str, str],
    short_name: str = "NISAR_L2_GCOV_PROVISIONAL_V1",
) -> list[Any]:
    """Busca granules NISAR para una caja y periodo."""
    return earthaccess.search_data(
        short_name=short_name,
        bounding_box=bounding_box,
        temporal=temporal,
    )


def download_dswx(
    bounding_box: tuple[float, float, float, float],
    temporal: tuple[str, str],
    output_dir: str | Path = "data",
    limit: int = 3,
) -> Any:
    """Descarga una muestra del producto OPERA DSWx-S1."""
    login()
    results = earthaccess.search_data(
        short_name="OPERA_L3_DSWX-S1_V1",
        bounding_box=bounding_box,
        temporal=temporal,
    )
    return earthaccess.download(results[:limit], str(output_dir))

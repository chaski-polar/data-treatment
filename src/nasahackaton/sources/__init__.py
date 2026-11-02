"""Clientes y adaptadores para fuentes externas de datos.

Los símbolos se importan de forma perezosa para que leer FAO no obligue a
instalar xarray, Earthaccess o Copernicus.
"""

__all__ = [
    "fetch_daily",
    "fetch_pdo",
    "woa23_box_mean",
    "open_monthly_ocean",
    "load_local_chlorophyll",
]


def __getattr__(name: str):
    if name in {"fetch_pdo", "woa23_box_mean"}:
        from nasahackaton.sources.noaa import fetch_pdo, woa23_box_mean

        return {"fetch_pdo": fetch_pdo, "woa23_box_mean": woa23_box_mean}[name]
    if name == "fetch_daily":
        from nasahackaton.sources.power import fetch_daily

        return fetch_daily
    if name == "open_monthly_ocean":
        from nasahackaton.sources.copernicus import open_monthly_ocean

        return open_monthly_ocean
    if name == "load_local_chlorophyll":
        from nasahackaton.sources.nasa_ocean_color import load_local_chlorophyll

        return load_local_chlorophyll
    raise AttributeError(name)

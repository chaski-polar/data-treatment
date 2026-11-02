"""Clientes y adaptadores para fuentes externas de datos."""

from nasahackaton.sources.noaa import fetch_pdo, woa23_box_mean
from nasahackaton.sources.power import fetch_daily

__all__ = ["fetch_daily", "fetch_pdo", "woa23_box_mean"]

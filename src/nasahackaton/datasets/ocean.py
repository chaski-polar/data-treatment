"""Conversión de datasets xarray a series mensuales del panel."""

from __future__ import annotations

import pandas as pd
import xarray as xr

from nasahackaton.transforms.spatial import spatial_series, surface
from nasahackaton.transforms.temporal import monthly_index
from nasahackaton.transforms.units import phytoplankton_carbon_mmol_to_mg


VARIABLE_NAMES = {
    "thetao": "sst",
    "so": "sss",
    "o2": "oxygen",
    "no3": "nitrate",
    "po4": "phosphate",
    "si": "silicate",
    "chl": "chlorophyll_a",
    "phyc": "phytoplankton_carbon",
}


def monthly_ocean_frame(dataset: xr.Dataset, *, aggregation: str = "median") -> pd.DataFrame:
    """Agrega la superficie y la caja espacial a una tabla mensual."""
    columns: dict[str, pd.Series] = {}
    for source_name, output_name in VARIABLE_NAMES.items():
        if source_name not in dataset:
            continue
        data = spatial_series(surface(dataset[source_name]), method=aggregation)
        series = data.to_series()
        if source_name == "phyc":
            series = phytoplankton_carbon_mmol_to_mg(series)
        columns[output_name] = series
    if not columns:
        raise ValueError("El dataset no contiene variables oceanográficas reconocidas")
    frame = monthly_index(pd.DataFrame(columns))
    return frame.groupby(level=0).mean(numeric_only=True)


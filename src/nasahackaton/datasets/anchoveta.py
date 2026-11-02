"""Variables observadas de anchoveta para unir al panel mensual."""

from __future__ import annotations

import pandas as pd

from nasahackaton.sources.fao import load_peru_anchoveta_capture


def annual_capture_frame(path: str = "fao_data/Global_production_quantity.csv") -> pd.DataFrame:
    """Carga captura anual sin inventar una desagregación mensual."""
    data = load_peru_anchoveta_capture(path).set_index("year")
    data.index = pd.to_datetime(data.index.astype(str) + "-01-01")
    return data


"""Lectura de producción pesquera FAO ya descargada."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_peru_anchoveta_capture(
    path: Path | str = "fao_data/Global_production_quantity.csv",
) -> pd.DataFrame:
    """Devuelve captura anual peruana de *Engraulis ringens*.

    La captura se conserva como respuesta separada: no se convierte
    automáticamente en biomasa.
    """
    frame = pd.read_csv(path)
    mask = (
        frame["COUNTRY.UN_CODE"].astype(str).str.contains("604")
        & frame["SPECIES.ALPHA_3_CODE"].eq("VET")
    )
    return (
        frame.loc[mask, ["PERIOD", "VALUE"]]
        .rename(columns={"PERIOD": "year", "VALUE": "capture_t"})
        .assign(year=lambda data: data["year"].astype(int))
        .sort_values("year")
        .reset_index(drop=True)
    )


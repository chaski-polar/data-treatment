"""Construcción y validación del panel mensual común a A, B y C."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from nasahackaton.transforms.temporal import add_lags, monthly_index


PANEL_COLUMNS = [
    "sst", "sss", "oxygen", "nitrate", "phosphate", "silicate",
    "chlorophyll_a", "phytoplankton_carbon", "zooplankton",
    "biomass_anchoveta", "capture_t", "oni", "pdo", "sam",
    "distance_coast",
]


def build_monthly_panel(*frames: pd.DataFrame, lags: tuple[int, ...] = (1, 2, 3, 6)) -> pd.DataFrame:
    """Une tablas por fecha sin rellenar artificialmente los datos faltantes."""
    if not frames:
        raise ValueError("Se necesita al menos una tabla")
    panel = frames[0].copy()
    for frame in frames[1:]:
        panel = panel.join(frame, how="outer", rsuffix="_duplicate")
    panel = monthly_index(panel)
    duplicated = [column for column in panel if column.endswith("_duplicate")]
    if duplicated:
        raise ValueError(f"Columnas duplicadas: {duplicated}")
    lagged = [column for column in ("chlorophyll_a", "phytoplankton_carbon", "nitrate", "phosphate") if column in panel]
    return add_lags(panel, lagged, lags=lags)


def save_panel(panel: pd.DataFrame, path: Path | str) -> Path:
    """Guarda el panel en Parquet o CSV según la extensión."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.suffix == ".parquet":
        panel.to_parquet(target)
    else:
        panel.to_csv(target, index=True, index_label="date")
    return target


def load_panel(path: Path | str) -> pd.DataFrame:
    """Carga un panel Parquet o CSV conservando el índice temporal."""
    target = Path(path)
    if target.suffix == ".parquet":
        return pd.read_parquet(target)
    return pd.read_csv(target, index_col="date", parse_dates=True)


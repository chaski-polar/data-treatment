"""Alineación temporal y variables rezagadas."""

from __future__ import annotations

import pandas as pd


def monthly_index(frame: pd.DataFrame) -> pd.DataFrame:
    """Normaliza el índice a comienzos de mes y ordena la tabla."""
    result = frame.copy()
    result.index = pd.to_datetime(result.index).to_period("M").to_timestamp()
    return result.sort_index()


def add_lags(frame: pd.DataFrame, columns: list[str], lags: tuple[int, ...] = (1, 2, 3, 6)) -> pd.DataFrame:
    """Añade rezagos mensuales sin interpolar datos faltantes."""
    result = frame.copy()
    for column in columns:
        if column not in result:
            continue
        for lag in lags:
            result[f"{column}_lag_{lag}"] = result[column].shift(lag)
    return result


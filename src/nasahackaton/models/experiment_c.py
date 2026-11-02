"""Experimento C: preparación para el modelo dinámico F-Z-A."""

from __future__ import annotations

import pandas as pd


STATE_VARIABLES = ["phytoplankton_carbon", "zooplankton", "biomass_anchoveta"]


def validate_state_panel(frame: pd.DataFrame) -> pd.DataFrame:
    """Devuelve las observaciones completas necesarias para calibrar F-Z-A."""
    missing = [column for column in STATE_VARIABLES if column not in frame]
    if missing:
        raise ValueError(f"Faltan estados para Experimento C: {', '.join(missing)}")
    result = frame[STATE_VARIABLES].dropna().copy()
    if len(result) < 24:
        raise ValueError("Experimento C necesita al menos 24 observaciones temporales")
    return result


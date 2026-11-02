"""Conversiones de unidades con nombres explícitos."""

from __future__ import annotations

import pandas as pd


def phytoplankton_carbon_mmol_to_mg(values: pd.Series) -> pd.Series:
    """Convierte mmol C/m³ a mg C/m³ usando la masa molar del carbono."""
    return values.astype(float) * 12.011


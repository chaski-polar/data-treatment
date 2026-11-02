"""Experimento B: contribución de productividad y fitoplancton."""

from __future__ import annotations

from typing import Any

import pandas as pd

from nasahackaton.models.experiment_a import fit_quadratic_baseline


PRODUCTIVITY_VARIABLES = ["chlorophyll_a", "nitrate", "phosphate", "phytoplankton_carbon"]


def fit_productivity_model(frame: pd.DataFrame, response: str = "biomass_anchoveta") -> dict[str, Any]:
    """Ajusta la misma base A incorporando predictores de productividad."""
    available = [name for name in PRODUCTIVITY_VARIABLES if name in frame]
    if not available:
        raise ValueError("No hay variables de productividad en el panel")
    # La implementación inicial conserva el ajuste reproducible de A; el GAM
    # Tweedie se añadirá cuando el panel real tenga cobertura suficiente.
    result = fit_quadratic_baseline(frame, response=response)
    result["model"] = "quadratic_productivity_placeholder"
    result["productivity_variables"] = available
    return result


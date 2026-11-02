"""Experimento A: línea base abiótica estimable desde datos reales."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


BASE_VARIABLES = ["sst", "sss", "oxygen", "distance_coast", "oni"]


def fit_quadratic_baseline(frame: pd.DataFrame, response: str = "biomass_anchoveta") -> dict[str, Any]:
    """Ajusta una línea base transparente; reemplazable luego por GAM Tweedie."""
    required = [response, *BASE_VARIABLES]
    data = frame.dropna(subset=required)
    if len(data) < 20:
        raise ValueError("No hay suficientes observaciones para Experimento A")
    x = data[BASE_VARIABLES].to_numpy(float)
    mean = x.mean(axis=0)
    std = x.std(axis=0)
    if np.any(std == 0):
        raise ValueError("Una variable de Experimento A no tiene variación")
    z = (x - mean) / std
    design = np.column_stack([np.ones(len(z)), z, z**2])
    y = data[response].to_numpy(float)
    coefficients, *_ = np.linalg.lstsq(design, y, rcond=None)
    prediction = design @ coefficients
    return {
        "model": "quadratic_baseline",
        "response": response,
        "variables": BASE_VARIABLES,
        "means": dict(zip(BASE_VARIABLES, mean)),
        "std": dict(zip(BASE_VARIABLES, std)),
        "coefficients": coefficients.tolist(),
        "n": len(data),
        "rmse": float(np.sqrt(np.mean((y - prediction) ** 2))),
    }


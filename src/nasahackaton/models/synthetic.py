"""Datos sintéticos únicamente para pruebas de código.

Nunca usar estas funciones para estimar resultados científicos.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def monthly_demo(start: str = "1998-01-01", end: str = "2024-12-01") -> pd.DataFrame:
    """Genera un panel artificial pequeño para probar los modelos."""
    index = pd.date_range(start, end, freq="MS")
    rng = np.random.default_rng(42)
    return pd.DataFrame(
        {
            "sst": 18.3 + 2 * np.sin(2 * np.pi * index.month / 12) + rng.normal(0, 0.2, len(index)),
            "sss": 34.83 + rng.normal(0, 0.2, len(index)),
            "oxygen": 6.0 + rng.normal(0, 0.4, len(index)),
            "distance_coast": 80.0 + rng.normal(0, 10.0, len(index)),
            "chlorophyll_a": 3.7 + rng.normal(0, 1.0, len(index)),
            "oni": rng.normal(0, 0.8, len(index)),
            "biomass_anchoveta": rng.lognormal(13, 0.3, len(index)),
        },
        index=index,
    )


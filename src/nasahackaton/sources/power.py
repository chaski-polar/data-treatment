"""Cliente para NASA POWER."""

from __future__ import annotations

import pandas as pd
import requests


POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"


def fetch_daily(
    latitude: float,
    longitude: float,
    start: str,
    end: str,
    parameters: str = "RH2M,PRECTOTCORR,T2M,WS2M",
) -> pd.DataFrame:
    """Descarga datos diarios de NASA POWER y los devuelve como DataFrame."""
    response = requests.get(
        POWER_URL,
        params={
            "parameters": parameters,
            "community": "AG",
            "latitude": latitude,
            "longitude": longitude,
            "start": start,
            "end": end,
            "format": "JSON",
        },
        timeout=30,
    )
    response.raise_for_status()
    parameters_data = response.json()["properties"]["parameter"]
    return pd.DataFrame(parameters_data).astype(float)

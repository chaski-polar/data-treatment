"""Series oceánicas de Copernicus Marine para una zona."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import copernicusmarine as cm


ZONES = {
    "peru": (-85, -20, -70, -3),
    "peninsula": (-70, -69, -55, -61),
}


def monthly_series(data_array):
    """Promedia la capa superficial y devuelve una serie mensual."""
    if "depth" in data_array.dims:
        data_array = data_array.isel(depth=0)
    series = data_array.mean(["latitude", "longitude"]).to_series()
    series.index = series.index.to_period("M")
    return series


def load_ocean_series(
    zone: str = "peru",
    start: str = "2020-01-01",
    end: str = "2023-12-31",
) -> pd.DataFrame:
    """Descarga y combina variables biogeoquímicas y temperatura."""
    west, south, east, north = ZONES[zone]
    common = {
        "minimum_longitude": west,
        "maximum_longitude": east,
        "minimum_latitude": south,
        "maximum_latitude": north,
        "start_datetime": start,
        "end_datetime": end,
        "minimum_depth": 0,
        "maximum_depth": 2,
    }
    biogeochemistry = cm.open_dataset(
        dataset_id="cmems_mod_glo_bgc_my_0.25deg_P1M-m",
        variables=["chl", "no3", "po4"],
        **common,
    )
    physics = cm.open_dataset(
        dataset_id="cmems_mod_glo_phy-all_my_0.25deg_P1D-m",
        variables=["thetao"],
        **common,
    )
    temperature = physics["thetao"].resample(time="1MS").mean()
    return pd.DataFrame(
        {
            "clorofila (mg/m3)": monthly_series(biogeochemistry["chl"]),
            "nitrato (mmol/m3)": monthly_series(biogeochemistry["no3"]),
            "fosfato (mmol/m3)": monthly_series(biogeochemistry["po4"]),
            "temperatura (°C)": monthly_series(temperature),
        }
    ).dropna()


def main() -> None:
    cm.login()
    data = load_ocean_series()
    print(data.head())
    print("\nCorrelaciones exploratorias:")
    print(data.corr().round(2))
    data.index = data.index.to_timestamp()
    data.plot(subplots=True, figsize=(10, 8), marker="o", title="Zona: peru")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()

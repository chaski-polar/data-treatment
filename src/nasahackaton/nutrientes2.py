"""Variante de nutrientes con detección de temperatura del ensamble."""

from __future__ import annotations

import copernicusmarine as cm

from nasahackaton.nutrientes import ZONES, monthly_series


def load_ensemble_temperature(
    zone: str = "peru",
    start: str = "2020-01-01",
    end: str = "2022-12-31",
):
    """Abre el producto físico y devuelve el nombre de temperatura disponible."""
    west, south, east, north = ZONES[zone]
    dataset = cm.open_dataset(
        dataset_id="cmems_mod_glo_phy-mnstd_my_0.25deg_P1D-m",
        minimum_longitude=west,
        maximum_longitude=east,
        minimum_latitude=south,
        maximum_latitude=north,
        start_datetime=start,
        end_datetime=end,
        minimum_depth=0,
        maximum_depth=2,
    )
    variable = next(
        name for name in dataset.data_vars
        if name.startswith("thetao") and "std" not in name
    )
    return dataset, variable


def main() -> None:
    cm.login()
    dataset, variable = load_ensemble_temperature()
    print("Variables disponibles:", list(dataset.data_vars))
    print("Usando como temperatura:", variable)
    print(monthly_series(dataset[variable].resample(time="1MS").mean()).head())


if __name__ == "__main__":
    main()

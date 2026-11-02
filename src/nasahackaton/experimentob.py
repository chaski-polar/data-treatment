"""Experimento B — predictores de productividad (sin zooplancton IMARPE).

Variables que faltaban según ``docs/bitacora.md``:

* PDO (NOAA PSL / ERDDAP CCIEA)
* Nutrientes WOA 2023 (nitrato, fosfato, silicato) — climatología mensual
* Carbono y fracciones micro/nano/pico desde color del océano (OC-CCI + Brewin)

Nota de la bitácora: WOA no tiene variación interanual; para series temporales
de nutrientes conviene el reanálisis CMEMS vía :mod:`nasahackaton.nutrientes`.
Zooplancton IMARPE queda fuera a propósito.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from nasahackaton.config import BoundingBox, PERU_OCEAN, PROJECT_ROOT
from nasahackaton.sources.noaa import (
    erddap_griddap_nc,
    fetch_pdo,
    woa23_box_mean,
)

# OC-CCI v6 mensual en OceanWatch (mismo patrón que modisa.py).
OCCCI_SERVER = "https://oceanwatch.pifsc.noaa.gov/erddap"
OCCCI_DATASET = "esa-cci-chla-monthly-v6-0"
OCCCI_VAR = "chlor_a"

# Brewin et al. (2010) — tres componentes (pico, nano, micro) sobre clorofila.
BREWIN_C1_PICO = 0.13
BREWIN_S_PICO = 0.80
BREWIN_C1_PICO_NANO = 0.77
BREWIN_S_PICO_NANO = 0.94

# Conversión simple Chl→C (mg C m⁻³): C = Chl / (Chl:C). Ver Behrenfeld et al.
DEFAULT_CHL_TO_C = 0.02

WOA_CACHE = PROJECT_ROOT / "data" / "woa23"


def brewin_size_classes(
    chlor_a: pd.Series | np.ndarray | float,
    *,
    c1_pico: float = BREWIN_C1_PICO,
    s_pico: float = BREWIN_S_PICO,
    c1_pico_nano: float = BREWIN_C1_PICO_NANO,
    s_pico_nano: float = BREWIN_S_PICO_NANO,
) -> pd.DataFrame:
    """Fracciones de clorofila en micro/nano/pico (Brewin 2010)."""
    chl = pd.Series(chlor_a, dtype=float).clip(lower=0.0)
    pico = c1_pico * (1.0 - np.exp(-s_pico * chl))
    pico_nano = c1_pico_nano * (1.0 - np.exp(-s_pico_nano * chl))
    pico = np.minimum(pico, chl)
    pico_nano = np.minimum(np.maximum(pico_nano, pico), chl)
    nano = pico_nano - pico
    micro = chl - pico_nano
    return pd.DataFrame(
        {
            "chlor_a": chl.to_numpy(),
            "chl_pico": np.asarray(pico),
            "chl_nano": np.asarray(nano),
            "chl_micro": np.asarray(micro),
            "frac_pico": np.where(chl > 0, pico / chl, np.nan),
            "frac_nano": np.where(chl > 0, nano / chl, np.nan),
            "frac_micro": np.where(chl > 0, micro / chl, np.nan),
        },
        index=chl.index,
    )


def chlorophyll_to_carbon(
    chlor_a: pd.Series | np.ndarray | float,
    *,
    chl_to_c: float = DEFAULT_CHL_TO_C,
) -> pd.Series:
    """Carbono fitoplanctónico aproximado (mg C m⁻³) con Chl:C constante."""
    chl = pd.Series(chlor_a, dtype=float)
    carbon = chl / chl_to_c
    carbon.name = "phyto_carbon"
    return carbon


def load_pdo(start: str = "1998-01-01", end: str = "2026-12-31") -> pd.Series:
    """PDO mensual NOAA (ERDDAP; cae a PSL si falla)."""
    try:
        return fetch_pdo(start=start, end=end, source="erddap")
    except Exception:  # noqa: BLE001
        return fetch_pdo(start=start, end=end, source="psl")


def load_woa_nutrients_climatology(
    box: BoundingBox = PERU_OCEAN,
    *,
    cache_dir: Path | None = None,
) -> pd.DataFrame:
    """Climatología mensual WOA23 (micromol/kg) promediada en la caja.

    Una fila por mes calendario (1–12). Sin variación interanual.
    """
    cache = Path(cache_dir) if cache_dir is not None else WOA_CACHE
    rows: list[dict[str, float | int]] = []
    for month in range(1, 13):
        row: dict[str, float | int] = {"month": month}
        for nutrient, column in (
            ("nitrate", "no3_woa"),
            ("phosphate", "po4_woa"),
            ("silicate", "si_woa"),
        ):
            row[column] = woa23_box_mean(
                nutrient,
                month,
                south=box.south,
                north=box.north,
                west=box.west,
                east=box.east,
                cache_dir=cache,
            )
        rows.append(row)
    return pd.DataFrame(rows).set_index("month")


def load_chlorophyll_occci(
    start: str = "1998-01-01",
    end: str = "2022-12-31",
    box: BoundingBox = PERU_OCEAN,
    *,
    lat_stride: int = 10,
    lon_stride: int = 10,
) -> pd.Series:
    """Serie mensual de clorofila-a OC-CCI v6 (mediana espacial en la caja)."""
    ds = erddap_griddap_nc(
        OCCCI_SERVER,
        OCCCI_DATASET,
        OCCCI_VAR,
        time_start=start,
        time_end=end,
        lat_max=box.north,
        lat_min=box.south,
        lon_min=box.west,
        lon_max=box.east,
        lat_stride=lat_stride,
        lon_stride=lon_stride,
    )
    da = ds[OCCCI_VAR]
    # Mediana es más robusta que la media en océano costero (bitácora / fitoplancton).
    series = da.median(dim=("latitude", "longitude"), skipna=True).to_series()
    series.index = pd.to_datetime(series.index).to_period("M").to_timestamp()
    return series.rename("chlor_a").astype(float)


def load_phytoplankton_size_carbon(
    start: str = "1998-01-01",
    end: str = "2022-12-31",
    box: BoundingBox = PERU_OCEAN,
    *,
    chl_to_c: float = DEFAULT_CHL_TO_C,
) -> pd.DataFrame:
    """Clorofila OC-CCI + fracciones Brewin + carbono aproximado.

    PACE solo cubre desde 2024; aquí se usa color del océano 1998–presente
    (OC-CCI) como pide la bitácora para el espectro de tamaños.
    """
    chlor_a = load_chlorophyll_occci(start=start, end=end, box=box)
    sizes = brewin_size_classes(chlor_a)
    carbon = chlorophyll_to_carbon(chlor_a, chl_to_c=chl_to_c)
    sizes["phyto_carbon"] = carbon
    sizes["c_pico"] = sizes["frac_pico"] * carbon
    sizes["c_nano"] = sizes["frac_nano"] * carbon
    sizes["c_micro"] = sizes["frac_micro"] * carbon
    return sizes


def load_experiment_b_predictors(
    start: str = "1998-01-01",
    end: str = "2022-12-31",
    box: BoundingBox = PERU_OCEAN,
    *,
    include_woa: bool = True,
    include_size_carbon: bool = True,
) -> pd.DataFrame:
    """Tabla mensual lista para el Experimento B (sin zooplancton)."""
    pdo = load_pdo(start=start, end=end)
    frame = pd.DataFrame({"PDO": pdo})
    frame.index = pd.to_datetime(frame.index).to_period("M").to_timestamp()

    if include_size_carbon:
        sizes = load_phytoplankton_size_carbon(start=start, end=end, box=box)
        frame = frame.join(sizes, how="outer")

    if include_woa:
        clim = load_woa_nutrients_climatology(box=box)
        months = frame.index.month
        for col in clim.columns:
            frame[col] = clim.loc[months, col].to_numpy()

    return frame.sort_index()


def main() -> None:
    """Descarga rápida de comprobación (PDO + enero WOA + tramo corto OC-CCI)."""
    print("PDO (2019–2020)…")
    pdo = load_pdo("2019-01-01", "2020-12-31")
    print(pdo.tail())

    print("\nWOA23 enero (caja Perú, micromol/kg)…")
    for nutrient, column in (
        ("nitrate", "no3_woa"),
        ("phosphate", "po4_woa"),
        ("silicate", "si_woa"),
    ):
        value = woa23_box_mean(
            nutrient,
            1,
            south=PERU_OCEAN.south,
            north=PERU_OCEAN.north,
            west=PERU_OCEAN.west,
            east=PERU_OCEAN.east,
            cache_dir=WOA_CACHE,
        )
        print(f"  {column}: {value:.3f}")

    print("\nOC-CCI + Brewin + carbono (2020-01…2020-03)…")
    sizes = load_phytoplankton_size_carbon("2020-01-01", "2020-03-01")
    print(sizes.head())


if __name__ == "__main__":
    main()

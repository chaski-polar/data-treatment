"""Construye el panel real por intervalos para los experimentos A y B.

La biomasa de cruceros no es mensual: cada fila representa una campaña con
fecha de inicio y fin. El panel de ajuste conserva una fila por campaña y
resume las variables ambientales dentro de esa misma ventana. La salida de
monitoreo sí es mensual, pero deja visibles la cobertura y los conflictos
entre campañas; nunca interpola biomasa entre cruceros.

Uso:
    .venv/bin/python scripts/04_build_real_panel.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PHYSICS = ROOT / "data/raw/copernicus/physics_1998-01-01_2026-10-31.nc"
DEFAULT_BGC = ROOT / "data/raw/copernicus/biogeochemistry_1998-01-01_2026-10-31.nc"
DEFAULT_OC_CCI = ROOT / "data/raw/ocean_color/chlorophyll_occci.nc"
DEFAULT_KD490 = ROOT / "data/raw/ocean_color/kd490_occci.nc"
DEFAULT_PDO = ROOT / "data/raw/noaa/pdo_monthly_1998_2026.csv"
DEFAULT_ICEN = ROOT / "data/raw/igp/icen_monthly.csv"
DEFAULT_NINO12 = ROOT / "data/nino12.long.anom.csv"
DEFAULT_BIOMASS = ROOT / "data/biomasa_cruceros.csv"
DEFAULT_OUTPUT = ROOT / "data/processed/tables"


def _suitability(values: pd.Series, lower: float, upper: float, decay: float) -> pd.Series:
    """Idoneidad trapezoidal usada en las ecuaciones documentadas."""
    values = pd.to_numeric(values, errors="coerce")
    score = pd.Series(np.nan, index=values.index, dtype=float)
    valid = values.notna()
    score.loc[valid] = 1.0
    below = valid & (values < lower)
    above = valid & (values > upper)
    score.loc[below] = np.maximum(0.0, 1.0 - (lower - values.loc[below]) / decay)
    score.loc[above] = np.maximum(0.0, 1.0 - (values.loc[above] - upper) / decay)
    return score


def add_suitability_components(frame: pd.DataFrame) -> pd.DataFrame:
    """Añade componentes HSI sin ocultar predictores aún no disponibles."""
    result = frame.copy()
    result["S_sst"] = _suitability(result["sst"], 16.0, 22.0, 2.5)
    result["S_sss"] = _suitability(result["sss"], 34.0, 35.2, 0.4)
    result["S_oxygen"] = _suitability(result["oxygen"], 5.0, 8.5, 1.5)
    result["S_distance_coast"] = np.maximum(0.0, 1.0 - result["distance_coast"] / 150.0)
    result["S_chlorophyll"] = _suitability(result["chlorophyll_a"], 2.5, 8.0, 1.5)
    abiotic = result[["S_sst", "S_sss", "S_oxygen", "S_distance_coast"]]
    trophic = result[["S_sst", "S_sss", "S_oxygen", "S_distance_coast", "S_chlorophyll"]]
    result["hsi_abiotic"] = abiotic.prod(axis=1, min_count=4).pow(0.25)
    result["hsi_trophic"] = trophic.prod(axis=1, min_count=5).pow(0.20)
    return result


def _monthly_spatial_frame(path: Path, variables: dict[str, str]) -> pd.DataFrame:
    """Lee un NetCDF, toma 0–5 m y mediana espacial por mes."""
    with xr.open_dataset(path) as source:
        ds = source.load()
    time_name = "time" if "time" in ds.coords else "valid_time"
    rows: dict[str, pd.Series] = {}
    for source_name, output_name in variables.items():
        if source_name not in ds:
            continue
        da = ds[source_name]
        if "depth" in da.dims:
            da = da.sel(depth=slice(0, 5)).mean("depth", skipna=True)
        spatial_dims = [d for d in ("latitude", "longitude", "lat", "lon") if d in da.dims]
        if spatial_dims:
            da = da.median(spatial_dims, skipna=True)
        series = da.to_series()
        series.index = pd.to_datetime(series.index).to_period("M").to_timestamp()
        rows[output_name] = series.groupby(level=0).median()
    if not rows:
        raise ValueError(f"No se encontraron variables en {path}")
    return pd.DataFrame(rows).sort_index()


def load_environment(args: argparse.Namespace) -> pd.DataFrame:
    physics = _monthly_spatial_frame(args.physics, {"thetao": "sst", "so": "sss"})
    bgc = _monthly_spatial_frame(
        args.bgc,
        {"chl": "chlorophyll_a", "no3": "nitrate", "po4": "phosphate", "o2": "oxygen", "phyc": "phytoplankton_carbon"},
    )
    # CMEMS: O2 en mmol m-3 y carbono en mmol C m-3.
    # Las ecuaciones documentadas usan ml L-1 y mg C m-3.
    if "oxygen" in bgc:
        bgc["oxygen"] = bgc["oxygen"] / 44.66
    if "phytoplankton_carbon" in bgc:
        bgc["phytoplankton_carbon"] = bgc["phytoplankton_carbon"] * 12.0107
    environment = physics.join(bgc, how="outer")

    if args.oc_cci.exists():
        oc_cci = _monthly_spatial_frame(args.oc_cci, {"chlor_a": "chlorophyll_occci"})
        environment = environment.join(oc_cci, how="outer")
    if args.kd490.exists():
        kd490 = _monthly_spatial_frame(args.kd490, {"kd_490": "kd490"})
        environment = environment.join(kd490, how="outer")

    if args.pdo.exists():
        pdo = pd.read_csv(args.pdo, parse_dates=["date"]).set_index("date")["PDO"]
        pdo.index = pdo.index.to_period("M").to_timestamp()
        environment = environment.join(pdo.rename("pdo"), how="outer")

    if args.icen.exists():
        icen = pd.read_csv(args.icen, parse_dates=["date"]).set_index("date")["icen"]
        icen.index = icen.index.to_period("M").to_timestamp()
        environment = environment.join(icen.rename("icen"), how="outer")

    if args.nino12.exists():
        nino12 = pd.read_csv(
            args.nino12,
            skiprows=1,
            sep=r"\s+",
            names=["date", "nino12"],
            na_values=(-9999, -99.99),
            engine="python",
        )
        nino12["date"] = pd.to_datetime(nino12["date"], errors="coerce")
        nino12["nino12"] = pd.to_numeric(nino12["nino12"], errors="coerce")
        nino12 = nino12.dropna(subset=["date"]).set_index("date")
        nino12.index = nino12.index.to_period("M").to_timestamp()
        environment = environment.join(nino12["nino12"], how="outer")

    # Estas variables no se sustituyen por PDO ni por valores constantes.
    # Quedan explícitas para que el informe de calidad muestre el bloqueo de A.
    for missing in ("oni", "distance_coast"):
        environment[missing] = np.nan

    # El ICEN histórico comienza en 1950, pero el panel operativo común
    # se limita a los meses cubiertos por CMEMS en esta ejecución.
    environment = environment.reindex(physics.index)

    environment = add_suitability_components(environment)
    environment.index.name = "date"
    # El archivo ERA5 contiene septiembre de 2026, pero CMEMS termina en
    # agosto para el periodo operativo documentado.
    return environment.sort_index()


def load_biomass(path: Path, stock: str) -> pd.DataFrame:
    frame = pd.read_csv(path, parse_dates=["fecha_inicio", "fecha_fin"])
    required = {"crucero", "fecha_inicio", "fecha_fin", "biomasa_t", "stock"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Faltan columnas en biomasa: {sorted(missing)}")
    frame = frame[frame["stock"].eq(stock)].copy()
    frame["biomasa_t"] = pd.to_numeric(frame["biomasa_t"], errors="coerce")
    frame = frame.dropna(subset=["fecha_inicio", "fecha_fin", "biomasa_t"])
    frame = frame[frame["fecha_fin"] >= frame["fecha_inicio"]].copy()
    if frame["crucero"].duplicated().any():
        raise ValueError("Hay varias filas para el mismo crucero; elige una medida de stock explícita")
    return frame.sort_values("fecha_inicio").reset_index(drop=True)


def _weighted_interval_mean(environment: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> pd.Series:
    months = pd.date_range(start.to_period("M").to_timestamp(), end.to_period("M").to_timestamp(), freq="MS")
    selected = environment.reindex(months)
    weights = []
    for month in months:
        month_end = month + pd.offsets.MonthEnd(1)
        overlap_start = max(start, month)
        overlap_end = min(end, month_end)
        weights.append(max(0, (overlap_end - overlap_start).days + 1))
    weights_array = np.asarray(weights, dtype=float)
    result = {}
    for column in selected.columns:
        values = selected[column].to_numpy(dtype=float)
        valid = np.isfinite(values) & (weights_array > 0)
        result[column] = float(np.average(values[valid], weights=weights_array[valid])) if valid.any() else np.nan
    return pd.Series(result)


def build_interval_panel(environment: pd.DataFrame, biomass: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, observation in biomass.iterrows():
        start = observation["fecha_inicio"]
        end = observation["fecha_fin"]
        row = observation.to_dict()
        row["interval_days"] = (end - start).days + 1
        row.update(_weighted_interval_mean(environment, start, end).to_dict())
        rows.append(row)
    panel = pd.DataFrame(rows)
    panel["biomass_anchoveta"] = panel["biomasa_t"]
    panel["biomass_observed"] = True
    panel["observation_type"] = "cruise_interval"
    return panel


def build_monitoring_series(environment: pd.DataFrame, biomass: pd.DataFrame) -> pd.DataFrame:
    """Expande intervalos a meses solo como cobertura observacional visible."""
    result = environment.copy()
    result["biomass_total_t"] = np.nan
    result["biomass_observed"] = False
    result["biomass_observation_count"] = 0
    result["biomass_cruise_ids"] = ""
    result["biomass_interval_start"] = pd.NaT
    result["biomass_interval_end"] = pd.NaT

    month_rows: dict[pd.Timestamp, list[pd.Series]] = {}
    for _, observation in biomass.iterrows():
        months = pd.date_range(observation["fecha_inicio"].to_period("M").to_timestamp(), observation["fecha_fin"].to_period("M").to_timestamp(), freq="MS")
        for month in months:
            month_rows.setdefault(month, []).append(observation)

    for month, observations in month_rows.items():
        if month not in result.index:
            result.loc[month, :] = np.nan
        result.loc[month, "biomass_observed"] = True
        result.loc[month, "biomass_observation_count"] = len(observations)
        result.loc[month, "biomass_cruise_ids"] = ";".join(str(item["crucero"]) for item in observations)
        result.loc[month, "biomass_interval_start"] = min(item["fecha_inicio"] for item in observations)
        result.loc[month, "biomass_interval_end"] = max(item["fecha_fin"] for item in observations)
        # Si dos campañas cubren el mismo mes, la media queda marcada por el
        # contador; no se interpreta como una nueva observación independiente.
        result.loc[month, "biomass_total_t"] = np.mean([item["biomasa_t"] for item in observations])

    result["data_quality"] = np.where(result["biomass_observed"], "environmental_series + cruise_interval", "environmental_series_only")
    result.index.name = "date"
    return result.sort_index()


def build_quality_report(environment: pd.DataFrame, interval_panel: pd.DataFrame, monitoring: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for column in environment.columns:
        rows.append({"table": "environment", "variable": column, "rows": len(environment), "non_null": int(environment[column].notna().sum()), "coverage_pct": float(environment[column].notna().mean() * 100)})
    for column in ("biomasa_t", *[c for c in environment.columns if c in interval_panel]):
        if column in interval_panel:
            rows.append({"table": "interval_panel", "variable": column, "rows": len(interval_panel), "non_null": int(interval_panel[column].notna().sum()), "coverage_pct": float(interval_panel[column].notna().mean() * 100)})
    rows.append({"table": "monitoring", "variable": "biomass_total_t", "rows": len(monitoring), "non_null": int(monitoring["biomass_total_t"].notna().sum()), "coverage_pct": float(monitoring["biomass_total_t"].notna().mean() * 100)})
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--physics", type=Path, default=DEFAULT_PHYSICS)
    parser.add_argument("--bgc", type=Path, default=DEFAULT_BGC)
    parser.add_argument("--oc-cci", type=Path, default=DEFAULT_OC_CCI)
    parser.add_argument("--kd490", type=Path, default=DEFAULT_KD490)
    parser.add_argument("--pdo", type=Path, default=DEFAULT_PDO)
    parser.add_argument("--icen", type=Path, default=DEFAULT_ICEN)
    parser.add_argument("--nino12", type=Path, default=DEFAULT_NINO12)
    parser.add_argument("--biomass", type=Path, default=DEFAULT_BIOMASS)
    parser.add_argument("--stock", default="toda_costa", choices=("toda_costa", "norte_centro", "sur"))
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    environment = load_environment(args)
    biomass = load_biomass(args.biomass, args.stock)
    interval_panel = build_interval_panel(environment, biomass)
    monitoring = build_monitoring_series(environment, biomass)
    quality = build_quality_report(environment, interval_panel, monitoring)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    interval_path = args.output_dir / "panel_experiments_ab.csv"
    monitoring_path = args.output_dir / "monitoring_series_ab.csv"
    monitoring_json_path = args.output_dir / "monitoring_series_ab.json"
    quality_path = args.output_dir / "panel_quality_report.csv"
    interval_panel.to_csv(interval_path, index=False)
    monitoring.to_csv(monitoring_path, index=True, date_format="%Y-%m-%d")
    monitoring.reset_index().to_json(monitoring_json_path, orient="records", date_format="iso", date_unit="s")
    quality.to_csv(quality_path, index=False)
    print(f"Panel por intervalos: {interval_path} ({len(interval_panel)} cruceros)")
    print(f"Serie de monitoreo:    {monitoring_path} ({len(monitoring)} meses)")
    print(f"Serie JSON para web:    {monitoring_json_path}")
    print(f"Reporte de calidad:     {quality_path}")
    print(f"Biomasa observada: {int(monitoring['biomass_observed'].sum())} meses; sin interpolación")
    print("Variables faltantes deliberadamente: oni, distance_coast")


if __name__ == "__main__":
    main()

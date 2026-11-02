"""Construye los paneles reales por intervalos para los experimentos A, B y C.

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
import base64
import gzip
import json
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
DEFAULT_ZOOPLANKTON_HINDCAST = ROOT / "data/raw/copernicus/zooplankton_hindcast_1998-01-01_2025-12-31.nc"
DEFAULT_ZOOPLANKTON_OPERATIONAL = ROOT / "data/raw/copernicus/zooplankton_operational_2023-12-01_2026-08-31.nc"
DEFAULT_OUTPUT = ROOT / "data/processed/tables"
GRID_LOG_MIN = -1.7  # 0,02 mg/m³; coincide con la escala visual del globo
GRID_LOG_MAX = 1.3   # 20 mg/m³


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


def add_biomass_interpolation(frame: pd.DataFrame) -> pd.DataFrame:
    """Interpola biomasa solo entre meses con observaciones de crucero.

    Esta columna es exclusivamente para visualización. La columna original
    biomass_total_t y biomass_observed se conservan intactas.
    """
    result = frame.copy()
    observed = result["biomass_total_t"].where(result["biomass_observed"])
    interpolated = observed.interpolate(method="linear", limit_area="inside")
    result["biomass_total_t_interpolated"] = interpolated
    result["biomass_value_type"] = np.select(
        [
            result["biomass_observed"],
            interpolated.notna() & ~result["biomass_observed"],
        ],
        ["observed", "interpolated"],
        default="missing",
    )
    result["biomass_interpolation_method"] = np.where(
        result["biomass_value_type"].eq("interpolated"),
        "linear_between_cruise_intervals",
        None,
    )
    return result


def _zooplankton_monthly(path: Path, source_label: str) -> pd.DataFrame:
    """Resume ``zooc`` espacialmente y por mes sin cargar la grilla completa."""
    with xr.open_dataset(path) as source:
        if "zooc" not in source:
            raise ValueError(f"No se encontró zooc en {path}")
        zoo = source["zooc"]
        if "depth" in zoo.dims:
            # El producto operativo trae capas pelágicas; usamos la epipelágica
            # para aproximar el alimento disponible en la superficie.
            zoo = zoo.isel(depth=0)
        spatial_dims = [d for d in ("latitude", "longitude", "lat", "lon") if d in zoo.dims]
        if not spatial_dims:
            raise ValueError(f"zooc no tiene dimensiones espaciales en {path}")
        zoo = zoo.median(spatial_dims, skipna=True)
        if "time" not in zoo.dims:
            time_name = "valid_time" if "valid_time" in zoo.dims else None
            if time_name:
                zoo = zoo.rename({time_name: "time"})
        if "time" not in zoo.dims:
            raise ValueError(f"zooc no tiene dimensión temporal en {path}")
        units = str(source["zooc"].attrs.get("units", "")).lower().replace(" ", "")
        monthly = zoo.resample(time="MS").mean(skipna=True).load()

    # Canonicalizamos a mg C m-2. El hindcast ya es contenido integrado;
    # el producto operativo es concentración en la primera capa, por lo que
    # se integra aproximadamente sobre 5 m antes de armonizarlo.
    if "g m-2".replace(" ", "") in units or "gm-2" in units:
        values = monthly * 1000.0
        conversion = "g C m-2 -> mg C m-2"
    elif "mmolm-3" in units:
        values = monthly * 12.0107 * 5.0
        conversion = "mmol C m-3 -> mg C m-2 usando 5 m"
    elif "mg c m-3".replace(" ", "") in units or "mgcm-3" in units:
        values = monthly * 5.0
        conversion = "mg C m-3 -> mg C m-2 usando 5 m"
    else:
        raise ValueError(f"Unidades de zooc no reconocidas en {path}: {units!r}")

    series = pd.Series(np.asarray(values.to_numpy(), dtype=float), index=pd.to_datetime(values["time"].values), name="zooplankton_carbon")
    return pd.DataFrame(
        {
            "zooplankton_carbon": series,
            "zooplankton_source": source_label,
            "zooplankton_conversion": conversion,
        }
    )


def load_zooplankton(hindcast: Path, operational: Path) -> pd.DataFrame:
    """Une hindcast y producto operativo, calibrando el segundo al solapamiento."""
    frames = []
    if hindcast.exists():
        frames.append(_zooplankton_monthly(hindcast, "CMEMS LMTL hindcast"))
    if operational.exists():
        frames.append(_zooplankton_monthly(operational, "CMEMS BGC operativo"))
    if not frames:
        raise FileNotFoundError("No se encontró ningún NetCDF de zooplancton")
    if len(frames) == 1:
        result = frames[0].copy()
        result["zooplankton_harmonization_factor"] = 1.0
        return result.sort_index()

    historical, recent = frames
    overlap = historical.join(recent, lsuffix="_hindcast", rsuffix="_operational", how="inner")
    valid = overlap[["zooplankton_carbon_hindcast", "zooplankton_carbon_operational"]].replace([np.inf, -np.inf], np.nan).dropna()
    valid = valid[(valid > 0).all(axis=1)]
    if valid.empty:
        raise ValueError("No hay solapamiento válido entre hindcast y zooplancton operativo")
    factor = float(np.median(valid["zooplankton_carbon_hindcast"] / valid["zooplankton_carbon_operational"]))
    recent = recent.copy()
    recent["zooplankton_carbon"] *= factor
    recent["zooplankton_harmonization_factor"] = factor
    historical = historical.copy()
    historical["zooplankton_harmonization_factor"] = 1.0
    result = historical.combine_first(recent)
    result["zooplankton_source"] = historical["zooplankton_source"].combine_first(recent["zooplankton_source"])
    result["zooplankton_conversion"] = historical["zooplankton_conversion"].combine_first(recent["zooplankton_conversion"])
    result["zooplankton_harmonization_factor"] = historical["zooplankton_harmonization_factor"].combine_first(recent["zooplankton_harmonization_factor"])
    return result.sort_index()


def build_experiment_c_panel(environment: pd.DataFrame, monitoring: pd.DataFrame, zooplankton: pd.DataFrame) -> pd.DataFrame:
    """Construye los estados F-Z-A mensuales para el Experimento C."""
    result = environment[["phytoplankton_carbon"]].join(zooplankton, how="outer")
    biomass_columns = ["biomass_total_t_interpolated", "biomass_total_t"]
    biomass_column = next((column for column in biomass_columns if column in monitoring), None)
    if biomass_column is None:
        raise ValueError("La serie de monitoreo no contiene biomasa de anchoveta")
    result = result.join(monitoring[[biomass_column, "biomass_observed"]], how="outer")
    result = result.rename(columns={biomass_column: "biomass_anchoveta", "zooplankton_carbon": "zooplankton"})
    if "biomass_value_type" in monitoring:
        result = result.join(monitoring[["biomass_value_type"]], how="left")
    else:
        result["biomass_value_type"] = np.where(result["biomass_observed"], "observed", "missing")
    result["experiment_c_data_quality"] = np.select(
        [result["biomass_value_type"].eq("observed"), result["biomass_value_type"].eq("interpolated")],
        ["zooplankton_model + biomass_observed", "zooplankton_model + biomass_interpolated"],
        default="zooplankton_model + biomass_missing",
    )
    result.index.name = "date"
    return result.sort_index()


def build_experiment_c_payload(panel: pd.DataFrame) -> dict:
    """Serializa los estados F-Z-A y sus metadatos para el monitor/videojuego."""
    records = panel.reset_index().copy()
    records["date"] = pd.to_datetime(records["date"]).dt.strftime("%Y-%m-%d")
    records = records.replace({np.nan: None})
    return {
        "schema_version": "1.0",
        "generated_at": pd.Timestamp.now("UTC").isoformat(),
        "experiment": "C",
        "states": {
            "F": {"column": "phytoplankton_carbon", "units": "mg C m-3"},
            "Z": {"column": "zooplankton", "units": "mg C m-2"},
            "A": {"column": "biomass_anchoveta", "units": "t"},
        },
        "notes": [
            "Zooplancton procede de modelos CMEMS y no de observaciones directas.",
            "El producto operativo se armoniza al hindcast usando la mediana del solapamiento.",
            "La biomasa interpolada se conserva como estimada para el monitor y el videojuego.",
        ],
        "records": records.to_dict(orient="records"),
    }


def build_quality_report(environment: pd.DataFrame, interval_panel: pd.DataFrame, monitoring: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for column in environment.columns:
        rows.append({"table": "environment", "variable": column, "rows": len(environment), "non_null": int(environment[column].notna().sum()), "coverage_pct": float(environment[column].notna().mean() * 100)})
    for column in ("biomasa_t", *[c for c in environment.columns if c in interval_panel]):
        if column in interval_panel:
            rows.append({"table": "interval_panel", "variable": column, "rows": len(interval_panel), "non_null": int(interval_panel[column].notna().sum()), "coverage_pct": float(interval_panel[column].notna().mean() * 100)})
    rows.append({"table": "monitoring", "variable": "biomass_total_t", "rows": len(monitoring), "non_null": int(monitoring["biomass_total_t"].notna().sum()), "coverage_pct": float(monitoring["biomass_total_t"].notna().mean() * 100)})
    return pd.DataFrame(rows)


def build_web_payload(monitoring: pd.DataFrame) -> dict:
    """Adapta la tabla interna a un JSON estable para la página."""
    columns = {
        "sst": "sst_c",
        "sss": "sss_psu",
        "oxygen": "oxygen_ml_l",
        "chlorophyll_a": "chlorophyll_a_mg_m3",
        "nitrate": "nitrate_mmol_m3",
        "phosphate": "phosphate_mmol_m3",
        "phytoplankton_carbon": "phytoplankton_carbon_mg_c_m3",
        "pdo": "pdo",
        "icen": "icen",
        "nino12": "nino12_anom_c",
        "distance_coast": "distance_coast_nm",
        "biomass_total_t": "biomass_total_t",
        "biomass_total_t_interpolated": "biomass_total_t_interpolated",
        "hsi_abiotic": "hsi_abiotic",
        "hsi_trophic": "hsi_trophic",
    }
    records = monitoring.reset_index().rename(columns=columns)
    records["date"] = pd.to_datetime(records["date"]).dt.strftime("%Y-%m-%d")
    records["biomass_cruise_ids"] = records["biomass_cruise_ids"].apply(
        lambda value: [item for item in str(value).split(";") if item] if pd.notna(value) else []
    )
    for date_column in ("biomass_interval_start", "biomass_interval_end"):
        records[date_column] = pd.to_datetime(records[date_column], errors="coerce").dt.strftime("%Y-%m-%d")
    records = records.replace({np.nan: None})
    return {
        "schema_version": "1.0",
        "generated_at": pd.Timestamp.now("UTC").isoformat(),
        "period": {
            "start": records["date"].iloc[0],
            "end": records["date"].iloc[-1],
        },
        "sources": {
            "environment": "CMEMS reanalysis; OC-CCI",
            "icen": "IGP/ENFEN, ICEN basado en ERSSTv5",
            "nino12": "NOAA PSL/CPC Niño 1+2",
            "pdo": "NOAA PSL",
            "biomass": "IMARPE cruise intervals",
            "coast_distance": "GSHHS-derived regional reference; partial coverage",
        },
        "notes": [
            "Biomass is observed only during cruise intervals; it is not interpolated.",
            "biomass_total_t_interpolated is for visualization only and must not be used as an observed response for model fitting.",
            "Missing values are null.",
            "distance_coast is null where the regional lookup has no coverage.",
        ],
        "records": records.to_dict(orient="records"),
    }


def build_chlorophyll_grid_payload(path: Path) -> dict:
    """Serializa la grilla mensual de clorofila CMEMS para el mapa web.

    La serie de monitoreo conserva la mediana espacial, pero el mapa necesita
    cada celda. Se toma la media vertical de 0–5 m, se conserva el orden
    ``time, latitude, longitude`` y se cuantiza en escala logarítmica a un
    byte: 0 significa sin dato y 1–255 son valores válidos. El bloque de
    bytes se comprime con gzip y se codifica en Base64 para mantener un JSON
    transportable por una página estática.
    """
    with xr.open_dataset(path) as source:
        if "chl" not in source:
            raise ValueError(f"No se encontró la variable chl en {path}")
        chl = source["chl"]
        if "depth" in chl.dims:
            chl = chl.sel(depth=slice(0, 5)).mean("depth", skipna=True)
        time_name = "time" if "time" in chl.coords else "valid_time"
        lat_name = next((name for name in ("latitude", "lat") if name in chl.coords), None)
        lon_name = next((name for name in ("longitude", "lon") if name in chl.coords), None)
        if not lat_name or not lon_name:
            raise ValueError(f"La grilla de {path} no tiene coordenadas latitud/longitud")
        chl = chl.transpose(time_name, lat_name, lon_name).load()

    values = np.asarray(chl.values, dtype=np.float32)
    valid = np.isfinite(values) & (values > 0)
    quantized = np.zeros(values.shape, dtype=np.uint8)
    with np.errstate(divide="ignore", invalid="ignore"):
        scaled = (np.log10(values[valid]) - GRID_LOG_MIN) / (GRID_LOG_MAX - GRID_LOG_MIN)
    quantized[valid] = np.clip(np.round(scaled * 254) + 1, 1, 255).astype(np.uint8)

    dates = pd.to_datetime(chl[time_name].values).to_period("M").astype(str).tolist()
    monthly_median = np.nanmedian(np.where(valid, values, np.nan).reshape(values.shape[0], -1), axis=1)
    data = gzip.compress(np.ascontiguousarray(quantized).tobytes(), compresslevel=9)
    return {
        "schema_version": "1.0",
        "generated_at": pd.Timestamp.now("UTC").isoformat(),
        "source": "CMEMS biogeochemistry reanalysis",
        "variable": "chl",
        "units": "mg m-3",
        "depth": {"min_m": 0, "max_m": 5, "aggregation": "mean"},
        "period": {"start": dates[0], "end": dates[-1]},
        "time": dates,
        "grid": {
            "latitude": np.asarray(chl[lat_name].values, dtype=float).round(6).tolist(),
            "longitude": np.asarray(chl[lon_name].values, dtype=float).round(6).tolist(),
            "shape": [int(values.shape[1]), int(values.shape[2])],
            "data_order": ["time", "latitude", "longitude"],
        },
        "encoding": {
            "type": "uint8-log10-gzip-base64",
            "missing": 0,
            "valid_min": 1,
            "valid_max": 255,
            "log10_min": GRID_LOG_MIN,
            "log10_max": GRID_LOG_MAX,
            "decode": "10 ** (log10_min + (value - 1) / 254 * (log10_max - log10_min))",
        },
        "regional_median": [None if not np.isfinite(value) else round(float(value), 8) for value in monthly_median],
        "data_gzip_base64": base64.b64encode(data).decode("ascii"),
    }
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
    parser.add_argument("--zooplankton-hindcast", type=Path, default=DEFAULT_ZOOPLANKTON_HINDCAST)
    parser.add_argument("--zooplankton-operational", type=Path, default=DEFAULT_ZOOPLANKTON_OPERATIONAL)
    parser.add_argument("--stock", default="toda_costa", choices=("toda_costa", "norte_centro", "sur"))
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--interpolate-biomass",
        action="store_true",
        help="Añade una serie interpolada solo para visualización; no extrapola.",
    )
    parser.add_argument(
        "--experiment-c",
        action="store_true",
        help="Genera también el panel y JSON F-Z-A del Experimento C.",
    )
    parser.add_argument(
        "--output-suffix",
        default="",
        help="Sufijo para no sobrescribir outputs existentes, por ejemplo _interpolated.",
    )
    args = parser.parse_args()

    environment = load_environment(args)
    biomass = load_biomass(args.biomass, args.stock)
    interval_panel = build_interval_panel(environment, biomass)
    monitoring = build_monitoring_series(environment, biomass)
    if args.interpolate_biomass:
        monitoring = add_biomass_interpolation(monitoring)
    experiment_c = None
    if args.experiment_c:
        if "biomass_total_t_interpolated" not in monitoring:
            monitoring = add_biomass_interpolation(monitoring)
            print("Experimento C: se activó interpolación de biomasa para visualización")
        zooplankton = load_zooplankton(args.zooplankton_hindcast, args.zooplankton_operational)
        experiment_c = build_experiment_c_panel(environment, monitoring, zooplankton)
    quality = build_quality_report(environment, interval_panel, monitoring)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    suffix = args.output_suffix
    interval_path = args.output_dir / f"panel_experiments_ab{suffix}.csv"
    monitoring_path = args.output_dir / f"monitoring_series_ab{suffix}.csv"
    monitoring_json_path = args.output_dir / f"monitoring_series_ab{suffix}.json"
    grid_json_path = args.output_dir / f"monitoring_grid_chlorophyll{suffix}.json"
    quality_path = args.output_dir / f"panel_quality_report{suffix}.csv"
    interval_panel.to_csv(interval_path, index=False)
    monitoring.to_csv(monitoring_path, index=True, date_format="%Y-%m-%d")
    monitoring_json_path.write_text(
        json.dumps(build_web_payload(monitoring), ensure_ascii=False, allow_nan=False),
        encoding="utf-8",
    )
    grid_json_path.write_text(
        json.dumps(build_chlorophyll_grid_payload(args.bgc), ensure_ascii=False, allow_nan=False, separators=(",", ":")),
        encoding="utf-8",
    )
    quality.to_csv(quality_path, index=False)
    if experiment_c is not None:
        experiment_c_path = args.output_dir / f"experiment_c_panel{suffix}.csv"
        experiment_c_json_path = args.output_dir / f"experiment_c_panel{suffix}.json"
        experiment_c.to_csv(experiment_c_path, index=True, index_label="date", date_format="%Y-%m-%d")
        experiment_c_json_path.write_text(
            json.dumps(build_experiment_c_payload(experiment_c), ensure_ascii=False, allow_nan=False),
            encoding="utf-8",
        )
        complete = experiment_c[["phytoplankton_carbon", "zooplankton", "biomass_anchoveta"]].notna().all(axis=1)
        print(f"Panel Experimento C: {experiment_c_path} ({int(complete.sum())} estados F-Z-A completos)")
        print(f"JSON Experimento C:   {experiment_c_json_path}")
    print(f"Panel por intervalos: {interval_path} ({len(interval_panel)} cruceros)")
    print(f"Serie de monitoreo:    {monitoring_path} ({len(monitoring)} meses)")
    print(f"Serie JSON para web:    {monitoring_json_path}")
    print(f"Grilla JSON para mapa:  {grid_json_path}")
    print(f"Reporte de calidad:     {quality_path}")
    print(f"Biomasa observada: {int(monitoring['biomass_observed'].sum())} meses; sin interpolación")
    print("Variables faltantes deliberadamente: oni, distance_coast")


if __name__ == "__main__":
    main()

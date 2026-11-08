#!/usr/bin/env python3
"""Prepare the exploratory ANCHOVETA 360 statistical panels.

This script deliberately keeps cruise biomass observations irregular. It only
interpolates environmental predictors at the campaign midpoint; it never
creates interpolated biomass observations.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "data" / "processed" / "tables"
DEFAULT_BIOMASS = ROOT / "data" / "biomasa_cruceros.csv"
DEFAULT_OUTPUT = TABLES / "exploratory_cruise_panel.csv"

REGIONS = {
    "antarctic": ["peninsula_antarctica", "bellingshausen"],
    "south_pacific": ["south_pacific_intermediate", "south_pacific_subtropical"],
    "transition": ["transition_humboldt"],
}

DEPTH = "subsurface_100_200m"
REMOTE_VARS = ["thetao_anom", "so_anom", "uo_anom", "vo_anom", "o2_anom"]


def parse_date(value: object) -> pd.Timestamp:
    return pd.to_datetime(value, errors="coerce")


def load_cruises(path: Path, stock: str) -> pd.DataFrame:
    frame = pd.read_csv(path)
    required = {"crucero", "fecha_inicio", "fecha_fin", "biomasa_t"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Biomasa: faltan columnas {sorted(missing)}")
    frame["fecha_inicio"] = frame["fecha_inicio"].map(parse_date)
    frame["fecha_fin"] = frame["fecha_fin"].map(parse_date)
    frame["biomasa_t"] = pd.to_numeric(frame["biomasa_t"], errors="coerce")
    if "stock" not in frame.columns:
        raise ValueError("Biomasa: falta la columna stock")
    frame = frame.loc[frame["stock"].eq(stock)].copy()
    if frame.empty:
        raise ValueError(f"No hay registros para stock={stock!r}")
    frame = frame.dropna(subset=["fecha_inicio", "fecha_fin", "biomasa_t"]).copy()
    frame = frame.loc[frame["fecha_fin"] >= frame["fecha_inicio"]].copy()
    frame["fecha_centro"] = frame["fecha_inicio"] + (
        frame["fecha_fin"] - frame["fecha_inicio"]
    ) / 2
    frame["date"] = frame["fecha_centro"].dt.to_period("M").dt.to_timestamp()
    frame["interval_days"] = (
        frame["fecha_fin"] - frame["fecha_inicio"]
    ).dt.days + 1
    if frame["crucero"].duplicated().any():
        raise ValueError("Hay códigos de crucero duplicados en la respuesta biológica")
    return frame.sort_values("fecha_inicio").reset_index(drop=True)


def load_interval_environment() -> pd.DataFrame:
    path = TABLES / "panel_experiments_ab.csv"
    frame = pd.read_csv(path)
    frame["fecha_inicio"] = pd.to_datetime(frame["fecha_inicio"], errors="coerce")
    frame["fecha_fin"] = pd.to_datetime(frame["fecha_fin"], errors="coerce")
    return frame


def load_connectivity() -> pd.DataFrame:
    path = TABLES / "connectivity_panel_monthly.csv"
    frame = pd.read_csv(path)
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    return frame


def interpolate_at(
    series: pd.Series, dates: pd.Series, target: pd.Timestamp
) -> tuple[float, str]:
    valid = pd.to_numeric(series, errors="coerce").notna() & dates.notna()
    x = dates.loc[valid].astype("datetime64[ns]").astype("int64").to_numpy(dtype=float)
    y = pd.to_numeric(series.loc[valid], errors="coerce").to_numpy(dtype=float)
    if len(x) == 0 or pd.isna(target):
        return np.nan, "missing"
    order = np.argsort(x)
    x, y = x[order], y[order]
    tx = float(pd.Timestamp(target).value)
    if tx < x[0] or tx > x[-1]:
        return np.nan, "outside_range"
    exact = np.where(x == tx)[0]
    if len(exact):
        return float(y[exact[0]]), "observed_month"
    return float(np.interp(tx, x, y)), "interpolated_linear"


def exact_month_value(
    series: pd.Series, dates: pd.Series, target: pd.Timestamp
) -> tuple[float, str]:
    """Return the available monthly value without temporal interpolation."""
    target_month = pd.Timestamp(target).to_period("M").to_timestamp()
    matches = pd.to_datetime(dates).eq(target_month)
    values = pd.to_numeric(series.loc[matches], errors="coerce").dropna()
    if values.empty:
        return np.nan, "missing_month"
    return float(values.iloc[0]), "observed_month_no_interpolation"


def regional_series(connectivity: pd.DataFrame) -> pd.DataFrame:
    """Create low-dimensional, pre-specified regional anomaly indices."""
    x = connectivity.loc[connectivity["depth_band"].eq(DEPTH)].copy()
    rows: list[dict[str, object]] = []
    for date, month in x.groupby("date", sort=True):
        row: dict[str, object] = {"date": date}
        for block, regions in REGIONS.items():
            subset = month.loc[month["region"].isin(regions)]
            for variable in REMOTE_VARS:
                row[f"{block}_{variable}"] = subset[variable].mean()
        rows.append(row)
    result = pd.DataFrame(rows).sort_values("date")

    # Standardize each monthly regional series over the full available period,
    # then average the pre-specified physical indicators. This is an index for
    # exploration, not a transported-water or causal connectivity measure.
    score_columns: list[str] = []
    for block in REGIONS:
        for variable in REMOTE_VARS:
            column = f"{block}_{variable}"
            values = pd.to_numeric(result[column], errors="coerce")
            sd = values.std(ddof=1)
            zcolumn = f"{column}_z"
            result[zcolumn] = (values - values.mean()) / sd if sd and np.isfinite(sd) else np.nan
            score_columns.append(zcolumn)
    result["connectivity_index_100_200"] = result[score_columns].mean(axis=1)
    return result


def aggregate_interval(connectivity: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> dict[str, float]:
    x = connectivity.loc[
        (connectivity["date"] >= start.to_period("M").to_timestamp())
        & (connectivity["date"] <= end.to_period("M").to_timestamp())
        & connectivity["depth_band"].eq(DEPTH)
    ]
    result: dict[str, float] = {}
    for block, regions in REGIONS.items():
        subset = x.loc[x["region"].isin(regions)]
        for variable in ["thetao_anom", "so_anom", "uo_anom", "vo_anom", "o2_anom"]:
            result[f"{block}_{variable}_interval"] = float(subset[variable].mean()) if not subset.empty else np.nan
    return result


def prepare(
    cruises: pd.DataFrame,
    interval_environment: pd.DataFrame,
    connectivity: pd.DataFrame,
    interpolate_predictors: bool = True,
) -> pd.DataFrame:
    regional = regional_series(connectivity)
    env_dates = regional["date"]
    output_rows: list[dict[str, object]] = []

    for _, cruise in cruises.iterrows():
        row = cruise.to_dict()
        matching = interval_environment.loc[interval_environment["crucero"].eq(cruise["crucero"])]
        if len(matching):
            for key, value in matching.iloc[0].to_dict().items():
                if key not in row and key not in {"fecha_inicio", "fecha_fin"}:
                    row[f"ab_{key}"] = value
        row.update(aggregate_interval(connectivity, cruise["fecha_inicio"], cruise["fecha_fin"]))

        # Midpoint interpolation is used only for environmental predictors.
        value_at = interpolate_at if interpolate_predictors else exact_month_value
        for column in regional.columns:
            if column == "date":
                continue
            value, kind = value_at(regional[column], env_dates, cruise["fecha_centro"])
            row[f"center_{column}"] = value
            row[f"center_{column}_source"] = kind
        # Pre-specified lags are generated for the connectivity index only.
        # They are environmental covariates, not extra biological observations.
        for lag in (0, 3, 6, 12, 18, 24):
            target = cruise["fecha_centro"] - pd.DateOffset(months=lag)
            value, kind = value_at(
                regional["connectivity_index_100_200"], env_dates, target
            )
            row[f"center_connectivity_index_100_200_lag{lag}"] = value
            row[f"center_connectivity_index_100_200_lag{lag}_source"] = kind
        output_rows.append(row)

    result = pd.DataFrame(output_rows)
    result["log10_biomass"] = np.log10(pd.to_numeric(result["biomasa_t"], errors="coerce"))
    result["biomass_value_type"] = "observed_cruise"
    result["environment_interpolation_scope"] = "predictors_only_midpoint_linear"
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--biomass", type=Path, default=DEFAULT_BIOMASS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--stock",
        default="toda_costa",
        help="Cobertura biológica a analizar; no mezclar stocks/regiones (default: toda_costa)",
    )
    parser.add_argument(
        "--no-interpolation",
        action="store_true",
        help="Usa únicamente el valor del mes central, sin interpolar predictores",
    )
    args = parser.parse_args()

    cruises = load_cruises(args.biomass, args.stock)
    interval_environment = load_interval_environment()
    connectivity = load_connectivity()
    result = prepare(
        cruises,
        interval_environment,
        connectivity,
        interpolate_predictors=not args.no_interpolation,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False, date_format="%Y-%m-%d")

    metadata = {
        "response": "biomasa_t, observed cruise-level IMARPE records",
        "stock_filter": args.stock,
        "n_cruises_with_complete_dates": int(len(result)),
        "date_min": result["fecha_inicio"].min().isoformat(),
        "date_max": result["fecha_fin"].max().isoformat(),
        "environment_source": "connectivity_panel_monthly.csv and panel_experiments_ab.csv",
        "connectivity_depth_band": DEPTH,
        "interpolation": (
            "none; monthly value at cruise midpoint month"
            if args.no_interpolation
            else "linear interpolation of environmental predictors at cruise midpoint only"
        ),
        "biomass_interpolated": False,
        "remote_blocks": REGIONS,
        "output": str(args.output),
    }
    metadata_path = args.output.with_name("exploratory_cruise_panel_metadata.json")
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(metadata, indent=2, ensure_ascii=False))
    print(f"Prepared panel: {args.output} ({len(result)} cruises, {len(result.columns)} columns)")


if __name__ == "__main__":
    main()

"""Ejecuta la Fase 3 de A para el monitor, ICEN vs Niño 1+2.

En modo monitor usa la biomasa mensual interpolada entre cruceros. La etiqueta
``biomass_value_type`` se conserva en el resultado y no se presenta como una
observación científica.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from nasahackaton.models.experiment_a import fit_quadratic_baseline


WINDOWS = {
    "train": ("1998-01-01", "2014-12-31"),
    "validation": ("2015-01-01", "2019-12-31"),
    "test": ("2020-01-01", "2024-12-31"),
    "prospective": ("2025-01-01", "2099-12-31"),
}
ENSO_HOLDOUTS = {
    "el_nino_2015_2016": ("2015-01-01", "2016-12-31"),
    "el_nino_2023_2024": ("2023-01-01", "2024-12-31"),
    "prospective_el_nino_2026_2027": ("2026-10-01", "2027-12-31"),
}


def _window(frame: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    dates = pd.Series(pd.to_datetime(frame["date"]), index=frame.index)
    return frame[dates.between(start, end)].copy()


def _predict(frame: pd.DataFrame, fit: dict) -> pd.Series:
    variables = fit["variables"]
    data = frame.dropna(subset=variables)
    x = data[variables].to_numpy(float)
    means = pd.Series(fit["means"])[variables].to_numpy(float)
    std = pd.Series(fit["std"])[variables].to_numpy(float)
    z = (x - means) / std
    design = pd.DataFrame({"intercept": 1.0}, index=data.index)
    for i, variable in enumerate(variables):
        design[f"{variable}_linear"] = z[:, i]
    for i, variable in enumerate(variables):
        design[f"{variable}_quadratic"] = z[:, i] ** 2
    prediction = design.to_numpy() @ pd.Series(fit["coefficients"]).to_numpy(float)
    return pd.Series(prediction, index=data.index, name="prediction")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/processed/tables/monitoring_series_ab_interpolated.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/models/experiment_a_monitor.json"))
    parser.add_argument("--predictions-output", type=Path, default=Path("data/processed/tables/experiment_a_monitor_predictions.csv"))
    parser.add_argument("--observed-only", action="store_true", help="Usa solo cruceros observados del panel A/B.")
    parser.add_argument("--min-observations", type=int, default=20)
    args = parser.parse_args()

    frame = pd.read_csv(args.input, parse_dates=["date"])
    if args.observed_only:
        frame = frame[frame["biomass_value_type"].eq("observed")].copy()
        response = "biomass_total_t"
        mode = "observed_only"
    else:
        response = "biomass_total_t_interpolated"
        mode = "monitor_interpolated"
    frame["biomass_anchoveta"] = frame[response]
    results = {
        "model_family": "quadratic_baseline_monitor_ready",
        "response": response,
        "mode": mode,
        "biomass_quality_counts": frame["biomass_value_type"].value_counts(dropna=False).to_dict(),
        "variants": {},
        "windows": {name: {"start": start, "end": end} for name, (start, end) in WINDOWS.items()},
        "enso_holdouts": {name: {"start": start, "end": end} for name, (start, end) in ENSO_HOLDOUTS.items()},
        "minimum_observations": args.min_observations,
        "notes": [
            "ICEN y nino12 se ajustan como variantes separadas; no se incluyen juntos.",
            "La validacion debe ser temporal y por eventos ENSO, no aleatoria.",
            "Este script queda preparado para reemplazar fit_quadratic_baseline por un GAM Tweedie cuando exista cobertura suficiente.",
        ],
    }
    fitted_models = {}
    for climate in ("icen", "nino12"):
        climate_result = {}
        usable = frame.dropna(subset=[climate]).copy()
        for name, (start, end) in WINDOWS.items():
            block = _window(usable, start, end)
            entry = {"n": len(block), "status": "not_fitted"}
            if name == "train" and len(block) >= args.min_observations:
                fit_frame = block.copy()
                fit_frame["oni"] = fit_frame[climate]
                available = [column for column in ("sst", "sss", "oxygen", "oni") if fit_frame[column].notna().mean() >= 0.8]
                fit = fit_quadratic_baseline(fit_frame, base_variables=available)
                fitted_models[climate] = fit
                entry["fit"] = fit
                entry["status"] = "fitted_monitor_baseline"
                for eval_name, (eval_start, eval_end) in WINDOWS.items():
                    eval_block = _window(usable, eval_start, eval_end).copy()
                    eval_block["oni"] = eval_block[climate]
                    eval_block["biomass_anchoveta"] = eval_block[response]
                    pred = _predict(eval_block, fit)
                    actual = eval_block.loc[pred.index, "biomass_anchoveta"].dropna()
                    pred = pred.loc[actual.index]
                    if len(pred):
                        entry.setdefault("metrics", {})[eval_name] = {
                            "n": int(len(pred)),
                            "rmse_t": float(((actual - pred) ** 2).mean() ** 0.5),
                            "mae_t": float((actual - pred).abs().mean()),
                        }
            elif name == "train":
                entry["reason"] = "insufficient_observed_cruises"
            climate_result[name] = entry
        climate_result["enso_holdouts"] = {
            name: {"n": len(_window(usable, start, end)), "status": "holdout_only"}
            for name, (start, end) in ENSO_HOLDOUTS.items()
        }
        results["variants"][climate] = climate_result

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    predictions = frame[["date", "biomass_value_type"]].copy()
    predictions["biomass_actual_t"] = frame[response]
    predictions = predictions.set_index("date")
    for climate, fit in fitted_models.items():
        prediction_frame = frame.set_index("date").copy()
        prediction_frame["oni"] = prediction_frame[climate]
        predictions[f"prediction_{climate}_t"] = _predict(prediction_frame, fit).reindex(predictions.index)
    args.predictions_output.parent.mkdir(parents=True, exist_ok=True)
    predictions.reset_index().to_csv(args.predictions_output, index=False, date_format="%Y-%m-%d")
    print(f"Plan de Fase 3 guardado en {args.output}")
    print(f"Predicciones del monitor guardadas en {args.predictions_output}")
    for climate, blocks in results["variants"].items():
        counts = [f"{name}={entry['n']}" for name, entry in blocks.items() if "n" in entry]
        print(f"{climate}: " + ", ".join(counts))


if __name__ == "__main__":
    main()

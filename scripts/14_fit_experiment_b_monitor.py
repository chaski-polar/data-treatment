"""Ejecuta la Fase 4: compara A contra modelos B de productividad.

Usa la biomasa interpolada solo para el monitor y conserva su tipo de calidad.
Cada variante se ajusta con los primeros años y se evalúa en bloques posteriores.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from nasahackaton.models.experiment_a import fit_quadratic_baseline


WINDOWS = {
    "train": ("1998-01-01", "2014-12-31"),
    "validation": ("2015-01-01", "2019-12-31"),
    "test": ("2020-01-01", "2024-12-31"),
    "prospective": ("2025-01-01", "2099-12-31"),
}
BASE = ["sst", "sss", "oxygen"]


def window(frame: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    dates = pd.Series(pd.to_datetime(frame["date"]), index=frame.index)
    return frame[dates.between(start, end)].copy()


def predict(frame: pd.DataFrame, fit: dict) -> pd.Series:
    variables = fit["variables"]
    data = frame.dropna(subset=variables)
    x = data[variables].to_numpy(float)
    means = np.array([fit["means"][v] for v in variables])
    std = np.array([fit["std"][v] for v in variables])
    z = (x - means) / std
    design = np.column_stack([np.ones(len(z)), z, z**2])
    return pd.Series(design @ np.asarray(fit["coefficients"]), index=data.index)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/processed/tables/monitoring_series_ab_interpolated.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/models/experiment_b_monitor.json"))
    args = parser.parse_args()
    frame = pd.read_csv(args.input, parse_dates=["date"])
    frame["biomass_anchoveta"] = frame["biomass_total_t_interpolated"]

    variants = {
        "B0_A_only": BASE,
        "B1_add_chlorophyll": [*BASE, "chlorophyll_a"],
        "B2_add_phytoplankton_carbon": [*BASE, "phytoplankton_carbon"],
        "B3_add_productivity": [*BASE, "chlorophyll_a", "phytoplankton_carbon", "nitrate", "phosphate"],
    }
    result = {
        "model_family": "quadratic_productivity_monitor_baselines",
        "response": "biomass_total_t_interpolated",
        "quality_counts": frame["biomass_value_type"].value_counts().to_dict(),
        "windows": {k: {"start": v[0], "end": v[1]} for k, v in WINDOWS.items()},
        "variants": {},
    }
    for name, requested in variants.items():
        usable = frame.copy()
        # El monitor puede operar con variables disponibles; se elimina solo lo
        # que no tenga al menos 80% de cobertura en el bloque de entrenamiento.
        train = window(usable, *WINDOWS["train"])
        variables = [v for v in requested if v in train and train[v].notna().mean() >= 0.8]
        fit_frame = train.dropna(subset=["biomass_anchoveta", *variables])
        entry = {"requested_variables": requested, "variables": variables, "n_train": len(fit_frame), "status": "not_fitted"}
        if len(fit_frame) >= 20 and len(variables):
            fit = fit_quadratic_baseline(fit_frame, base_variables=variables)
            entry["fit"] = fit
            entry["status"] = "fitted"
            entry["metrics"] = {}
            for split, bounds in WINDOWS.items():
                block = window(usable, *bounds)
                pred = predict(block, fit)
                actual = block.loc[pred.index, "biomass_anchoveta"].dropna()
                pred = pred.loc[actual.index]
                entry["metrics"][split] = {
                    "n": int(len(pred)),
                    "rmse_t": float(np.sqrt(np.mean((actual - pred) ** 2))) if len(pred) else None,
                    "mae_t": float(np.mean(np.abs(actual - pred))) if len(pred) else None,
                }
        else:
            entry["reason"] = "insufficient_training_rows_or_predictors"
        result["variants"][name] = entry
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    print(f"Experimento B guardado en {args.output}")
    for name, entry in result["variants"].items():
        metric = entry.get("metrics", {}).get("validation", {})
        print(f"{name}: vars={entry['variables']}, validation_RMSE={metric.get('rmse_t')}")


if __name__ == "__main__":
    main()

"""Ejecuta la Fase 5: calibración exploratoria dinámica F-Z-A para el monitor."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import least_squares


WINDOWS = {
    "train": ("1998-01-01", "2014-12-31"),
    "validation": ("2015-01-01", "2019-12-31"),
    "test": ("2020-01-01", "2024-12-31"),
}
STATE_COLUMNS = ["phytoplankton_carbon", "zooplankton", "biomass_anchoveta"]


def normalized_derivatives(frame: pd.DataFrame, scale: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    state = frame[STATE_COLUMNS].to_numpy(float) / scale.to_numpy(float)
    dates = pd.to_datetime(frame["date"])
    month_code = dates.dt.year.to_numpy(int) * 12 + dates.dt.month.to_numpy(int)
    dt = np.diff(month_code).astype(float)
    left = state[:-1]
    right = state[1:]
    valid = (dt == 1.0) & np.isfinite(left).all(axis=1) & np.isfinite(right).all(axis=1)
    return (left[valid], (right[valid] - left[valid]) / dt[valid, None])


def rhs(params: np.ndarray, state: np.ndarray) -> np.ndarray:
    # Parámetros positivos: rF, KF, gFZ, gFA, rZ, gZA, mF, mZ, mA.
    r_f, k_f, g_fz, g_fa, r_z, g_za, m_f, m_z, m_a = params
    f, z, a = state.T
    h = 0.8
    grazing_fz = g_fz * f * z / (h + f)
    grazing_fa = g_fa * f * a / (h + f)
    grazing_za = g_za * z * a / (h + z)
    return np.column_stack([
        r_f * f * (1 - f / k_f) - grazing_fz - grazing_fa - m_f * f,
        1.55 * grazing_fz - grazing_za - m_z * z,
        0.50 * grazing_fa + 0.70 * grazing_za - m_a * a,
    ])


def fit_block(frame: pd.DataFrame, scale: pd.Series) -> dict:
    states, derivatives = normalized_derivatives(frame, scale)
    if len(states) < 12:
        return {"status": "not_fitted", "n_monthly_transitions": int(len(states)), "reason": "fewer_than_12_transitions"}
    initial = np.array([1.2, 1.0, 2.0, 0.7, 1.55, 0.9, 0.02, 0.03, 0.25])
    result = least_squares(
        lambda p: (rhs(p, states) - derivatives).ravel(),
        initial,
        bounds=(np.full(9, 1e-8), np.full(9, 20.0)),
        loss="soft_l1",
        f_scale=0.1,
        max_nfev=5000,
    )
    fitted = rhs(result.x, states)
    return {
        "status": "fitted_exploratory",
        "n_monthly_transitions": int(len(states)),
        "parameters": dict(zip(["rF", "KF", "gFZ", "gFA", "rZ", "gZA", "mF", "mZ", "mA"], result.x.tolist())),
        "rmse_normalized_derivative": float(np.sqrt(np.mean((fitted - derivatives) ** 2))),
        "optimizer_cost": float(result.cost),
        "success": bool(result.success),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/processed/tables/experiment_c_panel_prepared.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/models/experiment_c_monitor.json"))
    args = parser.parse_args()
    frame = pd.read_csv(args.input, parse_dates=["date"]).sort_values("date")
    # Solo estados completos; A puede ser observado o interpolado, ambos válidos para monitor.
    frame = frame.dropna(subset=STATE_COLUMNS).copy()
    train = frame[frame["date"].between(*WINDOWS["train"])]
    scale = train[STATE_COLUMNS].median().replace(0, np.nan).fillna(1.0)
    result = {
        "model_family": "FZA_monthly_derivative_calibration_exploratory",
        "states": {"F": "phytoplankton_carbon", "Z": "zooplankton", "A": "biomass_anchoveta"},
        "units": {"F": "mg C m-3", "Z": "mg C m-2", "A": "t"},
        "response_quality": frame["biomass_value_type"].value_counts().to_dict(),
        "normalization_scale_median_train": scale.to_dict(),
        "warnings": [
            "Z sigue en mg C m-2 y F en mg C m-3; los parámetros son de estados normalizados.",
            "La calibración usa diferencias mensuales y biomasa interpolada para el monitor.",
            "No interpretar los parámetros como tasas biológicas publicables.",
        ],
        "windows": {},
    }
    for name, (start, end) in WINDOWS.items():
        block = frame[frame["date"].between(start, end)]
        result["windows"][name] = {"rows": len(block), **fit_block(block, scale)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    print(f"Experimento C guardado en {args.output}")
    for name, block in result["windows"].items():
        print(f"{name}: {block['status']}, transiciones={block.get('n_monthly_transitions', 0)}")


if __name__ == "__main__":
    main()

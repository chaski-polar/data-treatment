"""Fase 6: genera escenarios prospectivos de El Niño para el monitor.

La salida cubre los seis meses posteriores al último mes ambiental disponible.
Los escenarios no son observaciones: combinan climatología mensual, relaciones
históricas con ICEN y las ecuaciones calibradas en las fases 3–5.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


SCENARIO_MULTIPLIERS = {"weak": 0.70, "central": 1.00, "intense": 1.20}
ENVIRONMENT = ["sst", "sss", "oxygen", "chlorophyll_a", "phytoplankton_carbon", "nitrate", "phosphate"]


def predict(frame: pd.DataFrame, fit: dict) -> pd.Series:
    variables = fit["variables"]
    data = frame.dropna(subset=variables)
    x = data[variables].to_numpy(float)
    means = np.array([fit["means"][v] for v in variables])
    std = np.array([fit["std"][v] for v in variables])
    z = (x - means) / std
    design = np.column_stack([np.ones(len(z)), z, z**2])
    return pd.Series(design @ np.asarray(fit["coefficients"]), index=data.index)


def fit_slope(frame: pd.DataFrame, variable: str) -> float:
    data = frame[[variable, "icen"]].dropna()
    if len(data) < 24 or data["icen"].std() == 0:
        return 0.0
    return float(np.cov(data[variable], data["icen"], ddof=1)[0, 1] / data["icen"].var())


def ecological_rhs(params: dict[str, float], state: np.ndarray) -> np.ndarray:
    r_f, k_f = params["rF"], params["KF"]
    g_fz, g_fa = params["gFZ"], params["gFA"]
    g_za = params["gZA"]
    m_f, m_z, m_a = params["mF"], params["mZ"], params["mA"]
    f, z, a = state
    h = 0.8
    grazing_fz = g_fz * f * z / (h + f)
    grazing_fa = g_fa * f * a / (h + f)
    grazing_za = g_za * z * a / (h + z)
    return np.array([
        r_f * f * (1 - f / k_f) - grazing_fz - grazing_fa - m_f * f,
        1.55 * grazing_fz - grazing_za - m_z * z,
        0.50 * grazing_fa + 0.70 * grazing_za - m_a * a,
    ])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/processed/tables/monitoring_series_ab_interpolated.csv"))
    parser.add_argument("--c-panel", type=Path, default=Path("data/processed/tables/experiment_c_panel_prepared.csv"))
    parser.add_argument("--a-model", type=Path, default=Path("data/processed/models/experiment_a_monitor.json"))
    parser.add_argument("--b-model", type=Path, default=Path("data/processed/models/experiment_b_monitor.json"))
    parser.add_argument("--c-model", type=Path, default=Path("data/processed/models/experiment_c_monitor.json"))
    parser.add_argument("--horizon", type=int, default=6, choices=(3, 6))
    parser.add_argument("--output", type=Path, default=Path("data/processed/tables/enso_scenarios_monitor.csv"))
    parser.add_argument("--metadata", type=Path, default=Path("data/processed/models/enso_scenarios_monitor.json"))
    args = parser.parse_args()

    env = pd.read_csv(args.input, parse_dates=["date"]).sort_values("date")
    c_panel = pd.read_csv(args.c_panel, parse_dates=["date"]).sort_values("date")
    a_model = json.loads(args.a_model.read_text(encoding="utf-8"))
    b_model = json.loads(args.b_model.read_text(encoding="utf-8"))
    c_model = json.loads(args.c_model.read_text(encoding="utf-8"))
    a_icen = a_model["variants"]["icen"]["train"]["fit"]
    a_nino = a_model["variants"]["nino12"]["train"]["fit"]
    b3 = b_model["variants"]["B3_add_productivity"]["fit"]
    c_params = c_model["windows"]["train"]["parameters"]
    c_scale = pd.Series(c_model["normalization_scale_median_train"])

    last_date = env["date"].max()
    future_dates = pd.date_range(last_date + pd.offsets.MonthBegin(1), periods=args.horizon, freq="MS")
    month_clim = env.groupby(env["date"].dt.month)[ENVIRONMENT + ["icen"]].median()
    central_trajectory = np.array([3.8, 4.0, 3.7, 3.2, 2.8, 2.3])[:args.horizon]
    slopes = {variable: fit_slope(env, variable) for variable in ENVIRONMENT}
    rows = []
    for scenario, multiplier in SCENARIO_MULTIPLIERS.items():
        for i, date in enumerate(future_dates):
            icen = float(central_trajectory[i] * multiplier)
            base = month_clim.loc[date.month]
            values = {variable: float(base[variable] + slopes[variable] * (icen - base["icen"])) for variable in ENVIRONMENT}
            values["icen"] = icen
            # Relación histórica lineal para completar Niño 1+2 cuando el
            # producto futuro no esté disponible.
            relation = env[["icen", "nino12"]].dropna()
            nino12_slope = np.polyfit(relation["icen"], relation["nino12"], 1) if len(relation) >= 24 else [1.0, 0.0]
            values["nino12"] = float(nino12_slope[0] * icen + nino12_slope[1])
            values["date"] = date
            values["scenario"] = scenario
            values["horizon_month"] = i + 1
            values["scenario_multiplier"] = multiplier
            future = pd.DataFrame([values])
            future["oni"] = future["icen"]
            values["prediction_a_icen_t"] = float(predict(future, a_icen).iloc[0])
            future["oni"] = future["nino12"]
            values["prediction_a_nino12_t"] = float(predict(future, a_nino).iloc[0])
            values["prediction_b3_t"] = float(predict(pd.DataFrame([values]), b3).iloc[0])
            rows.append(values)

    output = pd.DataFrame(rows)
    # C comienza con F/Z actuales y A pronosticada por A-ICEN en el primer mes.
    c_latest = c_panel.dropna(subset=["phytoplankton_carbon", "zooplankton"]).iloc[-1]
    c_fit = c_model["windows"]["train"]
    for scenario in output["scenario"].unique():
        mask = output["scenario"].eq(scenario)
        first_a = output.loc[mask, "prediction_a_icen_t"].iloc[0]
        state = np.array([c_latest["phytoplankton_carbon"], c_latest["zooplankton"], first_a]) / c_scale[["phytoplankton_carbon", "zooplankton", "biomass_anchoveta"]].to_numpy()
        dynamic = []
        for _ in range(args.horizon):
            state = np.maximum(0.0, state + ecological_rhs(c_params, state))
            dynamic.append(state * c_scale[["phytoplankton_carbon", "zooplankton", "biomass_anchoveta"]].to_numpy())
        dynamic = np.asarray(dynamic)
        output.loc[mask, "c_f_dynamic"] = dynamic[:, 0]
        output.loc[mask, "c_z_dynamic"] = dynamic[:, 1]
        output.loc[mask, "c_a_dynamic"] = dynamic[:, 2]

    output["data_status"] = "scenario_not_observation"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output, index=False, date_format="%Y-%m-%d")
    metadata = {
        "horizon_months": args.horizon,
        "period": {"start": future_dates[0].strftime("%Y-%m-%d"), "end": future_dates[-1].strftime("%Y-%m-%d")},
        "scenarios": list(SCENARIO_MULTIPLIERS),
        "central_icen_path": central_trajectory.tolist(),
        "scenario_multipliers": SCENARIO_MULTIPLIERS,
        "last_observed_environment_month": last_date.strftime("%Y-%m-%d"),
        "c_initial_state_date": pd.Timestamp(c_latest["date"]).strftime("%Y-%m-%d"),
        "warnings": [
            "Todas las filas son escenarios, no observaciones futuras.",
            "Las variables ambientales futuras se construyen con climatologia mensual y pendientes historicas frente a ICEN.",
            "El Niño central sigue una trayectoria fuerte asumida para septiembre 2026–febrero 2027; actualizarla cuando haya un pronostico operativo nuevo.",
            "C usa el estado F/Z mas reciente disponible y A inicial de A-ICEN; sus salidas son simulacion exploratoria.",
        ],
    }
    args.metadata.parent.mkdir(parents=True, exist_ok=True)
    args.metadata.write_text(json.dumps(metadata, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    print(f"Escenarios guardados en {args.output} ({len(output)} filas)")
    print(f"Metadatos guardados en {args.metadata}")


if __name__ == "__main__":
    main()

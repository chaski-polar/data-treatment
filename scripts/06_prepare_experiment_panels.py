"""Prepara paneles separados y ventanas temporales para A, B y C.

Este script no interpola respuestas para ajustar modelos. La biomasa interpolada
se conserva únicamente en el panel de simulación/visualización de C.

Uso:
    .venv/bin/python scripts/06_prepare_experiment_panels.py
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "data/processed/tables"

BASE_A = ["sst", "sss", "oxygen", "distance_coast"]
CLIMATE = ["icen", "nino12"]
PRODUCTIVITY = ["chlorophyll_a", "phytoplankton_carbon", "nitrate", "phosphate", "kd490"]
SPLITS = {
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


def _read(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, parse_dates=["date"])
    return frame.set_index("date").sort_index()


def _write(frame: pd.DataFrame, path: Path) -> None:
    frame.to_csv(path, index=True, index_label="date", date_format="%Y-%m-%d")


def _split_counts(frame: pd.DataFrame, date_column: str = "date") -> dict:
    dates = pd.Series(
        pd.to_datetime(frame[date_column]) if date_column in frame else pd.to_datetime(frame.index),
        index=frame.index,
    )
    result = {}
    for name, (start, end) in SPLITS.items():
        mask = dates.between(start, end)
        result[name] = {"rows": int(mask.sum())}
    return result


def _event_counts(frame: pd.DataFrame, date_column: str = "date") -> dict:
    dates = pd.Series(
        pd.to_datetime(frame[date_column]) if date_column in frame else pd.to_datetime(frame.index),
        index=frame.index,
    )
    return {
        name: {"rows": int(dates.between(start, end).sum()), "start": start, "end": end}
        for name, (start, end) in ENSO_HOLDOUTS.items()
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--monitoring", type=Path, default=TABLES / "monitoring_series_ab.csv")
    parser.add_argument("--intervals", type=Path, default=TABLES / "panel_experiments_ab.csv")
    parser.add_argument("--experiment-c", type=Path, default=TABLES / "experiment_c_panel.csv")
    parser.add_argument("--output-dir", type=Path, default=TABLES)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    monitoring = _read(args.monitoring)
    intervals = pd.read_csv(args.intervals, parse_dates=["fecha_inicio", "fecha_fin"])
    c_panel = _read(args.experiment_c)

    # A/B: una fila por crucero, respuesta exclusivamente observada.
    observed = intervals[intervals["biomass_observed"].eq(True)].copy()
    observed["date"] = observed["fecha_inicio"].dt.to_period("M").dt.to_timestamp()
    a_columns = [c for c in ["date", "crucero", "fecha_inicio", "fecha_fin", "interval_days", "biomass_anchoveta", *BASE_A, *CLIMATE] if c in observed]
    b_columns = [c for c in [*a_columns, *PRODUCTIVITY, "chlorophyll_occci", "kd490", "hsi_abiotic", "hsi_trophic"] if c in observed]
    panel_a = observed[a_columns].sort_values("date")
    panel_b = observed[b_columns].sort_values("date")
    panel_a.to_csv(args.output_dir / "experiment_a_panel.csv", index=False, date_format="%Y-%m-%d")
    panel_b.to_csv(args.output_dir / "experiment_b_panel.csv", index=False, date_format="%Y-%m-%d")

    # C: conservar explícitamente los dos usos posibles de A.
    c_panel = c_panel.copy()
    c_panel["biomass_observed"] = c_panel["biomass_observed"].fillna(False).astype(bool)
    c_panel["biomass_fit_eligible"] = c_panel["biomass_observed"] & c_panel["biomass_anchoveta"].notna()
    c_panel["state_fit_eligible"] = c_panel[["phytoplankton_carbon", "zooplankton", "biomass_anchoveta"]].notna().all(axis=1) & c_panel["biomass_fit_eligible"]
    c_panel["simulation_eligible"] = c_panel[["phytoplankton_carbon", "zooplankton", "biomass_anchoveta"]].notna().all(axis=1)
    _write(c_panel, args.output_dir / "experiment_c_panel_prepared.csv")
    _write(c_panel[c_panel["state_fit_eligible"]], args.output_dir / "experiment_c_calibration_observed.csv")
    _write(c_panel[c_panel["simulation_eligible"]], args.output_dir / "experiment_c_simulation_states.csv")

    temporal = {
        "definition": "fixed temporal blocks; no random split",
        "windows": {name: {"start": start, "end": end} for name, (start, end) in SPLITS.items()},
        "experiment_a_observed_cruises": _split_counts(panel_a),
        "experiment_b_observed_cruises": _split_counts(panel_b),
        "experiment_c_months": _split_counts(c_panel),
        "experiment_c_calibration_states": _split_counts(c_panel[c_panel["state_fit_eligible"]]),
        "experiment_c_simulation_states": _split_counts(c_panel[c_panel["simulation_eligible"]]),
        "enso_event_holdouts": {
            "experiment_a_observed_cruises": _event_counts(panel_a),
            "experiment_b_observed_cruises": _event_counts(panel_b),
            "experiment_c_months": _event_counts(c_panel),
            "experiment_c_calibration_states": _event_counts(c_panel[c_panel["state_fit_eligible"]]),
        },
        "warnings": [
            "A y B usan solamente biomasa observada por crucero.",
            "La serie interpolada no es una observacion y solo se conserva para simulacion de C.",
            "Las ventanas temporales no sustituyen una validacion por eventos ENSO; tambien se requiere dejar fuera eventos completos.",
        ],
    }
    (args.output_dir / "temporal_splits.json").write_text(json.dumps(temporal, indent=2, ensure_ascii=False), encoding="utf-8")

    manifest = {
        "phase_1": {
            "experiment_a": "experiment_a_panel.csv",
            "experiment_b": "experiment_b_panel.csv",
            "experiment_c": "experiment_c_panel_prepared.csv",
            "experiment_c_calibration": "experiment_c_calibration_observed.csv",
            "experiment_c_simulation": "experiment_c_simulation_states.csv",
        },
        "phase_2": "temporal_splits.json",
        "rows": {
            "a_observed_cruises": len(panel_a),
            "b_observed_cruises": len(panel_b),
            "c_months": len(c_panel),
            "c_calibration_states": int(c_panel["state_fit_eligible"].sum()),
            "c_simulation_states": int(c_panel["simulation_eligible"].sum()),
        },
    }
    (args.output_dir / "experiment_panels_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

"""Ajusta Experimento A y guarda los parámetros estimados."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from nasahackaton.datasets.monthly_panel import load_panel
from nasahackaton.models.experiment_a import fit_quadratic_baseline


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data/processed/tables/panel_peru_monthly.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/models/experiment_a.json"))
    args = parser.parse_args()
    result = fit_quadratic_baseline(load_panel(args.input))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Experimento A guardado en {args.output}; n={result['n']}, RMSE={result['rmse']:.3g}")


if __name__ == "__main__":
    main()


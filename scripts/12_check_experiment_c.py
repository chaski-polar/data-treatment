"""Comprueba si el panel permite calibrar el sistema dinámico F-Z-A."""

from __future__ import annotations

import argparse
from pathlib import Path

from nasahackaton.datasets.monthly_panel import load_panel
from nasahackaton.models.experiment_c import validate_state_panel


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data/processed/tables/experiment_c_panel.csv"))
    args = parser.parse_args()
    states = validate_state_panel(load_panel(args.input))
    print(f"Experimento C: {len(states)} observaciones completas disponibles")


if __name__ == "__main__":
    main()


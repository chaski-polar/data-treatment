"""Punto de entrada para construir el panel mensual del proyecto."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from nasahackaton.datasets.monthly_panel import save_panel
from nasahackaton.models.synthetic import monthly_demo


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, help="Tabla mensual real en Parquet/CSV")
    parser.add_argument("--output", type=Path, default=Path("data/processed/tables/panel_peru_monthly.csv"))
    parser.add_argument("--demo", action="store_true", help="Genera datos sintéticos solo para probar el pipeline")
    args = parser.parse_args()
    if args.demo:
        panel = monthly_demo()
    elif args.input:
        panel = pd.read_parquet(args.input) if args.input.suffix == ".parquet" else pd.read_csv(args.input, index_col=0, parse_dates=True)
    else:
        raise SystemExit("Usa --input con datos reales o --demo para una prueba sintética")
    target = save_panel(panel, args.output)
    print(f"Panel guardado: {target} ({len(panel)} filas, {len(panel.columns)} columnas)")


if __name__ == "__main__":
    main()


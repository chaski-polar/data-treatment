#!/usr/bin/env python3
"""Generate PNG figures for the ANCHOVETA 360 exploratory report.

The script uses processed CSV outputs only. It does not download or modify
oceanographic data and is suitable for Google Colab.

Example from the data_treatment directory:

    python scripts/18_generate_exploratory_figures.py
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def resolve_root(value: str | None) -> Path:
    if value:
        root = Path(value).expanduser().resolve()
    elif (Path.cwd() / "data" / "processed").exists():
        root = Path.cwd()
    elif (Path.cwd() / "data_treatment" / "data" / "processed").exists():
        root = Path.cwd() / "data_treatment"
    else:
        root = Path.cwd()
    return root


def read_csv(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        print(f"[SKIP] Archivo no encontrado: {path}")
        return None
    try:
        return pd.read_csv(path)
    except Exception as exc:
        print(f"[SKIP] No se pudo leer {path}: {exc}")
        return None


def save(fig: plt.Figure, output: Path, name: str) -> None:
    output.mkdir(parents=True, exist_ok=True)
    path = output / name
    fig.savefig(path, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[OK] {path}")


def apply_date_axis(ax: plt.Axes) -> None:
    locator = mdates.AutoDateLocator()
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
    ax.grid(True, alpha=0.25)


def figure_biomass(panel: pd.DataFrame, output: Path) -> None:
    if panel is None or not {"fecha_centro", "biomasa_t"}.issubset(panel.columns):
        return
    x = panel.copy()
    x["fecha_centro"] = pd.to_datetime(x["fecha_centro"], errors="coerce")
    x["biomasa_t"] = pd.to_numeric(x["biomasa_t"], errors="coerce")
    x = x.dropna(subset=["fecha_centro", "biomasa_t"]).sort_values("fecha_centro")
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(x["fecha_centro"], x["biomasa_t"], color="#1769aa", alpha=0.55, linewidth=1.5)
    ax.scatter(x["fecha_centro"], x["biomasa_t"], color="#d95f02", s=55, zorder=3)
    for _, row in x.iterrows():
        ax.annotate(str(row.get("crucero", "")), (row["fecha_centro"], row["biomasa_t"]), xytext=(4, 5), textcoords="offset points", fontsize=8)
    ax.set_title("Biomasa observada por crucero IMARPE")
    ax.set_ylabel("Biomasa (t)")
    ax.set_xlabel("Fecha central de la campaña")
    apply_date_axis(ax)
    save(fig, output, "01_biomasa_cruceros.png")


def figure_model_metrics(metrics_a: pd.DataFrame | None, metrics_b: pd.DataFrame | None, output: Path) -> None:
    frames = [x for x in (metrics_a, metrics_b) if x is not None and not x.empty]
    if not frames:
        return
    combined = pd.concat(frames, ignore_index=True)
    combined["version"] = "interpolated"
    first_length = len(metrics_a) if metrics_a is not None else 0
    if metrics_b is not None:
        combined.loc[combined.index >= first_length, "version"] = "no_interpolation"
    if "model" not in combined or "adj_r2" not in combined or "loocv_rmse" not in combined:
        return
    order = ["A_local", "B_productivity", "C_connectivity"]
    labels = {"A_local": "A local", "B_productivity": "B productividad", "C_connectivity": "C conectividad"}
    fig, axes = plt.subplots(1, 2, figsize=(11, 5), constrained_layout=True)
    for ax, metric, title, color in [
        (axes[0], "adj_r2", "R² ajustado", "#1b9e77"),
        (axes[1], "loocv_rmse", "RMSE leave-one-cruise-out", "#7570b3"),
    ]:
        for version, group in combined.groupby("version", sort=False):
            values = []
            names = []
            for model in order:
                row = group.loc[group["model"].eq(model), metric]
                if not row.empty:
                    names.append(labels[model])
                    values.append(float(row.iloc[0]))
            positions = np.arange(len(values))
            offset = -0.18 if version == "interpolated" else 0.18
            ax.bar(positions + offset, values, width=0.34, label=version, color=color if version == "interpolated" else "#e7298a", alpha=0.85)
        ax.set_xticks(np.arange(len(order)), [labels[x] for x in order], rotation=20, ha="right")
        ax.set_title(title)
        ax.grid(True, axis="y", alpha=0.25)
    axes[0].set_ylim(bottom=0)
    axes[0].legend(frameon=False)
    fig.suptitle("Comparación de experimentos A, B y C")
    save(fig, output, "02_comparacion_modelos.png")


def figure_coefficients(coefs: pd.DataFrame | None, output: Path) -> None:
    if coefs is None or coefs.empty:
        return
    x = coefs.loc[~coefs["term"].eq("(Intercept)")].copy()
    if x.empty:
        return
    x["label"] = x["model"].str.replace("_", " ", regex=False) + " — " + x["term"]
    x = x.sort_values("estimate")
    fig, ax = plt.subplots(figsize=(10, max(4.5, 0.42 * len(x) + 1)))
    y = np.arange(len(x))
    ax.errorbar(x["estimate"], y, xerr=[x["estimate"] - x["bootstrap_low"], x["bootstrap_high"] - x["estimate"]], fmt="o", color="#1769aa", ecolor="#777777", capsize=3)
    ax.axvline(0, color="black", linewidth=1, alpha=0.7)
    ax.set_yticks(y, x["label"])
    ax.set_xlabel("Estimación del coeficiente con IC bootstrap 95 %")
    ax.set_title("Coeficientes de los modelos exploratorios")
    ax.grid(True, axis="x", alpha=0.25)
    save(fig, output, "03_coeficientes_bootstrap.png")


def figure_lags(lag_interp: pd.DataFrame | None, lag_nointerp: pd.DataFrame | None, output: Path) -> None:
    frames = []
    for frame, version in ((lag_interp, "interpolated"), (lag_nointerp, "no_interpolation")):
        if frame is None or frame.empty:
            continue
        x = frame.copy()
        x["version"] = version
        x["lag"] = x["variable"].str.extract(r"lag(\d+)")[0].astype(float)
        frames.append(x)
    if not frames:
        return
    x = pd.concat(frames, ignore_index=True).dropna(subset=["lag", "rho"])
    fig, ax = plt.subplots(figsize=(9, 5))
    for version, group in x.groupby("version", sort=False):
        group = group.sort_values("lag")
        ax.plot(group["lag"], group["rho"], marker="o", linewidth=2, label=version)
    ax.axhline(0, color="black", linewidth=1)
    ax.set_xticks([0, 3, 6, 12, 18, 24])
    ax.set_xlabel("Rezago (meses)")
    ax.set_ylabel("Correlación de Spearman")
    ax.set_title("Asociación exploratoria entre conectividad y biomasa")
    ax.legend(frameon=False)
    ax.grid(True, alpha=0.25)
    save(fig, output, "04_correlaciones_rezagos.png")


def figure_ram_lrt(ram: pd.DataFrame | None, output: Path) -> None:
    if ram is None or ram.empty:
        return
    x = ram.loc[ram["p-value"].notna()].copy()
    if x.empty:
        return
    x["covariance"] = x["comparison_type"].str.replace("GLS_ML_same_", "", regex=False)
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(x["covariance"], x["p-value"], color=["#66a61e", "#e6ab02"][: len(x)])
    ax.axhline(0.05, color="#d95f02", linestyle="--", label="α = 0.05")
    ax.set_ylabel("p-valor del contraste M0 vs M1")
    ax.set_title("Sensibilidad del contraste RAM a la autocorrelación")
    ax.set_ylim(0, max(0.35, float(x["p-value"].max()) * 1.25))
    ax.legend(frameon=False)
    ax.grid(True, axis="y", alpha=0.25)
    for bar, value in zip(bars, x["p-value"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{value:.3f}", ha="center", va="bottom")
    save(fig, output, "05_sensibilidad_ram_autocorrelacion.png")


def figure_connectivity_scatter(panel: pd.DataFrame | None, output: Path) -> None:
    if panel is None or panel.empty:
        return
    needed = {"log10_biomass", "center_connectivity_index_100_200_lag0"}
    if not needed.issubset(panel.columns):
        return
    x = panel.dropna(subset=list(needed)).copy()
    if len(x) < 3:
        return
    fig, ax = plt.subplots(figsize=(7, 5.5))
    ax.scatter(x["center_connectivity_index_100_200_lag0"], x["log10_biomass"], s=65, color="#1b9e77")
    for _, row in x.iterrows():
        ax.annotate(str(row.get("crucero", "")), (row["center_connectivity_index_100_200_lag0"], row["log10_biomass"]), xytext=(4, 4), textcoords="offset points", fontsize=8)
    ax.set_xlabel("Índice ambiental regional de conectividad")
    ax.set_ylabel("log10(biomasa observada)")
    ax.set_title("Biomasa e índice regional: asociación descriptiva")
    ax.grid(True, alpha=0.25)
    save(fig, output, "06_biomasa_vs_indice_conectividad.png")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="Directorio data_treatment; se autodetecta por defecto")
    parser.add_argument("--output", help="Carpeta de salida para PNG")
    args = parser.parse_args()
    root = resolve_root(args.root)
    tables = root / "data" / "processed" / "tables"
    analysis = root / "analysis_r" / "data"
    output = Path(args.output).expanduser().resolve() if args.output else tables / "figures_exploratory"

    cruise = read_csv(tables / "exploratory_cruise_panel_nointerp.csv")
    cruise_interp = read_csv(tables / "exploratory_cruise_panel.csv")
    metrics_nointerp = read_csv(analysis / "exploratory_nointerp" / "cruise_model_metrics.csv")
    metrics_interp = read_csv(analysis / "exploratory" / "cruise_model_metrics.csv")
    coefs = read_csv(analysis / "exploratory_nointerp" / "cruise_model_coefficients.csv")
    lags_nointerp = read_csv(analysis / "exploratory_nointerp" / "cruise_connectivity_lag_correlations.csv")
    lags_interp = read_csv(analysis / "exploratory" / "cruise_connectivity_lag_correlations.csv")
    ram = read_csv(analysis / "exploratory_nointerp" / "ram_block_lrt_corrected.csv")

    figure_biomass(cruise, output)
    figure_model_metrics(metrics_interp, metrics_nointerp, output)
    figure_coefficients(coefs, output)
    figure_lags(lags_interp, lags_nointerp, output)
    figure_ram_lrt(ram, output)
    figure_connectivity_scatter(cruise, output)
    print(f"Figuras exportadas en: {output}")


if __name__ == "__main__":
    main()

"""Contraste exploratorio de carbono fitoplanctónico Antártida–Humboldt.

Ejecutar desde data_treatment: uv run python scripts/18_test_phytoplankton_carbon_connectivity.py
No descarga datos, no interpola meses y no utiliza biomasa de anchoveta.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

ROOT = Path(__file__).resolve().parents[1]
REGIONS = ("peninsula_antarctica", "bellingshausen")
LAGS = (0, 3, 6, 12, 18, 24)
BAND = "surface_0_5m"


def calendar_hac(design: np.ndarray, residuals: np.ndarray,
                 dates: pd.DatetimeIndex, bandwidth: int) -> np.ndarray:
    """Newey–West con Bartlett; los huecos conservan su distancia calendario."""
    positions = dates.year.to_numpy() * 12 + dates.month.to_numpy()
    positions = positions - positions.min()
    scores = np.zeros((int(positions.max()) + 1, design.shape[1]))
    scores[positions] = design * residuals[:, None]
    meat = scores.T @ scores
    for lag in range(1, min(bandwidth, len(scores) - 1) + 1):
        cross = scores[lag:].T @ scores[:-lag]
        meat += (1 - lag / (bandwidth + 1)) * (cross + cross.T)
    bread = np.linalg.inv(design.T @ design)
    n, k = design.shape
    return bread @ meat @ bread * n / (n - k)


def standardize(s: pd.Series) -> pd.Series:
    sd = s.std(ddof=1)
    if not np.isfinite(sd) or sd < 1e-12:
        raise ValueError("serie constante o sin variación suficiente")
    return (s - s.mean()) / sd


def fit_contrast(frame: pd.DataFrame, lag: int, bandwidth: int,
                 ranked: bool = False) -> dict:
    d = frame.dropna().copy()
    out = {"n": len(d), "n_excluded": len(frame) - len(d), "status": "not_estimable"}
    if len(d) < 60:
        return {**out, "reason": "menos de 60 meses completos"}
    try:
        # Climatología y escalas recalculadas dentro de cada subconjunto.
        for name in ("x", "y"):
            d[name] -= d.groupby(d.index.month)[name].transform("mean")
        if ranked:
            for name in ("x", "y", "enso", "enso_lag"):
                d[name] = d[name].rank(method="average")
        y, x = standardize(d.y), standardize(d.x)
        controls = pd.DataFrame({"intercept": 1.0, "enso": standardize(d.enso)}, index=d.index)
        if lag:
            controls["enso_lag"] = standardize(d.enso_lag)
        months = d.index.year * 12 + d.index.month
        controls["trend"] = standardize(pd.Series(months, index=d.index, dtype=float))
        month_controls = pd.get_dummies(pd.Series(d.index.month, index=d.index),
                                        prefix="month", drop_first=True, dtype=float)
        controls = pd.concat([controls, month_controls], axis=1)
        design = np.column_stack([controls.to_numpy(), x.to_numpy()])
        condition = float(np.linalg.cond(design))
        if np.linalg.matrix_rank(design) < design.shape[1] or condition > 1e8:
            return {**out, "reason": "matriz singular o mal condicionada", "condition_number": condition}
        fit = sm.OLS(y.to_numpy(), design).fit()
        covariance = calendar_hac(design, fit.resid, d.index, bandwidth)
        variance = covariance[-1, -1]
        if not np.isfinite(variance) or variance <= 0:
            return {**out, "reason": "varianza HAC inválida"}
        se = float(np.sqrt(variance))
        beta = float(fit.params[-1])
        df = len(d) - design.shape[1]
        p = float(2 * stats.t.sf(abs(beta / se), df))
        critical = stats.t.ppf(0.975, df)
        c = controls.to_numpy()
        rx = x.to_numpy() - c @ np.linalg.lstsq(c, x, rcond=None)[0]
        ry = y.to_numpy() - c @ np.linalg.lstsq(c, y, rcond=None)[0]
        # Diagnóstico con pares de meses realmente consecutivos.
        residuals = pd.Series(fit.resid, index=d.index).reindex(frame.index)
        adjacent = pd.concat([residuals, residuals.shift(1)], axis=1).dropna()
        ac1 = adjacent.iloc[:, 0].corr(adjacent.iloc[:, 1]) if len(adjacent) > 2 else np.nan
        return {**out, "status": "ok", "reason": "", "start": str(d.index.min().date()),
                "end": str(d.index.max().date()), "beta_standardized": beta,
                "se_hac": se, "ci95_low": float(beta - critical * se),
                "ci95_high": float(beta + critical * se), "p_hac": p,
                "partial_r": float(np.corrcoef(rx, ry)[0, 1]),
                "residual_ac1": ac1, "condition_number": condition,
                "r_squared": float(fit.rsquared), "df_resid": df}
    except (ValueError, np.linalg.LinAlgError) as exc:
        return {**out, "reason": str(exc)}


def adjust_family(rows: list[dict], family: str) -> pd.DataFrame:
    result = pd.DataFrame(rows)
    if "p_hac" not in result:
        result["p_hac"] = np.nan
    # Los contrastes no estimables siguen contando en la familia prevista.
    q = multipletests(result.p_hac.fillna(1).to_numpy(), method="fdr_bh")[1]
    result["p_fdr"] = np.where(result.status.eq("ok"), q, np.nan)
    result["significant_fdr"] = result.p_fdr.lt(0.05)
    result["family"] = family
    return result


def load_inputs(panel_path: Path, nino_path: Path, start: int, end: int):
    panel = pd.read_csv(panel_path, parse_dates=["date"])
    required = {"date", "region", "depth_band", "phyc", "chl"}
    if not required.issubset(panel.columns):
        raise ValueError(f"Faltan columnas: {sorted(required - set(panel.columns))}")
    if panel.date.isna().any():
        raise ValueError("Fechas ausentes o inválidas en el panel")
    panel["date"] = panel.date.dt.to_period("M").dt.to_timestamp()
    if panel.duplicated(["date", "region", "depth_band"]).any():
        raise ValueError("Hay duplicados región/mes/banda; deben resolverse en la fuente")
    selected = panel[panel.depth_band.eq(BAND) & panel.region.isin((*REGIONS, "peru_humboldt"))].copy()
    calendar = pd.date_range(f"{start}-01-01", f"{end}-12-01", freq="MS")
    selected = selected[selected.date.isin(calendar)]
    audit = {"rows_panel": len(panel), "selected_rows": len(selected), "coverage": {},
             "source_kind": sorted(selected.source_kind.dropna().unique().tolist())
             if "source_kind" in selected else ["not supplied"]}
    for region in (*REGIONS, "peru_humboldt"):
        sub = selected[selected.region.eq(region)]
        if sub.empty:
            raise ValueError(f"Falta región {region} en {BAND}")
        audit["coverage"][region] = {}
        for variable in ("phyc", "chl"):
            values = pd.to_numeric(sub[variable], errors="raise")
            if np.isinf(values).any() or (values.dropna() < 0).any():
                raise ValueError(f"Valores inválidos en {region}/{variable}")
            audit["coverage"][region][variable] = {"valid_months": int(values.notna().sum()),
                "missing_months": len(calendar) - int(values.notna().sum())}
    nino = pd.read_csv(nino_path)
    if len(nino.columns) != 2:
        raise ValueError("El archivo Niño 1+2 debe contener fecha y una columna de valores")
    dates = pd.to_datetime(nino.iloc[:, 0], errors="raise").dt.to_period("M").dt.to_timestamp()
    if dates.duplicated().any():
        raise ValueError("Meses duplicados en Niño 1+2")
    enso = pd.Series(pd.to_numeric(nino.iloc[:, 1], errors="raise").to_numpy(), index=dates)
    enso = enso.replace([-99.99, -9999], np.nan).reindex(calendar)
    if np.isinf(enso).any():
        raise ValueError("Infinitos en Niño 1+2")
    audit["nino_missing_months"] = int(enso.isna().sum())
    series = {v: selected.pivot(index="date", columns="region", values=v).reindex(calendar)
              for v in ("phyc", "chl")}
    return series, enso, calendar, audit


def make_frames(series: pd.DataFrame, enso: pd.Series, calendar: pd.DatetimeIndex):
    frames = {}
    for region in REGIONS:
        for lag in LAGS:
            # shift sobre meses completos, antes de excluir o dividir años.
            frames[region, lag] = pd.DataFrame({"y": series.peru_humboldt,
                "x": series[region].shift(lag), "enso": enso, "enso_lag": enso.shift(lag)},
                index=calendar).iloc[max(LAGS):]
    # Una misma muestra completa para todos los contrastes de esta variable.
    common = pd.concat([d.notna().all(axis=1) for d in frames.values()], axis=1).all(axis=1)
    for frame in frames.values():
        frame.loc[~common, :] = np.nan
    return frames


def run_family(frames, name: str, bandwidth: int, subset: str = "all", ranked: bool = False):
    rows = []
    for (region, lag), frame in frames.items():
        midpoint = len(frame) // 2
        if subset == "first_half":
            frame = frame.iloc[:midpoint]
        elif subset == "second_half":
            frame = frame.iloc[midpoint:]
        elif subset == "without_1998":
            # Excluir tanto respuesta 1998 como predictor que provenga de 1998.
            source_dates = frame.index - pd.DateOffset(months=lag)
            frame = frame.copy()
            frame.loc[(frame.index.year == 1998) | (source_dates.year == 1998), :] = np.nan
        rows.append({"region": region, "depth_band": BAND, "lag_months": lag,
                     "bandwidth_months": bandwidth, "subset": subset,
                     "method": "partial_rank_HAC" if ranked else "OLS_HAC",
                     **fit_contrast(frame, lag, bandwidth, ranked)})
    return adjust_family(rows, name)


def write_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def write_report(output: Path, primary: pd.DataFrame, sensitivity: pd.DataFrame):
    ok = primary[primary.status.eq("ok")]
    significant = ok[ok.significant_fdr]
    lines = ["# Carbono fitoplanctónico Antártida–Humboldt", "",
             f"Contrastes previstos: {len(primary)}; estimables: {len(ok)}; significativos con FDR: {len(significant)}.", ""]
    if len(ok) != len(primary):
        conclusion = "No concluyente para la familia completa: existen contrastes no estimables."
    elif significant.empty:
        conclusion = "No se obtuvo evidencia suficiente para rechazar H0 en los 12 contrastes especificados."
    else:
        conclusion = "Se detectaron asociaciones exploratorias; su estabilidad se evalúa por contraste a continuación."
    lines += [conclusion, "", "| Región | Rezago (meses) | n | Beta estandarizado | IC 95 % | p HAC | p FDR |", "|---|---:|---:|---:|---|---:|---:|"]
    for _, r in ok.iterrows():
        lines.append(f"| {r.region} | {r.lag_months} | {r.n} | {r.beta_standardized:.3f} | [{r.ci95_low:.3f}, {r.ci95_high:.3f}] | {r.p_hac:.5g} | {r.p_fdr:.5g} |")
    lines += ["", "## Sensibilidad de los contrastes detectados", ""]
    for _, r in significant.iterrows():
        checks = sensitivity[(sensitivity.region == r.region) & (sensitivity.lag_months == r.lag_months)
                             & ~sensitivity.family.eq("chlorophyll_secondary")]
        stable = checks.status.eq("ok") & checks.significant_fdr & (np.sign(checks.beta_standardized) == np.sign(r.beta_standardized))
        label = "Asociación exploratoria consistente con las comprobaciones realizadas" if stable.all() else "Asociación sensible al periodo o al método"
        lines.append(f"- {r.region}, {r.lag_months} meses: {label} ({int(stable.sum())}/{len(checks)} comprobaciones mantienen signo y FDR < 0.05).")
    if significant.empty:
        lines.append("No hay detecciones principales que evaluar como asociaciones persistentes.")
    lines += ["", "## Método y límites", "",
              "- Respuesta: phyc de Humboldt peruano; predictor: phyc antártico. Ambos son campos del mismo modelo CMEMS, no observaciones independientes.",
              "- Se elimina la climatología mensual y se estandariza dentro de cada muestra. Se controla Niño 1+2 simultáneo, rezagado, tendencia lineal y efectos fijos de mes calendario.",
              "- Inferencia bilateral t con covarianza HAC/Bartlett, corrección de muestra finita y distancias calendario; ancho principal 12 meses. Las bandas 6/24 son sensibilidades.",
              "- FDR Benjamini–Hochberg en cada familia predefinida de 12 pruebas; los IC mostrados son individuales, sin ajuste simultáneo.",
              "- partial_rank_HAC usa rangos de anomalías y controles ENSO; es una sensibilidad de asociación parcial por rangos, no el p independiente de Spearman.",
              "- La ventana común empieza tras los primeros 24 meses. Sin 1998 excluye también predictores rezagados procedentes de ese año; algunos rezagos pueden quedar idénticos al principal.",
              "- No se rellenan huecos. La reducción original es mediana espacial del promedio de niveles, no carbono integrado en la columna de agua.",
              "- La inferencia HAC es asintótica; residual_ac1 y condition_number quedan en CSV para diagnóstico. La significancia no demuestra transporte ni causalidad.",
              "- No rechazar H0 no demuestra ausencia de relación. El menor p-valor no representa por sí solo toda la hipótesis.", ""]
    (output / "report.md").write_text("\n".join(lines), encoding="utf-8")
    return conclusion


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel", type=Path, default=ROOT / "data/processed/tables/connectivity_panel_monthly.csv")
    parser.add_argument("--nino12", type=Path, default=ROOT / "data/nino12.long.anom.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "data/processed/analysis/phytoplankton_carbon_connectivity")
    parser.add_argument("--start-year", type=int, default=1998)
    parser.add_argument("--end-year", type=int, default=2025)
    args = parser.parse_args()
    if args.start_year >= args.end_year:
        parser.error("El año inicial debe ser menor que el final")
    try:
        series, enso, calendar, audit = load_inputs(args.panel, args.nino12, args.start_year, args.end_year)
    except (ValueError, FileNotFoundError) as exc:
        parser.exit(2, f"Error de entrada: {exc}\n")
    frames = make_frames(series["phyc"], enso, calendar)
    primary = run_family(frames, "primary", 12)
    sensitivity = pd.concat([
        run_family(frames, "HAC_6", 6), run_family(frames, "HAC_24", 24),
        run_family(frames, "without_1998", 12, "without_1998"),
        run_family(frames, "first_half", 12, "first_half"),
        run_family(frames, "second_half", 12, "second_half"),
        run_family(frames, "partial_rank_secondary", 12, ranked=True),
        run_family(make_frames(series["chl"], enso, calendar), "chlorophyll_secondary", 12),
    ], ignore_index=True)
    args.output.mkdir(parents=True, exist_ok=True)
    primary.to_csv(args.output / "primary_results.csv", index=False)
    sensitivity.to_csv(args.output / "sensitivity_results.csv", index=False)
    aligned = []
    for (region, lag), frame in frames.items():
        item = frame.rename_axis("date").reset_index()
        item["source_region"], item["lag_months"] = region, lag
        item["used"] = frame.notna().all(axis=1).to_numpy()
        item["phyc_peru_mg_c_m3"] = item.y * 12.0107
        item["phyc_source_mg_c_m3"] = item.x * 12.0107
        aligned.append(item)
    pd.concat(aligned, ignore_index=True).to_csv(args.output / "aligned_panel.csv", index=False)
    audit["inputs"] = [{"path": str(p.resolve()), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in (args.panel, args.nino12)]
    audit["common_complete_months"] = int(next(iter(frames.values())).notna().all(axis=1).sum())
    write_json(args.output / "input_audit.json", audit)
    write_json(args.output / "analysis_config.json", {
        "start_year": args.start_year, "end_year": args.end_year, "regions": REGIONS,
        "target": "peru_humboldt", "band": BAND, "lags_months": LAGS, "alpha": 0.05,
        "primary_hac_months": 12, "fdr": "BH within each planned family of 12",
        "controls": ["Niño 1+2 at response month", "Niño 1+2 at source month (if lag > 0)",
                     "linear calendar trend", "calendar month fixed effects"],
        "minimum_complete_months": 60, "maximum_condition_number": 1e8,
        "climatology": "calendar-month means within each complete aligned subset",
        "units": "mmol C/m3; mg C/m3 = mmol C/m3 * 12.0107",
        "versions": {p: importlib.metadata.version(p) for p in ("numpy", "pandas", "scipy", "statsmodels")},
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "randomness": "none; deterministic analysis",
    })
    conclusion = write_report(args.output, primary, sensitivity)
    print(primary[["region", "lag_months", "n", "status", "p_hac", "p_fdr"]].to_string(index=False))
    print(f"\n{conclusion}\nInforme: {args.output / 'report.md'}")


if __name__ == "__main__":
    main()

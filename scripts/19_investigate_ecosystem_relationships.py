"""Exploración acotada de relaciones ecológicas con series ya disponibles.

No modifica los análisis anteriores. Todas las hipótesis se guardan antes del
ajuste; FDR global sobre la lista completa, sin buscar el mejor rezago.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import importlib.util
import importlib.metadata
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("carbon_analysis", Path(__file__).with_name("18_test_phytoplankton_carbon_connectivity.py"))
carbon = importlib.util.module_from_spec(spec)
spec.loader.exec_module(carbon)
REGIONS = (*carbon.REGIONS, "peru_humboldt", "south_pacific_intermediate", "south_pacific_subtropical", "transition_humboldt")
ZONES = ("paita", "chimbote", "callao", "pisco", "ilo")


@dataclass
class Hypothesis:
    id: str
    predictor: str
    response: str
    lag: int
    control_enso: bool
    rationale: str
    evidence: str


def load_series():
    panel_path = ROOT / "data/processed/tables/connectivity_panel_monthly.csv"
    monitor_path = ROOT / "src/nasahackaton/monitor_data.json"
    panel = pd.read_csv(panel_path, parse_dates=["date"])
    if panel.duplicated(["date", "region", "depth_band"]).any():
        raise ValueError("Panel con fechas duplicadas por región/banda")
    monitor = pd.DataFrame(json.loads(monitor_path.read_text())["records"])
    monitor.index = pd.to_datetime(monitor.date).dt.to_period("M").dt.to_timestamp()
    if monitor.index.duplicated().any():
        raise ValueError("Monitor con meses duplicados")
    index = pd.date_range("1998-01-01", "2025-12-01", freq="MS")
    data = pd.DataFrame(index=index)
    data["nino12"] = pd.to_numeric(monitor.nino12_psl_c, errors="raise")
    for region in REGIONS:
        for var, band in [("phyc", "surface_0_5m"), ("chl", "surface_0_5m"),
                          ("no3", "surface_0_5m"), ("mlotst", "surface_2d")]:
            p = panel[panel.region.eq(region) & panel.depth_band.eq(band)].set_index("date")
            data[f"{region}:{var}"] = p[var]
        chl, phy = data[f"{region}:chl"], data[f"{region}:phyc"]
        data[f"{region}:log_chl_carbon"] = np.log(chl.where(chl > 0) / (phy.where(phy > 0) * 12.0107))
    for zone in (*ZONES, "rey_jorge", "peninsula_antartica"):
        data[f"occci:{zone}"] = monitor[f"chl_{zone}_mg_m3"]
    files = [panel_path, monitor_path]
    for zone in ("chimbote", "paita"):
        path = ROOT / f"data/giovanni/{zone}_modisa_chl_mensual_2002-2025.csv"
        d = pd.read_csv(path, skiprows=8)
        dates = pd.to_datetime(d.iloc[:, 0]).dt.to_period("M").dt.to_timestamp()
        if dates.duplicated().any():
            raise ValueError(f"Giovanni {zone}: meses duplicados")
        values = pd.to_numeric(d.iloc[:, 1], errors="raise").replace(-32767, np.nan)
        data[f"modis:{zone}"] = pd.Series(values.to_numpy(), index=dates)
        files.append(path)
    t = panel[panel.region.eq("peru_humboldt")].pivot(index="date", columns="depth_band", values="thetao")
    data["peru_humboldt:thermal_gradient"] = t.surface_0_5m - t.subsurface_100_200m
    if np.isinf(data.to_numpy()).any():
        raise ValueError("Series con infinitos")
    return data, files


def hypotheses():
    rows = []
    def add(x, y, lag, enso, reason, evidence):
        rows.append(Hypothesis(f"H{len(rows)+1:02d}", x, y, lag, enso, reason, evidence))
    for source, zones in [("occci", ZONES), ("modis", ("chimbote", "paita"))]:
        for z in zones:
            add("nino12", f"{source}:{z}", 0, False,
                "ENSO y clorofila local: comprobación de asociación conocida; no causalidad",
                "climate_index_vs_satellite")
    add("nino12", "peru_humboldt:phyc", 0, False,
        "¿El carbono responde igual que el pigmento al calentamiento costero?", "climate_index_vs_model")
    for r in REGIONS:
        add(f"{r}:mlotst", f"{r}:phyc", 0, True,
            "Mezcla y biomasa superficial: disponibilidad de luz y dilución", "same_model")
    for z in ZONES:
        add("peru_humboldt:mlotst", f"occci:{z}", 0, True,
            "Mezcla regional y clorofila satelital costera; cajas no idénticas", "model_vs_satellite")
    for z in ("chimbote", "paita"):
        add("peru_humboldt:mlotst", f"modis:{z}", 0, True,
            "Comprobación NASA de mezcla regional y pigmento costero", "model_vs_satellite")
    for r, z in [("peninsula_antarctica", "peninsula_antartica"), ("peninsula_antarctica", "rey_jorge")]:
        add(f"{r}:mlotst", f"occci:{z}", 0, True,
            "Mezcla antártica y pigmento satelital; cobertura óptica estacional y cajas diferentes", "model_vs_satellite")
    for r in REGIONS:
        add(f"{r}:no3", f"{r}:phyc", 1, True,
            "Nutriente un mes antes y carbono: suministro/consumo; signo no preestablecido", "same_model")
    add("peru_humboldt:thermal_gradient", "peru_humboldt:phyc", 0, True,
        "Contraste térmico superficie–100/200 m como descriptor, no profundidad exacta de termoclina", "same_model")
    for r in (*carbon.REGIONS, "peru_humboldt"):
        add(f"{r}:mlotst", f"{r}:log_chl_carbon", 0, True,
            "Mezcla y cantidad de pigmento por carbono: hipótesis de fotoaclimatación, no medición fisiológica", "same_model_derived_ratio")
    return rows


def controls(d, h):
    c = pd.DataFrame({"const": 1.0}, index=d.index)
    if h.control_enso:
        c["enso"] = carbon.standardize(d.enso)
        if h.lag:
            c["enso_source"] = carbon.standardize(d.enso_source)
    c["trend"] = carbon.standardize(pd.Series(d.index.year * 12 + d.index.month, index=d.index, dtype=float))
    return pd.concat([c, pd.get_dummies(pd.Series(d.index.month, index=d.index), prefix="month", drop_first=True, dtype=float)], axis=1)


def fit(d, h, bandwidth=12):
    d = d.dropna().copy()
    result = {"n": len(d), "status": "not_estimable"}
    if len(d) < 84:
        return {**result, "reason": "menos de 84 meses"}
    try:
        # Anomalías de x e y; los efectos fijos de mes conservan el ajuste estacional de controles.
        for v in ("x", "y"):
            d[v] = d[v] - d.groupby(d.index.month)[v].transform("mean")
            d[v] = carbon.standardize(d[v])
        c = controls(d, h).to_numpy()
        design = np.c_[c, d.x]
        if np.linalg.matrix_rank(design) < design.shape[1] or np.linalg.cond(design) > 1e8:
            return {**result, "reason": "matriz singular"}
        model = sm.OLS(d.y.to_numpy(), design).fit()
        cov = carbon.calendar_hac(design, model.resid, d.index, bandwidth)
        se = float(np.sqrt(cov[-1, -1]))
        if not np.isfinite(se) or se <= 0:
            return {**result, "reason": "varianza inválida"}
        beta, df = float(model.params[-1]), len(d)-design.shape[1]
        ci = stats.t.ppf(.975, df) * se
        rx = d.x.to_numpy() - c @ np.linalg.lstsq(c, d.x, rcond=None)[0]
        ry = d.y.to_numpy() - c @ np.linalg.lstsq(c, d.y, rcond=None)[0]
        return {**result, "status": "ok", "reason": "", "beta": beta,
                "ci_low": beta-ci, "ci_high": beta+ci,
                "partial_r": float(np.corrcoef(rx, ry)[0, 1]),
                "p_hac": float(2*stats.t.sf(abs(beta/se), df)),
                "start": str(d.index.min().date()), "end": str(d.index.max().date())}
    except (ValueError, np.linalg.LinAlgError) as e:
        return {**result, "reason": str(e)}


def adjust(rows):
    d = pd.DataFrame(rows)
    q = multipletests(d.p_hac.fillna(1), method="fdr_bh")[1]
    d["q_global"] = np.where(d.status.eq("ok"), q, np.nan)
    d["significant"] = d.q_global.lt(.05)
    return d


def conditional_cv(frame, h):
    """Evaluación por años; x contemporáneo conocido, no pronóstico operativo."""
    records = []
    for year in range(2012, 2026):
        tr = frame.loc[:f"{year-1}-12"].dropna().copy()
        te = frame.loc[str(year)].dropna().copy()
        if len(tr)<84 or len(te)<6:
            continue
        # Climatologías, escalas y regresiones calculadas solo con el pasado.
        for v in ("x", "y"):
            clim = tr.groupby(tr.index.month)[v].mean()
            tr[v] -= clim.reindex(tr.index.month).to_numpy()
            te[v] -= clim.reindex(te.index.month).to_numpy()
        def design(d):
            cols = [np.ones(len(d)), (d.index.year*12+d.index.month).to_numpy(dtype=float)]
            cols += [(d.index.month == month).astype(float) for month in range(2,13)]
            if h.control_enso:
                cols.append(d.enso.to_numpy())
                if h.lag: cols.append(d.enso_source.to_numpy())
            return np.column_stack(cols)
        train_c, test_c = design(tr), design(te)
        b = np.linalg.lstsq(train_c, tr.y, rcond=None)[0]
        xtr, xte = np.c_[train_c, tr.x], np.c_[test_c, te.x]
        a = np.linalg.lstsq(xtr, tr.y, rcond=None)[0]
        for i, date in enumerate(te.index):
            records.append({"date": str(date.date()), "observed": te.y.iloc[i],
                            "baseline": float(test_c[i]@b), "with_predictor": float(xte[i]@a)})
    if not records:
        return {"cv_n": 0, "cv_improvement_pct": np.nan}
    r = pd.DataFrame(records)
    rm0 = float(np.sqrt(np.mean((r.observed-r.baseline)**2)))
    rm1 = float(np.sqrt(np.mean((r.observed-r.with_predictor)**2)))
    return {"cv_n": len(r), "cv_rmse_baseline": rm0, "cv_rmse_predictor": rm1,
            "cv_improvement_pct": 100*(1-rm1/rm0) if rm0 else np.nan}


def write_outputs(output, summary, results):
    lines = ["# Exploración de relaciones ecológicas", "",
             f"Hipótesis: {len(summary)}; con FDR global < 0.05: {int(summary.significant.sum())}; "
             f"significativas en todas las sensibilidades: {int(summary.all_sensitivities_significant.sum())}.", "",
             "La familia de 33 pruebas se fijó antes de la ejecución, a partir de disponibilidad y literatura. "
             "Este ajuste no cubre todas las búsquedas históricas del proyecto. Los periodos ya fueron inspeccionados "
             "en otros análisis; las sensibilidades no son una confirmación ciega ni validación independiente.", "",
             "MLD se extrajo de surface_2d, donde tiene 336 meses por región. El script E7 anterior "
             "consultaba surface_0_5m y por ello la descartaba como vacía.", "",
             "## Resultados completos", "",
             "r es correlación parcial tras controles, no correlación de las series brutas. "
             "La significancia usa regresión con covarianza HAC12 y FDR BH global. IC individuales, no simultáneos. "
             "Se controla tendencia y mes; ENSO simultáneo y rezagado se añade cuando no es el predictor investigado.", "",
             "| ID | Predictor | Respuesta | n | r parcial | p HAC | q FDR | Todas las sensibilidades | Mejora RMSE condicional % |",
             "|---|---|---|---:|---:|---:|---:|---|---:|"]
    for _,r in summary.iterrows():
        lines.append(f"| {r.id} | {r.predictor} | {r.response} | {r.n} | {r.partial_r:.3f} | "
                     f"{r.p_hac:.3g} | {r.q_global:.3g} | {'sí' if r.all_sensitivities_significant else 'no'} | {r.cv_improvement_pct:.2f} |")
    lines += ["", "## Interpretación", "",
              "- all_sensitivities_significant exige FDR < 0.05 y mismo signo en 1998–2011, 2012–2025, sin 1998, HAC6 y HAC24.",
              "- La mejora de RMSE compara el modelo con predictor frente al modelo con los mismos controles sin él, por años 2012–2025, entrenando solo con el pasado.",
              "- Los predictores de rezago 0 están disponibles en el mes evaluado. Es una evaluación explicativa condicional, no un pronóstico futuro ni una estimación del valor operacional.",
              "- Un resultado puede ser significativo y empeorar la evaluación temporal (por ejemplo H29). No se recomienda por significancia sola.",
              "- Los productos CMEMS comparten estructura del modelo/forzamiento. Una relación entre sus campos no es una comprobación observacional independiente.",
              "- OC-CCI combina sensores, entre ellos MODIS. La comparación con MODIS es una sensibilidad al producto y procesamiento, no independencia completa de sensores.",
              "- El cociente clorofila/carbono es un descriptor derivado de pigmento por carbono; no mide por sí solo productividad, fotosíntesis ni biomasa adicional.",
              "- Las cajas de MLD regional y satélite costero no coinciden exactamente. En Antártida faltan meses de observación óptica; no se extrapolan inviernos.",
              "- No se demuestran relaciones causales, transporte Antártida–Perú ni efectos en anchoveta.",
              "- NASA Chimbote cubre 281 meses desde julio de 2002 hasta noviembre de 2025; ambos primeros meses se conservan al leer el CSV original.", "",
              "## Reproducción", "", "```bash", "uv run python scripts/19_investigate_ecosystem_relationships.py", "```", ""]
    (output/"report.md").write_text("\n".join(lines),encoding="utf-8")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    chosen = summary[summary.all_sensitivities_significant]
    labels = {"H02":"El Niño → clorofila de Chimbote (OC-CCI)",
              "H03":"El Niño → clorofila de Callao (OC-CCI)",
              "H08":"El Niño → carbono de Humboldt (CMEMS)",
              "H10":"Mezcla → carbono, Bellingshausen (CMEMS)",
              "H12":"Mezcla → carbono, Pacífico intermedio (CMEMS)",
              "H13":"Mezcla → carbono, Pacífico subtropical (CMEMS)",
              "H28":"Nitrato +1 mes → carbono, subtropical (CMEMS)",
              "H29":"Nitrato +1 mes → carbono, transición (CMEMS)*",
              "H33":"Mezcla → clorofila/carbono, Humboldt (CMEMS)"}
    if chosen.empty:
        return
    fig,ax=plt.subplots(figsize=(12,7))
    for name,offset,color,label in [("main",-.2,"#243f60","Periodo completo"),
                                     ("early",0,"#238b66","Hasta 2011"),
                                     ("late",.2,"#c56a2b","Desde 2012")]:
        d=results[results.scenario.eq(name)].set_index("id").loc[chosen.id]
        ax.errorbar(d.beta,np.arange(len(d))+offset,
                    xerr=np.vstack([d.beta-d.ci_low,d.ci_high-d.beta]),
                    fmt="o",capsize=2,color=color,label=label,markersize=4)
    ax.axvline(0,color="grey",linewidth=1)
    ax.set_yticks(np.arange(len(chosen)),[labels.get(i,i) for i in chosen.id])
    ax.invert_yaxis()
    ax.set_xlabel("Efecto estandarizado e intervalo de confianza individual del 95 %")
    ax.set_title("Asociaciones que pasan FDR en las comprobaciones definidas",loc="left",fontweight="bold")
    ax.legend(loc="lower left",fontsize=8)
    ax.grid(axis="x",alpha=.2)
    fig.text(.01,.01,"Exploración retrospectiva; CMEMS es modelado. *H29 empeora la evaluación temporal pese a su significancia.",fontsize=8)
    fig.tight_layout(rect=(0,.035,1,1))
    fig.savefig(output/"candidate_effects.png",dpi=160)
    fig.savefig(output/"candidate_effects.svg")
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT/"data/processed/analysis/ecosystem_relationships")
    args=parser.parse_args()
    data, files = load_series()
    hs=hypotheses()
    args.output.mkdir(parents=True, exist_ok=True)
    config={"hypotheses": [asdict(h) for h in hs], "n_tests":len(hs),
            "period":"1998-2025, según cobertura de cada par", "split":"hasta 2011 / desde 2012",
            "inference":"OLS, month fixed effects, linear trend, ENSO if specified; calendar HAC12; global BH",
            "warning":"Exploración retrospectiva; el periodo posterior ya fue inspeccionado en trabajos previos. No es confirmación independiente.",
            "cv":"Expanding annual training, 2012-2025; known x at target date for lag0, conditional assessment, not future forecast",
            "versions":{p:importlib.metadata.version(p) for p in ("numpy","pandas","scipy","statsmodels","matplotlib")},
            "scripts":[{"path":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
                       for p in (Path(__file__),Path(__file__).with_name("18_test_phytoplankton_carbon_connectivity.py"))],
            "sources":[{"path":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
    (args.output/"hypotheses_and_config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False)+"\n")
    data.to_csv(args.output/"input_series.csv", index_label="date")
    coverage=data.count().rename("available_months").to_frame()
    coverage.to_csv(args.output/"coverage.csv",index_label="series")
    frames={}
    for h in hs:
        frames[h.id]=pd.DataFrame({"x":data[h.predictor].shift(h.lag),"y":data[h.response],
                                  "enso":data.nino12,"enso_source":data.nino12.shift(h.lag)})
    scenarios=[("main",12),("early",12),("late",12),("without_1998",12),("HAC6",6),("HAC24",24)]
    outputs=[]
    for scenario,bw in scenarios:
        rows=[]
        for h in hs:
            d=frames[h.id]
            if scenario=="early": d=d.loc[:"2011-12"]
            elif scenario=="late":d=d.loc["2012-01":]
            elif scenario=="without_1998":
                source=d.index-pd.DateOffset(months=h.lag)
                d=d.copy();d.loc[(d.index.year==1998)|(source.year==1998),:]=np.nan
            rows.append({**asdict(h),"scenario":scenario,"bandwidth":bw,**fit(d,h,bw)})
        outputs.append(adjust(rows))
    results=pd.concat(outputs,ignore_index=True)
    results.to_csv(args.output/"all_results.csv",index=False)
    summary=results[results.scenario.eq("main")].copy()
    for scenario,_ in scenarios[1:]:
        subset=results[results.scenario.eq(scenario)].set_index("id")
        for col in ("partial_r","q_global","significant","status"):
            summary[f"{scenario}_{col}"]=summary.id.map(subset[col])
    summary["stable_sign"] = True
    summary["all_sensitivities_significant"] = summary.significant.copy()
    for scenario,_ in scenarios[1:]:
        summary["stable_sign"] &= np.sign(summary.partial_r).eq(np.sign(summary[f"{scenario}_partial_r"]))
        summary["all_sensitivities_significant"] &= summary[f"{scenario}_significant"].eq(True)
    cv={h.id:conditional_cv(frames[h.id],h) for h in hs}
    for col in {k for v in cv.values() for k in v}:
        summary[col]=summary.id.map(lambda k:cv[k].get(col,np.nan))
    summary.to_csv(args.output/"summary.csv",index=False)
    write_outputs(args.output,summary,results)
    print('Hipótesis totales:',len(hs),'| significativas global FDR:',int(summary.significant.sum()),
          '| todas las sensibilidades:',int(summary.all_sensitivities_significant.sum()))
    cols=["id","predictor","response","partial_r","q_global","early_partial_r","early_q_global",
          "late_partial_r","late_q_global","cv_improvement_pct","stable_sign","all_sensitivities_significant"]
    print(summary.sort_values("q_global")[cols].to_string(index=False))
    print('Resultados:',args.output)


if __name__=="__main__":main()

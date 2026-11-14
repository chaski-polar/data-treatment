"""Enfoques nuevos (14/11): E1 tendencia de eventos extremos, E2 tendencia y control de la fenología (amplitud y fecha del pico),
E3 estudio de eventos de El Niño (dosis-respuesta y recuperación). Solo datos locales."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

RAIZ = Path(r"D:\hackathon\NASA")
SALIDA = RAIZ / "pruebas" / "fitoplancton" / "tablas"
ZONAS = ["paita", "chimbote", "callao", "pisco", "ilo", "rey_jorge", "peninsula_antartica"]
PERU = ZONAS[:5]
CLAVE = {"paita": "peru_norte_paita_sechura", "chimbote": "peru_centro_norte_chimbote", "callao": "peru_centro_callao", "pisco": "peru_sur_pisco",
         "ilo": "peru_sur_ilo", "rey_jorge": "antartida_rey_jorge", "peninsula_antartica": "antartida_peninsula"}

mon = pd.DataFrame(json.load(open(RAIZ / "pruebas" / "json_pagina" / "monitor_data.json", encoding="utf-8"))["records"])
mon.index = pd.to_datetime(mon["date"]).dt.to_period("M").dt.to_timestamp()
nino = mon["nino12_psl_c"].astype(float)
vm = pd.read_csv(RAIZ / "datos" / "peru" / "variables_mensuales.csv")


def fdr(p):
    p = np.asarray(p, float)
    o = np.argsort(p)
    aj = np.minimum.accumulate((p[o] * len(p) / np.arange(1, len(p) + 1))[::-1])[::-1].clip(max=1)
    r = np.empty(len(p))
    r[o] = aj
    return r


def mk(s):
    s = s.dropna()
    if len(s) < 10 or s.nunique() < 3:
        return np.nan, np.nan, np.nan
    tau, p = stats.kendalltau(s.index, s.values)
    return float(tau), float(p), float(stats.theilslopes(s.values, s.index)[0] * 10)


# ------------------------------------------------------------ E1 eventos extremos por año
filas = []
for z in ZONAS:
    chl = mon[f"chl_{z}_anom_pct"].astype(float).loc["1998":"2025"].dropna()
    bajo = (chl <= -30).groupby(chl.index.year).sum()
    cuenta = chl.groupby(chl.index.year).count()
    bajo = bajo[cuenta >= 9]
    tau, p, sen = mk(bajo.astype(float))
    filas.append({"prueba": "E1 meses con clorofila <= -30 % por año", "zona": z, "periodo": "1998-2025", "n_anios": len(bajo), "tau": tau, "p": p, "tendencia_por_decada": sen})
    d = vm[(vm.variable == "temperatura_superficial_C") & (vm.zona == CLAVE[z])]
    t = pd.Series(d.valor.astype(float).to_numpy(), index=pd.to_datetime(d.mes + "-01")).sort_index().loc["1986":"2025"].dropna()
    base = t.loc["1986":"2015"]
    anom = t - base.groupby(base.index.month).mean().reindex(t.index.month).to_numpy()
    umbral = 1.0 if z in PERU else 0.5
    calido = (anom >= umbral).groupby(anom.index.year).sum()
    cuenta = anom.groupby(anom.index.year).count()
    calido = calido[cuenta >= 9]
    tau, p, sen = mk(calido.astype(float))
    filas.append({"prueba": f"E1 meses con temperatura >= +{umbral} °C sobre 1986-2015 por año", "zona": z, "periodo": "1986-2025", "n_anios": len(calido), "tau": tau, "p": p, "tendencia_por_decada": sen})
e1 = pd.DataFrame(filas)
e1["p_fdr"] = fdr(e1.p.fillna(1))

# ------------------------------------------------------------ E2 fenología de la clorofila
filas = []
for z in ZONAS:
    c = mon[f"chl_{z}_mg_m3"].astype(float).loc["1998":"2025"]
    g = c.groupby(c.index.year)
    ok = g.count() >= 10
    amp = ((g.max() - g.min()) / g.mean())[ok]
    pico = g.max()[ok]
    mes_pico = c.groupby(c.index.year).apply(lambda s: s.idxmax().month if s.notna().any() else np.nan)[ok]
    for nombre, s in (("amplitud estacional (máx-mín)/media", amp), ("valor del pico anual", pico), ("mes del pico anual", mes_pico.astype(float))):
        tau, p, sen = mk(s)
        filas.append({"prueba": f"E2 {nombre}", "zona": z, "periodo": "1998-2025", "n_anios": len(s), "tau": tau, "p": p, "tendencia_por_decada": sen})
e2 = pd.DataFrame(filas)
e2["p_fdr"] = fdr(e2.p.fillna(1))

# ------------------------------------------------------------ E3 estudio de eventos de El Niño
n3 = nino.rolling(3, center=True).mean()
picos = []
for f, v in n3.loc["1998":"2026"].dropna().sort_values(ascending=False).items():
    if v >= 1.5 and all(abs((f - q).days) > 365 for q in picos):
        picos.append(f)
picos = sorted(picos)
filas = []
for z in PERU:
    a = mon[f"chl_{z}_anom_pct"].astype(float)
    for f in picos:
        ventana = a.loc[f - pd.DateOffset(months=3): f + pd.DateOffset(months=9)].dropna()
        if len(ventana) < 8:
            continue
        despues = a.loc[f:].dropna()
        rec = np.nan
        for i in range(len(despues) - 2):
            if (despues.iloc[i:i + 3] >= -10).all():
                rec = (despues.index[i].year - f.year) * 12 + despues.index[i].month - f.month
                break
        filas.append({"zona": z, "pico_nino12": f.strftime("%Y-%m"), "nino12_pico_c": round(float(n3.loc[f]), 2), "min_chl_pct": round(float(ventana.min()), 1), "meses_hasta_recuperar": rec})
ev = pd.DataFrame(filas)
res = []
for z, g in ev.groupby("zona"):
    if len(g) >= 4:
        r, p = stats.spearmanr(g.nino12_pico_c, g.min_chl_pct)
        res.append({"zona": z, "n_eventos": len(g), "rho_nino_pico_vs_min_chl": round(float(r), 2), "p": round(float(p), 3), "recuperacion_mediana_meses": float(g.meses_hasta_recuperar.median())})
e3 = pd.DataFrame(res)

pd.set_option("display.width", 220)
e1.round(4).to_csv(SALIDA / "nuevos_E1_eventos_extremos_tendencia.csv", index=False)
e2.round(4).to_csv(SALIDA / "nuevos_E2_fenologia_tendencia.csv", index=False)
ev.to_csv(SALIDA / "nuevos_E3_eventos_nino_detalle.csv", index=False)
e3.to_csv(SALIDA / "nuevos_E3_eventos_nino_resumen.csv", index=False)
print("E1 (tendencia de extremos)\n", e1.round(3).to_string(index=False))
print("\nE2 (fenologia) significativas p<0.05:", int((e2.p < 0.05).sum()), "de", len(e2), "| FDR:", int((e2.p_fdr < 0.05).sum()))
print(e2[e2.p < 0.05].round(3).to_string(index=False))
print("\nE3 eventos:", [p.strftime("%Y-%m") for p in picos])
print(e3.to_string(index=False))

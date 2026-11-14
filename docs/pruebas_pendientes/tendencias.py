"""Tendencias (el núcleo del reto "Be an Earth System Trend Detective"): Mann-Kendall anual, Mann-Kendall estacional
(Hirsch), pendiente de Sen, regresión mensual con n efectivo, por estación, sensibilidad al año de inicio y series largas
(CRW 1985-2025 y ERSST v5 1950-2025). Solo datos locales."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats

RAIZ = Path(r"D:\hackathon\NASA")
SALIDA = RAIZ / "pruebas" / "fitoplancton" / "tablas"
ZONAS = {"paita": (-6.5, -4.5, -82.0, -80.5), "chimbote": (-10.0, -8.0, -80.0, -78.0), "callao": (-13.0, -11.0, -78.5, -76.8),
         "pisco": (-14.5, -13.0, -77.0, -76.0), "ilo": (-18.0, -16.5, -72.5, -71.0),
         "rey_jorge": (-63.0, -61.5, -60.5, -56.5), "peninsula_antartica": (-68.0, -60.0, -70.0, -55.0)}
CLAVE = {"paita": "peru_norte_paita_sechura", "chimbote": "peru_centro_norte_chimbote", "callao": "peru_centro_callao", "pisco": "peru_sur_pisco",
         "ilo": "peru_sur_ilo", "rey_jorge": "antartida_rey_jorge", "peninsula_antartica": "antartida_peninsula"}


def mk_anual(s: pd.Series) -> dict:
    s = s.dropna()
    if len(s) < 8:
        return {"n": len(s), "tau": np.nan, "p": np.nan, "sen_por_decada": np.nan}
    tau, p = stats.kendalltau(s.index, s.values)
    return {"n": len(s), "tau": float(tau), "p": float(p), "sen_por_decada": float(stats.theilslopes(s.values, s.index)[0] * 10)}


def kendall_estacional(m: pd.Series) -> dict:
    """Prueba de Hirsch: Mann-Kendall dentro de cada mes del año y suma de los 12 estadísticos."""
    S = V = 0.0
    pend = []
    for mes in range(1, 13):
        x = m[m.index.month == mes].dropna()
        n = len(x)
        if n < 6:
            continue
        v = x.values
        S += sum(np.sign(v[j] - v[i]) for i in range(n - 1) for j in range(i + 1, n))
        V += n * (n - 1) * (2 * n + 5) / 18
        yr = x.index.year.values
        pend += [(v[j] - v[i]) / (yr[j] - yr[i]) for i in range(n - 1) for j in range(i + 1, n) if yr[j] != yr[i]]
    if V == 0:
        return {"z": np.nan, "p": np.nan, "sen_por_decada": np.nan}
    z = (S - np.sign(S)) / np.sqrt(V)
    return {"z": float(z), "p": float(2 * stats.norm.sf(abs(z))), "sen_por_decada": float(np.median(pend) * 10)}


def ols_mensual(m: pd.Series) -> dict:
    """Pendiente de la anomalía mensual (sin estacionalidad) con n efectivo por autocorrelación de orden 1."""
    a = m.dropna()
    a = a - a.groupby(a.index.month).transform("mean")
    t = (a.index.year + (a.index.month - 1) / 12).to_numpy()
    sl, _, r, _, _ = stats.linregress(t, a.values)
    r1 = np.corrcoef(a.values[:-1], a.values[1:])[0, 1]
    neff = len(a) * (1 - r1) / (1 + r1)
    tt = r * np.sqrt((neff - 2) / max(1e-12, 1 - r * r))
    return {"pend_por_decada": float(sl * 10), "n_meses": len(a), "n_eff": round(float(neff), 1), "p_neff": float(2 * stats.t.sf(abs(tt), max(neff - 2, 1)))}


def anual(m: pd.Series, meses=None, min_meses=6) -> pd.Series:
    x = m[m.index.month.isin(meses)] if meses else m
    g = x.groupby(x.index.year)
    return g.mean()[g.count() >= (min_meses if not meses else max(2, len(meses) - 1))]


# ---------------------------------------------------------------- series
mon = pd.DataFrame(json.load(open(RAIZ / "pruebas" / "json_pagina" / "monitor_data.json", encoding="utf-8"))["records"])
mon.index = pd.to_datetime(mon["date"]).dt.to_period("M").dt.to_timestamp()
vm = pd.read_csv(RAIZ / "datos" / "peru" / "variables_mensuales.csv")


def serie_crw(z):
    d = vm[(vm.variable == "temperatura_superficial_C") & (vm.zona == CLAVE[z])]
    return pd.Series(d.valor.astype(float).to_numpy(), index=pd.to_datetime(d.mes + "-01")).sort_index()


er = xr.open_dataset(RAIZ / "datos" / "tendencias_largas" / "ersstv5_sst_mnmean.nc")


def serie_ersst(z):
    la0, la1, lo0, lo1 = ZONAS[z]
    sub = er.sst.sel(lat=slice(la1 + 1.0, la0 - 1.0) if er.lat[0] > er.lat[-1] else slice(la0 - 1.0, la1 + 1.0),
                     lon=slice((lo0 - 1.0) % 360, (lo1 + 1.0) % 360))
    s = sub.mean(dim=("lat", "lon"), skipna=True).to_series()
    s.index = s.index.to_period("M").to_timestamp()
    return s.dropna()


series = []
for z in ZONAS:
    series.append((f"SST {z}", "CRW v3.1 (NOAA)", "sst", serie_crw(z).loc["1986-01":"2025-12"]))
    series.append((f"SST {z}", "ERSST v5 (NOAA, 2 grados)", "sst", serie_ersst(z).loc["1950-01":"2025-12"]))
    key = "rey_jorge" if z == "rey_jorge" else z
    c = mon[f"chl_{z}_mg_m3"].astype(float).loc["1998-01":"2025-12"]
    series.append((f"clorofila {z}", "OC-CCI v6 (ESA)", "chl", c))
g = pd.read_csv(RAIZ / "datos" / "giovanni" / "chimbote_modisa_chl_mensual_2002-2025.csv", skiprows=9)
g.columns = ["t", "v"]
gs = pd.Series(g.v.replace(-32767, np.nan).to_numpy(), index=pd.to_datetime(g.t).dt.to_period("M").dt.to_timestamp())
series.append(("clorofila chimbote", "MODIS-Aqua (NASA, Giovanni)", "chl", gs.loc["2002-07":"2025-11"]))

# ---------------------------------------------------------------- tabla principal
filas = []
for nombre, fuente, tipo, m in series:
    p0, p1 = m.index.min().year, m.index.max().year
    ini_completo = p0 if m.index.min().month == 1 else p0 + 1
    A = anual(m).loc[ini_completo:p1]
    for metodo, r in [("Mann-Kendall anual (media del año)", mk_anual(A)),
                      ("Mann-Kendall anual, solo verano (dic-mar)", mk_anual(anual(m, [12, 1, 2, 3]))),
                      ("Mann-Kendall anual, solo invierno (jun-sep)", mk_anual(anual(m, [6, 7, 8, 9])))]:
        filas.append({"serie": nombre, "fuente": fuente, "periodo": f"{ini_completo}-{p1}", "metodo": metodo, "n": r["n"],
                      "tendencia_por_decada": round(r["sen_por_decada"], 4), "p": r["p"]})
    k = kendall_estacional(m)
    filas.append({"serie": nombre, "fuente": fuente, "periodo": f"{ini_completo}-{p1}", "metodo": "Mann-Kendall estacional (Hirsch, mensual)",
                  "n": int(m.notna().sum()), "tendencia_por_decada": round(k["sen_por_decada"], 4), "p": k["p"]})
    o = ols_mensual(m)
    filas.append({"serie": nombre, "fuente": fuente, "periodo": f"{ini_completo}-{p1}", "metodo": "Regresión mensual sin estacionalidad (n efectivo)",
                  "n": o["n_meses"], "tendencia_por_decada": round(o["pend_por_decada"], 4), "p": o["p_neff"]})
T = pd.DataFrame(filas)
T["significativa_p05"] = T["p"] < 0.05
T["p"] = T["p"].round(4)
T.to_csv(SALIDA / "tendencias_resumen.csv", index=False)

# ---------------------------------------------------------------- sensibilidad al año de inicio (solo series de SST largas y antárticas)
filas = []
for nombre, fuente, tipo, m in series:
    A = anual(m)
    for ini in range(int(A.index.min()), int(A.index.max()) - 14):
        r = mk_anual(A.loc[ini:])
        filas.append({"serie": nombre, "fuente": fuente, "inicio": ini, "n": r["n"], "tendencia_por_decada": round(r["sen_por_decada"], 4), "p": round(r["p"], 4)})
S = pd.DataFrame(filas)
S.to_csv(SALIDA / "tendencias_sensibilidad_inicio.csv", index=False)

# ---------------------------------------------------------------- impresión
pd.set_option("display.width", 250)
print(T[T.metodo.str.contains("anual \\(media|estacional|Regresión")][["serie", "fuente", "periodo", "metodo", "n", "tendencia_por_decada", "p"]].to_string(index=False))
print("\nsignificativas p<0,05:", int(T.significativa_p05.sum()), "de", len(T))

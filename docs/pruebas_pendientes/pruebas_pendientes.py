"""Pruebas pendientes (ver PRUEBAS_POSIBLES.md): A4 predicción con asimetría, A1 clorofila -> desembarques mensuales,
B1 El Niño -> Antártida, A3 viento ERA5 -> clorofila. Solo datos locales. Criterio de aceptación: correlación parcial con
Niño 1+2, n efectivo (Pyper-Peterman), FDR, sin 1998 y mitades del periodo."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

RAIZ = Path(r"D:\hackathon\NASA")
SALIDA = RAIZ / "pruebas" / "fitoplancton" / "tablas"
ZONAS = ["paita", "chimbote", "callao", "pisco", "ilo"]
CLAVE = {"paita": "peru_norte_paita_sechura", "chimbote": "peru_centro_norte_chimbote", "callao": "peru_centro_callao",
         "pisco": "peru_sur_pisco", "ilo": "peru_sur_ilo"}


def autocorr(x, k):
    a, b = x[:-k], x[k:]
    ok = np.isfinite(a) & np.isfinite(b)
    return 0.0 if ok.sum() < 10 else float(np.corrcoef(a[ok], b[ok])[0, 1])


def corr_neff(x: pd.Series, y: pd.Series, lag: int = 0) -> dict:
    """Pearson entre x (adelantada `lag` meses) e y con n efectivo de Pyper y Peterman (1998)."""
    xs = x.shift(lag)
    df = pd.concat([xs, y], axis=1).dropna()
    n = len(df)
    if n < 24:
        return {"n": n, "n_eff": np.nan, "r": np.nan, "p": np.nan}
    r = float(np.corrcoef(df.iloc[:, 0], df.iloc[:, 1])[0, 1])
    xa, ya = xs.reindex(y.index).to_numpy(float), y.to_numpy(float)
    kmax = max(1, n // 5)
    suma = sum(((n - k) / n) * autocorr(xa, k) * autocorr(ya, k) for k in range(1, kmax + 1))
    n_eff = float(np.clip(n / (1 + 2 * suma), 5, n))
    t = r * np.sqrt((n_eff - 2) / max(1e-12, 1 - r ** 2))
    return {"n": n, "n_eff": round(n_eff, 1), "r": r, "p": float(2 * stats.t.sf(abs(t), n_eff - 2))}


def fdr(p: pd.Series) -> pd.Series:
    p = p.astype(float)
    out = pd.Series(np.nan, index=p.index)
    ok = p.notna()
    if ok.any():
        v = p[ok].to_numpy()
        o = np.argsort(v)
        aj = np.minimum.accumulate((v[o] * len(v) / np.arange(1, len(v) + 1))[::-1])[::-1].clip(max=1)
        res = np.empty(len(v))
        res[o] = aj
        out[ok] = res
    return out


def residuo(y: pd.Series, control: pd.Series) -> pd.Series:
    """Parte de y que no explica el control (regresión lineal simultánea)."""
    df = pd.concat([y, control], axis=1).dropna()
    b = np.polyfit(df.iloc[:, 1], df.iloc[:, 0], 1)
    return (df.iloc[:, 0] - np.polyval(b, df.iloc[:, 1])).reindex(y.index)


def anomalia_mensual(s: pd.Series, base=("1998", "2025")) -> pd.Series:
    ref = s.loc[base[0]:base[1]]
    return s - ref.groupby(ref.index.month).mean().reindex(s.index.month).to_numpy()


def evaluar(x, y, lag, control=None) -> dict:
    """Prueba completa: sin control, parcial, sin 1998 y mitades del periodo."""
    xx, yy = (residuo(x, control), residuo(y, control)) if control is not None else (x, y)
    base = corr_neff(xx, yy, lag)
    sin98 = corr_neff(xx[xx.index.year != 1998], yy[yy.index.year != 1998], lag)
    mitad = yy.dropna().index[len(yy.dropna()) // 2]
    h1 = corr_neff(xx[xx.index < mitad], yy[yy.index < mitad], lag)
    h2 = corr_neff(xx[xx.index >= mitad], yy[yy.index >= mitad], lag)
    return {"lag": lag, "n": base["n"], "n_eff": base["n_eff"], "r": base["r"], "p": base["p"],
            "r_sin1998": sin98["r"], "r_mitad1": h1["r"], "r_mitad2": h2["r"]}


def cerrar(filas: list[dict]) -> pd.DataFrame:
    t = pd.DataFrame(filas)
    t["p_fdr"] = fdr(t["p"])
    t["misma_direccion"] = (np.sign(t["r"]) == np.sign(t["r_sin1998"])) & (np.sign(t["r"]) == np.sign(t["r_mitad1"])) & (np.sign(t["r"]) == np.sign(t["r_mitad2"]))
    t["robusta"] = (t["p_fdr"] < 0.05) & t["misma_direccion"]
    return t.round(4)


# ------------------------------------------------------------------ datos
mon = pd.DataFrame(json.load(open(RAIZ / "pruebas" / "json_pagina" / "monitor_data.json", encoding="utf-8"))["records"])
mon.index = pd.to_datetime(mon["date"]).dt.to_period("M").dt.to_timestamp()
nino = mon["nino12_psl_c"].astype(float)

texto = open(RAIZ / "repos" / "chaski-polar-webpage" / "public" / "assets" / "data" / "datos.js", encoding="utf-8").read()
datos = json.loads(texto[texto.index("{"):texto.rindex("}") + 1])
idx = pd.period_range("1993-01", periods=406, freq="M").to_timestamp()
viento = {}
for z in ZONAS:
    s = datos["series"][CLAVE[z]]
    u = pd.Series([np.nan if v is None else v for v in s["viento_u_m_s"]], index=idx)
    v = pd.Series([np.nan if q is None else q for q in s["viento_v_m_s"]], index=idx)
    viento[z] = anomalia_mensual((v - u) / np.sqrt(2))  # positivo = viento a favor de la surgencia (hacia el NO)

des = pd.read_csv(RAIZ / "punto1_anchoveta" / "1a_desembarques_mensuales_bcrp" / "desembarques_anchoveta_mensual_2003_2026.csv")
des.index = pd.to_datetime(des["mes"] + "-01")

resumen = []

# ------------------------------------------------------------------ A4: asimetría como predicción
filas = []
for z in ZONAS:
    chl, sst = mon[f"chl_{z}_anom_pct"].astype(float), mon[f"sst_{z}_anom_c"].astype(float)
    for nombre, ajuste, prueba in [("2015-2025 (ajuste 1998-2014)", slice("1998", "2014"), slice("2015", "2025")),
                                   ("2026 (ajuste 1998-2025)", slice("1998", "2025"), slice("2026", "2026"))]:
        d = pd.concat([chl, sst], axis=1, keys=["c", "t"]).dropna()
        a, b = d.loc[ajuste], d.loc[prueba]
        if len(b) < 3:
            continue
        X_lin = lambda t: np.c_[np.ones(len(t)), t["t"]]
        X_asi = lambda t: np.c_[np.ones(len(t)), np.maximum(t["t"], 0), np.minimum(t["t"], 0)]
        bl = np.linalg.lstsq(X_lin(a), a["c"], rcond=None)[0]
        ba = np.linalg.lstsq(X_asi(a), a["c"], rcond=None)[0]
        pl, pa = X_lin(b) @ bl, X_asi(b) @ ba
        rm = lambda p: float(np.sqrt(np.mean((b["c"] - p) ** 2)))
        filas.append({"zona": z, "prueba": nombre, "n_meses": len(b), "pend_calor_pct_por_C": round(ba[1], 1), "pend_frio_pct_por_C": round(ba[2], 1),
                      "rmse_sin_modelo": round(rm(0 * pl), 1), "rmse_lineal": round(rm(pl), 1), "rmse_asimetrico": round(rm(pa), 1),
                      "r_asimetrico": round(float(np.corrcoef(pa, b["c"])[0, 1]), 3) if len(b) > 3 else np.nan,
                      "mejora_vs_lineal_pct": round(100 * (1 - rm(pa) / rm(pl)), 1)})
a4 = pd.DataFrame(filas)
a4.to_csv(SALIDA / "pendientes_A4_prediccion_asimetria.csv", index=False)
print("A4\n", a4.to_string(index=False))
m26 = mon.loc["2026", [f"chl_{z}_anom_pct" for z in ZONAS]].dropna(how="all")
print("meses 2026 con clorofila:", list(m26.index.strftime("%Y-%m")))

# ------------------------------------------------------------------ A1: clorofila -> desembarques mensuales
filas = []
for region, col, zonas in [("norte-centro", "norte_centro_t", ["paita", "chimbote", "callao"]), ("sur", "sur_t", ["pisco", "ilo"])]:
    y_all = np.log1p(des[col].astype(float))
    abierto = des[col] > 0
    for z in zonas:
        x = mon[f"chl_{z}_anom_pct"].astype(float).reindex(des.index)
        for modo, y in [("todos los meses", anomalia_mensual(y_all, ("2003", "2025"))), ("solo meses con pesca", anomalia_mensual(y_all.where(abierto), ("2003", "2025")))]:
            for lag in range(0, 5):
                for ctrl in (None, nino.reindex(des.index)):
                    e = evaluar(x, y, lag, ctrl)
                    filas.append({"region": region, "zona_clorofila": z, "meses": modo, "control_nino12": ctrl is not None, **e})
a1 = cerrar(filas)
a1.to_csv(SALIDA / "pendientes_A1_clorofila_desembarques.csv", index=False)
print("\nA1: pruebas", len(a1), "| robustas:", int(a1["robusta"].sum()))
print(a1.sort_values("p").head(8)[["region", "zona_clorofila", "meses", "control_nino12", "lag", "n", "n_eff", "r", "p_fdr", "r_sin1998", "r_mitad1", "r_mitad2", "robusta"]].to_string(index=False))

# ------------------------------------------------------------------ B1: El Niño -> Antártida
filas = []
for xn in ["nino12_psl_c", "oni_c"]:
    for yn in ["sea_ice_antarctic_anom_mkm2", "sam_index", "chl_rey_jorge_anom_pct", "chl_peninsula_antartica_anom_pct"]:
        for lag in range(0, 13):
            filas.append({"predictor": xn, "respuesta": yn, **evaluar(mon[xn].astype(float), mon[yn].astype(float), lag)})
b1 = cerrar(filas)
b1.to_csv(SALIDA / "pendientes_B1_nino_antartida.csv", index=False)
print("\nB1: pruebas", len(b1), "| robustas:", int(b1["robusta"].sum()))
print(b1.sort_values("p").head(8)[["predictor", "respuesta", "lag", "n", "n_eff", "r", "p_fdr", "r_sin1998", "r_mitad1", "r_mitad2", "robusta"]].to_string(index=False))

# ------------------------------------------------------------------ A3: viento ERA5 -> clorofila
filas = []
for z in ZONAS:
    y = mon[f"chl_{z}_anom_pct"].astype(float)
    x = viento[z].reindex(y.index)
    for lag in range(0, 4):
        for ctrl in (None, nino):
            filas.append({"zona": z, "control_nino12": ctrl is not None, **evaluar(x, y, lag, ctrl)})
a3 = cerrar(filas)
a3.to_csv(SALIDA / "pendientes_A3_viento_clorofila.csv", index=False)
print("\nA3: pruebas", len(a3), "| robustas:", int(a3["robusta"].sum()))
print(a3.sort_values("p").head(8)[["zona", "control_nino12", "lag", "n", "n_eff", "r", "p_fdr", "r_sin1998", "r_mitad1", "r_mitad2", "robusta"]].to_string(index=False))

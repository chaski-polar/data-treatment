"""E7: mecanismo físico de El Niño sobre la clorofila (cadena con mediación): Niño 1+2 -> termoclina/oxígeno/nitrato -> clorofila.
Datos: panel de conectividad (región peru_humboldt, 1998-2025) y clorofila observada por zona. Mismo criterio de aceptación."""
import json
from pathlib import Path
import numpy as np, pandas as pd
AQUI = Path(__file__).parent
exec((AQUI / "pruebas_pendientes.py").read_text(encoding="utf-8").split("# ------------------------------------------------------------------ datos")[0])
mon = pd.DataFrame(json.load(open(RAIZ / "pruebas" / "json_pagina" / "monitor_data.json", encoding="utf-8"))["records"])
mon.index = pd.to_datetime(mon["date"]).dt.to_period("M").dt.to_timestamp()
nino = mon["nino12_psl_c"].astype(float)
panel = pd.read_csv(RAIZ / "drive_aaron" / "connectivity_panel_monthly.csv", parse_dates=["date"])
def pv(var, banda, region="peru_humboldt"):
    d = panel[(panel.region == region) & (panel.depth_band == banda)].set_index("date")[var].astype(float)
    return d.reindex(mon.index)
S, M, I = "surface_0_5m", "subsurface_100_200m", "intermediate_200_500m"
vars_ = {"temp 100-200 m": pv("thetao_anom", M), "oxígeno 100-200 m": pv("o2_anom", M), "nitrato 100-200 m": pv("no3_anom", M),
         "oxígeno 200-500 m": pv("o2_anom", I), "nivel del mar": pv("zos_anom", "surface_2d"), "capa de mezcla": pv("mlotst_anom", S),
         "temp superficie": pv("thetao_anom", S), "oxígeno superficie": pv("o2_anom", S), "nitrato superficie": pv("no3_anom", S),
         "fosfato superficie": pv("po4_anom", S), "clorofila (modelo)": pv("chl_anom", S)}
vacias = [k for k, v in vars_.items() if v.notna().sum() < 100]
print("sin datos suficientes:", vacias)
vars_ = {k: v for k, v in vars_.items() if k not in vacias}
filas = []
for nombre, x in vars_.items():           # eslabón A: Niño 1+2 -> variable del mar
    for lag in range(0, 7):
        filas.append({"eslabon": "A Nino1+2 ->", "variable": nombre, **evaluar(nino, x, lag)})
A = cerrar(filas)
filas = []
for nombre, x in vars_.items():           # eslabón B: variable -> clorofila observada de la costa central, sin y con Niño controlado
    for zona in ["chimbote", "callao"]:
        y = mon[f"chl_{zona}_anom_pct"].astype(float)
        for lag in range(0, 4):
            for ctrl in (None, nino):
                filas.append({"eslabon": "B variable ->", "variable": nombre, "zona": zona, "control_nino12": ctrl is not None, **evaluar(x, y, lag, ctrl)})
B = cerrar(filas)
A.to_csv(SALIDA / "nuevos_E7_eslabonA_nino_a_variable.csv", index=False)
B.to_csv(SALIDA / "nuevos_E7_eslabonB_variable_a_clorofila.csv", index=False)
print("ESLABÓN A: Niño 1+2 -> variable (mejor desfase por variable)")
m = A.loc[A.r.abs().groupby(A.variable).idxmax()].sort_values("r")
print(m[["variable", "lag", "n_eff", "r", "p_fdr", "r_sin1998", "r_mitad1", "r_mitad2", "robusta"]].round(3).to_string(index=False))
print("\nESLABÓN B: variable -> clorofila (con Niño 1+2 controlado), mejor por variable y zona")
b = B[B.control_nino12]; m = b.loc[b.r.abs().groupby([b.variable, b.zona]).idxmax()].sort_values("p")
print(m[["variable", "zona", "lag", "n_eff", "r", "p_fdr", "r_sin1998", "robusta"]].round(3).head(10).to_string(index=False))
print("\nrobustas B con control de Niño:", int(b.robusta.sum()), "de", len(b), "| sin control:", int(B[~B.control_nino12].robusta.sum()))

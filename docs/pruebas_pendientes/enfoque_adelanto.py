"""E4: capacidad de adelanto. ¿Cuántos meses antes anticipan El Niño (Niño 1+2) y el ONI la clorofila de cada zona?
Para el ONI se controla Niño 1+2 simultáneo (si adelanta de verdad, aporta información que el Niño costero aún no trae)."""
import json
from pathlib import Path
import numpy as np, pandas as pd
AQUI = Path(__file__).parent
fuente = (AQUI / "pruebas_pendientes.py").read_text(encoding="utf-8").split("# ------------------------------------------------------------------ datos")[0]
exec(fuente)
mon = pd.DataFrame(json.load(open(RAIZ / "pruebas" / "json_pagina" / "monitor_data.json", encoding="utf-8"))["records"])
mon.index = pd.to_datetime(mon["date"]).dt.to_period("M").dt.to_timestamp()
nino, oni = mon["nino12_psl_c"].astype(float), mon["oni_c"].astype(float)
filas = []
for z in ZONAS:
    y = mon[f"chl_{z}_anom_pct"].astype(float)
    for lag in range(0, 9):
        filas.append({"zona": z, "predictor": "Nino1+2", "control": "ninguno", **evaluar(nino, y, lag)})
        filas.append({"zona": z, "predictor": "ONI", "control": "ninguno", **evaluar(oni, y, lag)})
        filas.append({"zona": z, "predictor": "ONI", "control": "Nino1+2 simultaneo", **evaluar(oni, y, lag, nino)})
t = cerrar(filas)
t.to_csv(SALIDA / "nuevos_E4_adelanto_nino_oni.csv", index=False)
print("pruebas", len(t), "| robustas", int(t.robusta.sum()))
for (p, c), g in t.groupby(["predictor", "control"]):
    mejor = g.loc[g.r.abs().groupby(g.zona).idxmax()]
    print(f"\n{p} / control {c}: mejor desfase por zona")
    print(mejor[["zona", "lag", "n_eff", "r", "p_fdr", "r_sin1998", "robusta"]].round(3).to_string(index=False))

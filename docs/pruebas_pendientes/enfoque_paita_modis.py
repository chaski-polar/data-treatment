"""E6: contraste del rebote tardío de Paita (E4) con una segunda fuente: clorofila MODIS-Aqua (NASA, Giovanni)."""
import json
from pathlib import Path
import numpy as np, pandas as pd
AQUI = Path(__file__).parent
exec((AQUI / "pruebas_pendientes.py").read_text(encoding="utf-8").split("# ------------------------------------------------------------------ datos")[0])
mon = pd.DataFrame(json.load(open(RAIZ / "pruebas" / "json_pagina" / "monitor_data.json", encoding="utf-8"))["records"])
mon.index = pd.to_datetime(mon["date"]).dt.to_period("M").dt.to_timestamp()
nino = mon["nino12_psl_c"].astype(float)
g = pd.read_csv(RAIZ / "datos" / "giovanni" / "paita_modisa_chl_mensual_2002-2025.csv", skiprows=9)
g.columns = ["t", "v"]
mod = pd.Series(g.v.replace(-32767, np.nan).to_numpy(), index=pd.to_datetime(g.t).dt.to_period("M").dt.to_timestamp()).reindex(mon.index)
occ = mon["chl_paita_mg_m3"].astype(float).where(mon.index >= "2002-07-01")
def pct(s):
    clim = s.loc["2003":"2025"].groupby(s.loc["2003":"2025"].index.month).mean()
    return 100 * (s / clim.reindex(s.index.month).to_numpy() - 1)
am, ao = pct(mod).loc["2002-07":"2025-11"], pct(occ).loc["2002-07":"2025-11"]
j = pd.concat([am, ao], axis=1, keys=["modis", "occci"]).dropna()
print("correlación de las anomalías MODIS vs OC-CCI en Paita: r = %.3f (n=%d)" % (j.corr().iloc[0, 1], len(j)))
filas = []
for nombre, y in (("MODIS-Aqua (NASA)", am), ("OC-CCI (ESA), mismo periodo", ao)):
    for lag in range(0, 9):
        filas.append({"fuente": nombre, **evaluar(nino, y, lag)})
t = cerrar(filas)
t.to_csv(SALIDA / "nuevos_E6_paita_modis.csv", index=False)
print(t[["fuente", "lag", "n", "n_eff", "r", "p_fdr", "r_mitad1", "r_mitad2", "robusta"]].round(3).to_string(index=False))

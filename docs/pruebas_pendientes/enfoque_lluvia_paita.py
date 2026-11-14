"""E5: ¿el aumento de clorofila y turbidez en Paita-Sechura 2-8 meses después de El Niño viene de la lluvia (escorrentía de ríos)?
Lluvia NASA POWER (PRECTOTCORR) en Paita-Sechura frente a Niño 1+2, a la clorofila y a Kd490 de la zona."""
import json
from pathlib import Path
import numpy as np, pandas as pd
AQUI = Path(__file__).parent
exec((AQUI / "pruebas_pendientes.py").read_text(encoding="utf-8").split("# ------------------------------------------------------------------ datos")[0])
mon = pd.DataFrame(json.load(open(RAIZ / "pruebas" / "json_pagina" / "monitor_data.json", encoding="utf-8"))["records"])
mon.index = pd.to_datetime(mon["date"]).dt.to_period("M").dt.to_timestamp()
nino = mon["nino12_psl_c"].astype(float)
t = open(RAIZ / "repos" / "chaski-polar-webpage" / "public" / "assets" / "data" / "datos.js", encoding="utf-8").read()
j = json.loads(t[t.index("{"):t.rindex("}") + 1])
idx = pd.period_range("1984-01", periods=492, freq="M").to_timestamp()
lluvia = anomalia_mensual(pd.Series([np.nan if v is None else v for v in j["power"]["sitios"]["peru_paita_sechura"]["PRECTOTCORR"]], index=idx)).reindex(mon.index)
chl = mon["chl_paita_anom_pct"].astype(float)
d = pd.read_csv(RAIZ / "datos" / "peru" / "variables_mensuales.csv")
k = d[(d.variable == "turbidez_kd490_m-1") & (d.zona == "peru_norte_paita_sechura")]
kd = anomalia_mensual(pd.Series(k.valor.astype(float).to_numpy(), index=pd.to_datetime(k.mes + "-01")).sort_index()).reindex(mon.index)
filas = []
for nombre, x, y, lags in [("Nino1+2 -> lluvia Paita", nino, lluvia, range(0, 9)), ("lluvia Paita -> clorofila Paita", lluvia, chl, range(0, 7)),
                           ("lluvia Paita -> Kd490 Paita", lluvia, kd, range(0, 7)), ("Nino1+2 -> clorofila Paita", nino, chl, range(0, 9))]:
    for lag in lags:
        filas.append({"relacion": nombre, "control": "ninguno", **evaluar(x, y, lag)})
# ¿Queda efecto del Niño sobre la clorofila de Paita una vez quitada la lluvia?
for lag in range(2, 9):
    c = residuo(chl, lluvia.shift(max(lag - 2, 0)))
    filas.append({"relacion": "Nino1+2 -> clorofila Paita (sin la parte explicada por la lluvia)", "control": "lluvia", **evaluar(nino, c, lag)})
tab = cerrar(filas)
tab.to_csv(SALIDA / "nuevos_E5_lluvia_paita.csv", index=False)
for r, g in tab.groupby("relacion", sort=False):
    m = g.loc[g.r.abs().idxmax()]
    print(f"{r[:70]:70s} mejor lag {int(m.lag)} r={m.r:+.3f} p_fdr={m.p_fdr:.3f} sin98={m.r_sin1998:+.3f} robusta={bool(m.robusta)}")

# ---- robustez: quitar un año a la vez (la relación Niño 1+2 -> clorofila de Paita a 5 meses)
rs = {}
for a in sorted(set(mon.index.year)):
    m = mon.index.year != a
    rs[a] = corr_neff(nino[m], chl[m], 5)["r"]
s = pd.Series(rs)
print(f"\nquitando un año a la vez: r entre {s.min():+.3f} y {s.max():+.3f}; el año que más la baja: {s.idxmin()}")
# ¿se repite en las otras zonas con el mismo desfase? (para ver si es un efecto del norte)
for z in ["chimbote", "callao", "pisco", "ilo"]:
    print(z, "lag 5:", round(corr_neff(nino, mon[f"chl_{z}_anom_pct"].astype(float), 5)["r"], 3))

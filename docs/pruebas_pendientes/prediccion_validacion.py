"""E8: capacidad predictiva con validación honesta. Origen móvil (se ajusta solo con el pasado): predicción de la anomalía de clorofila
(%) de cada zona con h meses de antelación a partir de Niño 1+2 y de la propia clorofila, comparada con la climatología (0) y con la
persistencia. Luego, prueba con 2026 (observado) usando datos del servidor."""
import json
from pathlib import Path
import numpy as np, pandas as pd
RAIZ = Path(r"D:\hackathon\NASA"); SAL = RAIZ / "pruebas" / "fitoplancton" / "tablas"
mon = pd.DataFrame(json.load(open(RAIZ / "pruebas" / "json_pagina" / "monitor_data.json", encoding="utf-8"))["records"])
mon.index = pd.to_datetime(mon["date"]).dt.to_period("M").dt.to_timestamp(); nino = mon["nino12_psl_c"].astype(float)
t = open(RAIZ / "repos" / "chaski-polar-webpage" / "public" / "assets" / "data" / "datos.js", encoding="utf-8").read()
j = json.loads(t[t.index("{"):t.rindex("}") + 1]); idx = pd.period_range("1993-01", periods=406, freq="M").to_timestamp()
CL = {"paita": "peru_norte_paita_sechura", "chimbote": "peru_centro_norte_chimbote", "callao": "peru_centro_callao", "pisco": "peru_sur_pisco", "ilo": "peru_sur_ilo"}
def anom_2026(z):
    s = pd.Series([np.nan if v is None else v for v in j["series"][CL[z]]["clorofila_mg_m3"]], index=idx)
    b = s.loc["1998":"2025"]; c = b.groupby(b.index.month).mean()
    return 100 * (s / c.reindex(s.index.month).to_numpy() - 1)
filas = []
for z in CL:
    y = anom_2026(z).reindex(nino.index)
    for h in (1, 2, 3):
        d = pd.concat([y, nino.shift(h), y.shift(h)], axis=1, keys=["y", "n", "p"])
        pred, obs, pers, clim = [], [], [], []
        for anio in range(2010, 2026):
            tr = d.loc[:f"{anio - 1}-12"].dropna(); te = d.loc[str(anio)].dropna()
            if len(tr) < 60 or te.empty: continue
            X = np.c_[np.ones(len(tr)), tr.n, tr.p]; b = np.linalg.lstsq(X, tr.y, rcond=None)[0]
            pred += list(np.c_[np.ones(len(te)), te.n, te.p] @ b); obs += list(te.y); pers += list(te.p); clim += [0.0] * len(te)
        obs, pred, pers = map(np.array, (obs, pred, pers)); r = lambda p: float(np.sqrt(np.mean((obs - p) ** 2)))
        filas.append({"zona": z, "horizonte_meses": h, "n": len(obs), "rmse_climatologia": round(r(0 * obs), 1), "rmse_persistencia": round(r(pers), 1), "rmse_modelo": round(r(pred), 1),
                      "habilidad_vs_climatologia_pct": round(100 * (1 - r(pred) / r(0 * obs)), 1), "habilidad_vs_persistencia_pct": round(100 * (1 - r(pred) / r(pers)), 1), "r": round(float(np.corrcoef(obs, pred)[0, 1]), 3)})
T = pd.DataFrame(filas); T.to_csv(SAL / "nuevos_E8_prediccion_origen_movil.csv", index=False)
print("Origen móvil 2010-2025 (ajuste solo con el pasado)\n", T.to_string(index=False))
# 2026: ajuste con 1998-2025, predicción con Niño 1+2 conocido, y comparación con la clorofila observada de 2026
out = []
for z in CL:
    y = anom_2026(z).reindex(nino.index); d = pd.concat([y, nino], axis=1, keys=["y", "n"]); tr = d.loc[:"2025-12"].dropna()
    b = np.polyfit(tr.n, tr.y, 1); te = d.loc["2026"].dropna()
    for f, row in te.iterrows(): out.append({"zona": z, "mes": f.strftime("%Y-%m"), "nino12": round(row.n, 2), "observada_pct": round(row.y, 1), "predicha_pct": round(float(np.polyval(b, row.n)), 1)})
O = pd.DataFrame(out); O.to_csv(SAL / "nuevos_E8_prediccion_2026.csv", index=False)
print("\n2026 (meses con clorofila observada y Niño 1+2):", O.mes.nunique(), "meses")
print(O.groupby("zona").apply(lambda g: pd.Series({"meses": len(g), "observada_media": round(g.observada_pct.mean(), 1), "predicha_media": round(g.predicha_pct.mean(), 1), "r": round(float(np.corrcoef(g.observada_pct, g.predicha_pct)[0, 1]), 2) if len(g) > 3 else np.nan})).to_string())

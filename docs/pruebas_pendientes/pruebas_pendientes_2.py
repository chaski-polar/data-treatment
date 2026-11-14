"""Segunda tanda de pruebas pendientes (ver PRUEBAS_POSIBLES.md): A5 nivel del mar, A2 Kd490/oxígeno, B2 SAM x El Niño,
B3 cadena con puente en el Pacífico Sur, B4 corrientes, B5 otras especies de la FAO. Usa el panel de conectividad
(1998-2025) y los datos locales; las funciones estadísticas son las de pruebas_pendientes.py."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

AQUI = Path(__file__).parent
fuente = (AQUI / "pruebas_pendientes.py").read_text(encoding="utf-8").split("# ------------------------------------------------------------------ datos")[0]
fuente = fuente.replace("if n < 24:", "if n < MIN_N:")
MIN_N = 24
exec(fuente)  # autocorr, corr_neff, fdr, residuo, anomalia_mensual, evaluar, cerrar, RAIZ, SALIDA, ZONAS

mon = pd.DataFrame(json.load(open(RAIZ / "pruebas" / "json_pagina" / "monitor_data.json", encoding="utf-8"))["records"])
mon.index = pd.to_datetime(mon["date"]).dt.to_period("M").dt.to_timestamp()
nino = mon["nino12_psl_c"].astype(float)

panel = pd.read_csv(RAIZ / "drive_aaron" / "connectivity_panel_monthly.csv", parse_dates=["date"])


def pv(region, var, banda="surface_0_5m"):
    d = panel[(panel.region == region) & (panel.depth_band == banda)].set_index("date")[var].astype(float)
    return d.reindex(mon.index)


def mejor_banda_zos():
    c = panel[panel.zos.notna()].groupby(["region", "depth_band"]).size()
    return c.to_string()


texto = open(RAIZ / "repos" / "chaski-polar-webpage" / "public" / "assets" / "data" / "datos.js", encoding="utf-8").read()
datos = json.loads(texto[texto.index("{"):texto.rindex("}") + 1])
SAM, HIELO = mon["sam_index"].astype(float), mon["sea_ice_antarctic_anom_mkm2"].astype(float)
resumen = {}


def reportar(nombre, t, cols):
    t.to_csv(SALIDA / f"pendientes_{nombre}.csv", index=False)
    resumen[nombre] = (len(t), int(t["robusta"].sum()))
    print(f"\n{nombre}: pruebas {len(t)} | robustas {int(t['robusta'].sum())}")
    print(t.sort_values("p").head(5)[cols].to_string(index=False))


COLS = ["lag", "n", "n_eff", "r", "p_fdr", "r_sin1998", "r_mitad1", "r_mitad2", "robusta"]

# ---------------------------------------------------------------- A5 nivel del mar -> clorofila
print("zos disponible en:\n", mejor_banda_zos())
zos = pv("peru_humboldt", "zos_anom", "surface_2d")
if zos.notna().sum() < 100:
    zos = pv("peru_humboldt", "zos_anom")
filas = []
for z in ZONAS:
    y = mon[f"chl_{z}_anom_pct"].astype(float)
    for lag in range(0, 5):
        for ctrl in (None, nino):
            filas.append({"zona": z, "control_nino12": ctrl is not None, **evaluar(zos, y, lag, ctrl)})
reportar("A5_nivel_mar_clorofila", cerrar(filas), ["zona", "control_nino12"] + COLS)

# ---------------------------------------------------------------- A2 Kd490 y oxigeno
kd = anomalia_mensual(mon["kd490"].astype(float))
o2 = pv("peru_humboldt", "o2_anom")
filas = []
for nombre, y in [("o2_peru_humboldt", o2), ("chl_occci", anomalia_mensual(mon["chlorophyll_occci"].astype(float)))]:
    for lag in range(0, 4):
        for ctrl in (None, nino):
            filas.append({"respuesta": nombre, "control_nino12": ctrl is not None, **evaluar(kd, y, lag, ctrl)})
reportar("A2_kd490_oxigeno", cerrar(filas), ["respuesta", "control_nino12"] + COLS)

# ---------------------------------------------------------------- B2 SAM x Nino (interaccion, prueba por desplazamiento circular)
def t_interaccion(y, s, n):
    d = pd.concat([y, s, n], axis=1).dropna()
    z = (d - d.mean()) / d.std()
    X = np.c_[np.ones(len(z)), z.iloc[:, 1], z.iloc[:, 2], z.iloc[:, 1] * z.iloc[:, 2]]
    b, *_ = np.linalg.lstsq(X, z.iloc[:, 0], rcond=None)
    res = z.iloc[:, 0] - X @ b
    s2 = res @ res / (len(z) - 4)
    return b[3] / np.sqrt(s2 * np.linalg.inv(X.T @ X)[3, 3]), b[3]


rng = np.random.default_rng(7)
filas = []
for yn in ["chl_rey_jorge_anom_pct", "chl_peninsula_antartica_anom_pct", "sea_ice_antarctic_anom_mkm2"]:
    y = mon[yn].astype(float)
    for lag in (0, 6):
        n_l = nino.shift(lag)
        t_obs, beta = t_interaccion(y, SAM, n_l)
        nulos = []
        for _ in range(1000):
            k = int(rng.integers(24, len(n_l) - 24))
            nulos.append(t_interaccion(y, SAM, pd.Series(np.roll(n_l.to_numpy(), k), index=n_l.index))[0])
        p = float((np.abs(nulos) >= abs(t_obs)).mean())
        sin98 = t_interaccion(y[y.index.year != 1998], SAM[SAM.index.year != 1998], n_l[n_l.index.year != 1998])[1]
        filas.append({"respuesta": yn, "lag_nino": lag, "coef_interaccion": round(beta, 3), "coef_sin1998": round(sin98, 3), "p_desplazamiento": round(p, 4)})
b2 = pd.DataFrame(filas)
b2["p_fdr"] = fdr(b2["p_desplazamiento"]).round(4)
b2["robusta"] = (b2["p_fdr"] < 0.05) & (np.sign(b2["coef_interaccion"]) == np.sign(b2["coef_sin1998"]))
b2.to_csv(SALIDA / "pendientes_B2_sam_x_nino.csv", index=False)
resumen["B2_sam_x_nino"] = (len(b2), int(b2["robusta"].sum()))
print("\nB2: pruebas", len(b2), "| robustas", int(b2["robusta"].sum()))
print(b2.to_string(index=False))

# ---------------------------------------------------------------- B3 cadena con puente
puentes = ["south_pacific_subtropical", "south_pacific_intermediate"]
vars_p = ["thetao_anom", "no3_anom", "chl_anom"]
f1, f2 = [], []
for reg in puentes:
    for vp in vars_p:
        b = pv(reg, vp)
        for xn, x in [("sam", SAM), ("hielo", HIELO)]:
            for lag in range(0, 13):
                f1.append({"puente": reg, "var_puente": vp, "origen": xn, **evaluar(x, b, lag)})
        for zona in ["chimbote", "callao"]:
            y = mon[f"chl_{zona}_anom_pct"].astype(float)
            for lag in range(0, 7):
                f2.append({"puente": reg, "var_puente": vp, "zona": zona, **evaluar(b, y, lag)})
e1, e2 = cerrar(f1), cerrar(f2)
e1.to_csv(SALIDA / "pendientes_B3_eslabon1_antartida_puente.csv", index=False)
e2.to_csv(SALIDA / "pendientes_B3_eslabon2_puente_peru.csv", index=False)
cadenas = e1[e1.robusta][["puente", "var_puente"]].drop_duplicates().merge(e2[e2.robusta][["puente", "var_puente"]].drop_duplicates())
resumen["B3_eslabon1"] = (len(e1), int(e1["robusta"].sum()))
resumen["B3_eslabon2"] = (len(e2), int(e2["robusta"].sum()))
print("\nB3 eslabón 1 (Antártida→puente): pruebas", len(e1), "| robustas", int(e1.robusta.sum()))
print(e1.sort_values("p").head(4)[["puente", "var_puente", "origen"] + COLS].to_string(index=False))
print("B3 eslabón 2 (puente→Perú): pruebas", len(e2), "| robustas", int(e2.robusta.sum()))
print(e2.sort_values("p").head(4)[["puente", "var_puente", "zona"] + COLS].to_string(index=False))
print("cadenas completas (ambos eslabones robustos):", len(cadenas))

# ---------------------------------------------------------------- B4 corrientes -> temperatura y nitrato del Peru
filas = []
for reg in ["transition_humboldt", "south_pacific_intermediate"]:
    for comp in ["uo_anom", "vo_anom"]:
        x = pv(reg, comp)
        for destino in ["thetao_anom", "no3_anom"]:
            y = pv("peru_humboldt", destino)
            for lag in range(0, 13):
                for ctrl in (None, nino):
                    filas.append({"region_corriente": reg, "componente": comp, "destino": destino, "control_nino12": ctrl is not None, **evaluar(x, y, lag, ctrl)})
reportar("B4_corrientes_temperatura_nitrato", cerrar(filas), ["region_corriente", "componente", "destino", "control_nino12"] + COLS)

# ---------------------------------------------------------------- B5 otras especies de la FAO (anual, con tendencia quitada)
MIN_N = 15
exec(fuente.replace("if n < 24:", "if n < 15:"))  # redefine con minimo anual
anios = pd.to_datetime([f"{a}-01-01" for a in range(1995, 1995 + 30)])
anual = lambda s: s.groupby(s.index.year).mean().set_axis(pd.to_datetime([f"{a}-01-01" for a in sorted(set(s.index.year))]))
nino_a, sam_a, hielo_a = anual(nino), anual(SAM), anual(HIELO)
filas = []
for sp, serie in datos["pesca"].items():
    if sp == "inicio" or not isinstance(serie, list):
        continue
    y = pd.Series([np.nan if v in (None, 0) else float(v) for v in serie], index=anios).loc["1998":"2024"]
    y = np.log(y)
    y = y - np.polyval(np.polyfit(np.arange(len(y)), y.fillna(y.mean()), 1), np.arange(len(y)))  # quita la tendencia lineal
    for xn, x in [("sam", sam_a), ("hielo", hielo_a)]:
        for lag in range(0, 4):
            for ctrl in (None, nino_a):
                filas.append({"especie": sp, "predictor": xn, "control_nino12": ctrl is not None, **evaluar(x, y, lag, ctrl)})
reportar("B5_especies_fao", cerrar(filas), ["especie", "predictor", "control_nino12"] + COLS)

print("\nRESUMEN", resumen)

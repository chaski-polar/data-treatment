"""E9: tendencia por celda (dónde sube o baja): Mann-Kendall y pendiente de Sen sobre promedios anuales de cada celda de los mapas de
la web (clorofila de 0,5 grados y anomalía de temperatura de 1 grado), con corrección FDR (Benjamini-Hochberg) entre celdas y con tres
años de inicio (1998, 2003, 2012) para mostrar cuánto depende el resultado del periodo."""
import base64, gzip, json
from pathlib import Path
import numpy as np
from scipy import stats

SRC = Path(r"D:\hackathon\NASA\repos\chaski-polar-estetica\public\assets\data\mapas\mapas.json")
SAL = Path(r"D:\hackathon\NASA\pruebas\fitoplancton\tablas\nuevos_E9_tendencias_por_celda.json")
d = json.load(open(SRC, encoding="utf-8"))
NM = d["meses"]


def b(s):
    return np.frombuffer(gzip.decompress(base64.b64decode(s)), np.uint8)


def fdr(p):
    q = np.full(len(p), np.nan)
    v = np.isfinite(p)
    o = np.argsort(p[v])
    pv = p[v][o]
    aj = np.minimum.accumulate((pv * v.sum() / np.arange(1, v.sum() + 1))[::-1])[::-1].clip(max=1)
    t = np.empty(v.sum())
    t[o] = aj
    q[v] = t
    return q


INICIOS = [1998, 2003, 2012]
out = {"inicio": d["inicio"], "lat_n": d["lat_n"], "lon_o": d["lon_o"], "fin": 2025, "inicios": INICIOS}
for nombre in ("clorofila", "temperatura"):
    g = d["capas"][nombre]
    filas, cols = g["filas"], g["cols"]
    mask = np.unpackbits(np.frombuffer(base64.b64decode(g["mascara"]), np.uint8))[: filas * cols].astype(bool)
    idx = np.flatnonzero(mask)
    datos = b(g["datos"]).reshape(len(idx), NM)
    if nombre == "clorofila":
        val = np.where(datos > 0, g["log0"] + (datos.astype(float) - 1) / 254 * (g["log1"] - g["log0"]), np.nan)
        conv = lambda s_: (10 ** s_ - 1) * 100
    else:
        val = np.where(datos > 0, (datos.astype(float) - 128) * g["paso"], np.nan)
        conv = lambda s_: s_
    capa = {"celda": g["celda"], "filas": filas, "cols": cols, "indices": idx.tolist(),
            "unidad": "% per decade" if nombre == "clorofila" else "°C per decade (anomaly)", "por_inicio": {}}
    for a0 in INICIOS:
        anios = np.arange(a0, 2026)
        pend = np.full(len(idx), np.nan)
        p = np.full(len(idx), np.nan)
        for i, r in enumerate(val):
            ym = np.array([np.nanmean(r[(a - 1998) * 12:(a - 1998) * 12 + 12]) if np.isfinite(r[(a - 1998) * 12:(a - 1998) * 12 + 12]).sum() >= 8 else np.nan for a in anios])
            ok = np.isfinite(ym)
            if ok.sum() < 0.7 * len(anios):
                continue
            p[i] = stats.kendalltau(anios[ok], ym[ok])[1]
            pend[i] = stats.theilslopes(ym[ok], anios[ok])[0] * 10
        q = fdr(p)
        v = np.isfinite(p)
        sig = (q < 0.05) & v
        pp = np.where(v, conv(pend), np.nan)
        print(f"{nombre} desde {a0}: celdas {int(v.sum())}; p<0,05 sin corregir {100 * (p[v] < 0.05).mean():.0f} %; con FDR {int(sig.sum())} ({100 * sig.sum() / v.sum():.0f} %): "
              f"suben {int((sig & (pp > 0)).sum())}, bajan {int((sig & (pp < 0)).sum())}; mediana {np.nanmedian(pp):+.3f}")
        capa["por_inicio"][str(a0)] = {"pendiente": [None if not np.isfinite(x) else round(float(x), 2 if nombre == "clorofila" else 3) for x in pp],
                                       "significativa": [int(x) for x in sig]}
    out[nombre] = capa
json.dump(out, open(SAL, "w"), separators=(",", ":"))
print("JSON KB:", SAL.stat().st_size // 1024)

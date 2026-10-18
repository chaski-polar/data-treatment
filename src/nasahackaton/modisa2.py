"""
v2: ¿qué cambió en la clorofila de bahías de cultivo peruanas (MODIS-Aqua, mensual 4 km)?

Mejoras sobre v1:
  1) Máscara de agua: la cobertura se mide SOLO sobre píxeles de agua (v1 contaba la tierra).
  2) Control de calidad: un mes entra en la serie solo si tiene datos en >= MIN_FRAC_PIX_MES de los píxeles de agua.
  3) Tendencia con p-valor corregido por autocorrelación lag-1 (n efectivo), además del p ingenuo.
  4) Extremos: meses con anomalía > UMBRAL_SD desviaciones; frecuencia por año y tendencia.
  5) Calendario de riesgo: probabilidad de mes extremo por mes calendario.
  6) Mapa de tendencia por píxel con corrección por pruebas múltiples (Benjamini-Hochberg, FDR).

Salidas: modisa_v2_<sitio>.png (un panel por sitio), modisa_v2_resumen.csv.
Uso: pip install xarray netCDF4 pandas numpy scipy matplotlib ; python revisar_modisa_bahias_v2.py
Las cajas son APROXIMADAS (de memoria): ajústalas mirando un mapa.
Límite: la clorofila satelital es un indicador de biomasa, no de toxicidad; no es un sistema de alerta.
"""
import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats
import matplotlib.pyplot as plt

CANDIDATOS = [
    ("https://oceanwatch.pifsc.noaa.gov/erddap", "aqua_chla_monthly_2018_0"),
    ("https://oceanwatch.pifsc.noaa.gov/erddap", "esa-cci-chla-monthly-v6-0"),
    ("https://oceanwatch.pifsc.noaa.gov/erddap", "noaa_snpp_chla_monthly"),
    ("https://coastwatch.pfeg.noaa.gov/erddap", "erdMH1chlamday_R2022SQ"),
    ("https://coastwatch.pfeg.noaa.gov/erddap", "erdMH1chlamday"),
]
VAR_CANDIDATAS = ["chlor_a", "chlorophyll", "chla"]

# (lat_min, lat_max, lon_min, lon_max)
# SITIOS = {
#     "sechura": (-6.0, -5.2, -81.2, -80.6),
#     "samanco": (-9.5, -9.0, -78.8, -78.3),
#     "paracas": (-14.1, -13.6, -76.5, -76.0),
# }
SITIOS = {
    # --- COSTA NORTE ---
    "tumbes": (-3.9, -3.4, -80.9, -80.2),
    "talara": (-4.8, -4.3, -81.4, -81.0),
    "paita": (-5.3, -4.8, -81.3, -80.9),
    "sechura": (-6.0, -5.2, -81.2, -80.6),
    "pimentel": (-7.0, -6.6, -80.1, -79.8),
    "pacasmayo": (-7.5, -7.1, -79.8, -79.5),
    "chimbote": (-9.2, -8.8, -78.8, -78.5),
    "samanco": (-9.5, -9.0, -78.8, -78.3),
    "casma": (-9.7, -9.3, -78.5, -78.2),

    # --- COSTA CENTRO ---
    "huarmey": (-10.2, -9.9, -78.3, -78.0),
    "supe_huacho": (-11.2, -10.7, -77.8, -77.5),
    "chancay": (-11.6, -11.4, -77.3, -77.1),
    "callao_lima": (-12.2, -11.9, -77.3, -77.0),
    "lurin_chilca": (-12.5, -12.2, -76.9, -76.7),
    "pisco": (-13.8, -13.6, -76.4, -76.1),
    "paracas": (-14.1, -13.6, -76.5, -76.0),

    # --- COSTA SUR ---
    "san_juan_de_marcona": (-15.4, -15.1, -75.3, -75.1),
    "chala": (-15.9, -15.7, -74.4, -74.2),
    "ico_atico": (-16.3, -16.1, -73.7, -73.5),
    "camana": (-16.7, -16.5, -72.8, -72.5),
    "mollendo_matarani": (-17.1, -16.9, -72.2, -71.9),
    "ilo": (-17.8, -17.5, -71.5, -71.3),
    "yarada_tacna": (-18.3, -18.0, -70.9, -70.4),
}
# SITIOS = {
#     "isla_adelaida": (-67.5, -66.0, -69.0, -67.0),
#     "isla_rey_jorge": (-62.3, -61.8, -59.0, -57.5),
#     "estrecho_de_bransfield": (-63.5, -61.8, -61.5, -57.0),
# }
INICIO, FIN = "2003-01-01", "2025-12-31"

EXCLUIR = ("2015-01-01", "2017-12-31")

MIN_FRAC_AGUA = 0.10     # un píxel es "agua" si tiene dato en >=10% de los meses (tierra: ~0%)
MIN_FRAC_PIX_MES = 0.25  # un mes cuenta si >=25% de los píxeles de agua tienen dato
UMBRAL_SD = 1.0          # mes extremo: anomalía log10 > 1 desviación estándar
MIN_MESES_ANIO = 6       # año válido para frecuencia de extremos
MIN_MESES_PIXEL = 60     # meses mínimos para estimar tendencia en un píxel
ALFA = 0.05


def cargar(ds, var, caja):
    la0, la1, lo0, lo1 = caja
    da = ds[var].sel(time=slice(INICIO, FIN))
    da = da.sortby("latitude").sortby("longitude")
    lon = da["longitude"].values
    if lon.min() >= 0 and lo0 < 0:  # dataset en [0, 360]
        lo0, lo1 = lo0 + 360, lo1 + 360
    da = da.sel(latitude=slice(la0, la1), longitude=slice(lo0, lo1))
    if "altitude" in da.dims:
        da = da.squeeze("altitude", drop=True)
    if EXCLUIR:
        a, b = np.datetime64(EXCLUIR[0]), np.datetime64(EXCLUIR[1])
        da = da.where(~((da["time"] >= a) & (da["time"] <= b)))
    return da.load()


def tendencia(t, y):
    """Theil-Sen + Mann-Kendall con p ajustado por autocorrelación lag-1 (aproximado)."""
    t, y = np.asarray(t, float), np.asarray(y, float)
    ok = np.isfinite(y)
    t, y = t[ok], y[ok]
    n = len(y)
    if n < 10:
        return None
    tau, p_naive = stats.kendalltau(t, y)
    slope, intercept, lo, hi = stats.theilslopes(y, t)
    res = y - (intercept + slope * t)
    r = np.corrcoef(res[:-1], res[1:])[0, 1] if n > 3 else 0.0
    r = float(np.clip(np.nan_to_num(r), 0.0, 0.95))  # solo inflamos si hay autocorrelación positiva
    n_eff = n * (1 - r) / (1 + r)
    z = tau / np.sqrt(2 * (2 * n + 5) / (9 * n * (n - 1)))
    p_adj = 2 * (1 - stats.norm.cdf(abs(z) * np.sqrt(n_eff / n)))
    return dict(n=n, tau=tau, p_naive=p_naive, p=p_adj, r1=r, n_eff=n_eff,
                pend=slope, lo=lo, hi=hi)


def bh_fdr(p, alfa=ALFA):
    p = np.asarray(p)
    m = len(p)
    sig = np.zeros(m, bool)
    if m == 0:
        return sig
    orden = np.argsort(p)
    ok = p[orden] <= alfa * np.arange(1, m + 1) / m
    if ok.any():
        sig[orden[: np.max(np.where(ok)[0]) + 1]] = True
    return sig


def anom_log(da):
    logs = np.log10(da.where(da > 0))
    clim = logs.groupby("time.month").mean("time")
    return logs.groupby("time.month") - clim


def decimal(idx):
    idx = pd.DatetimeIndex(idx)
    return (idx.year + (idx.month - 0.5) / 12).values


def pct(slope_log):  # pendiente log10/año -> % por año
    return (10 ** slope_log - 1) * 100


def revisar(nombre, caja, ds, var, graficar=True):
    da = cargar(ds, var, caja)
    agua = da.notnull().mean("time") >= MIN_FRAC_AGUA
    n_agua = int(agua.sum())
    ny, nx = da.sizes["latitude"], da.sizes["longitude"]
    print(f"\n=== {nombre} ===")
    print(f"Caja: {ny}x{nx} = {ny*nx} píxeles; de agua: {n_agua}")
    if n_agua < 5:
        print("Muy pocos píxeles de agua: la resolución de 4 km no alcanza para esta caja.")
        return None

    # --- cobertura real sobre agua ---
    da_w = da.where(agua)
    frac_pix = da_w.notnull().sum(["latitude", "longitude"]) / n_agua
    ok_mes = frac_pix >= MIN_FRAC_PIX_MES
    por_mes = frac_pix.groupby("time.month").mean()
    print(f"Cobertura media sobre agua: {float(frac_pix.mean())*100:.0f}% de píxeles por mes")
    print("  por mes calendario (%):", {int(m): round(float(v) * 100) for m, v in zip(por_mes["month"].values, por_mes.values)})
    print(f"Meses utilizables (>= {MIN_FRAC_PIX_MES:.0%} de píxeles con dato): {int(ok_mes.sum())} de {da.sizes['time']}")

    serie = da_w.mean(["latitude", "longitude"], skipna=True).where(ok_mes).to_series()
    serie.index = pd.DatetimeIndex(serie.index)
    logs = np.log10(serie.where(serie > 0))
    anom = logs - logs.groupby(logs.index.month).transform("mean")

    # --- tendencia de la anomalía (caja) ---
    res = tendencia(decimal(anom.index), anom.values)
    fila = dict(sitio=nombre, pix_agua=n_agua, cobertura_pct=float(frac_pix.mean()) * 100,
                meses_ok=int(ok_mes.sum()))
    if res:
        print(f"Tendencia caja: {pct(res['pend']):+.2f} %/año [{pct(res['lo']):+.2f}, {pct(res['hi']):+.2f}] "
              f"p_naive={res['p_naive']:.3f}  p_ajustado={res['p']:.3f}  (lag1={res['r1']:.2f}, n={res['n']}, n_eff={res['n_eff']:.0f})")
        fila.update(tend_pct_anio=pct(res["pend"]), tend_p_ajustado=res["p"])

    # --- extremos ---
    sd = float(anom.std())
    # ext = (anom > UMBRAL_SD * sd).where(anom.notnull())
    ext = (anom > UMBRAL_SD * sd).astype(float).where(anom.notnull())
    cal = ext.groupby(ext.index.month).mean()
    cal_n = anom.notnull().groupby(anom.index.month).sum()
    print(f"Mes extremo = anomalía > {UMBRAL_SD:.1f} SD ({UMBRAL_SD*sd:+.3f} log10). Prob. por mes calendario (%):",
          # {int(m): round(float(v) * 100) for m, v in cal.items()})
        {int(m): round(float(v) * 100) for m, v in cal.items() if np.isfinite(v)})
    print("  meses con dato por mes calendario:", {int(m): int(v) for m, v in cal_n.items()})
    anual = pd.DataFrame({"ext": ext, "ok": anom.notnull()}).groupby(anom.index.year).agg(
        ext=("ext", "mean"), n=("ok", "sum"))
    anual = anual[anual["n"] >= MIN_MESES_ANIO]
    r_ext = tendencia(anual.index.values.astype(float), anual["ext"].values)
    if r_ext:
        print(f"Frecuencia anual de extremos: pendiente {r_ext['pend']*100:+.2f} puntos %/año "
              f"[{r_ext['lo']*100:+.2f}, {r_ext['hi']*100:+.2f}], p_ajustado={r_ext['p']:.3f} (años válidos: {len(anual)})")
        fila.update(ext_pend_pp_anio=r_ext["pend"] * 100, ext_p=r_ext["p"])

    # --- mapa por píxel con FDR ---
    an_px = anom_log(da_w)
    t_all = decimal(da["time"].values)
    lat, lon = da["latitude"].values, da["longitude"].values
    mapa = np.full((ny, nx), np.nan)
    pv = np.full((ny, nx), np.nan)
    for i in range(ny):
        for j in range(nx):
            if not agua.values[i, j]:
                continue
            y = an_px.values[:, i, j]
            if np.isfinite(y).sum() < MIN_MESES_PIXEL:
                continue
            r = tendencia(t_all, y)
            if r:
                mapa[i, j], pv[i, j] = pct(r["pend"]), r["p"]
    idx = np.where(np.isfinite(pv))
    sig_flat = bh_fdr(pv[idx])
    sig = np.zeros_like(pv, bool)
    sig[idx[0][sig_flat], idx[1][sig_flat]] = True
    n_t, n_s = len(idx[0]), int(sig.sum())
    n_pos, n_neg = int((sig & (mapa > 0)).sum()), int((sig & (mapa < 0)).sum())
    print(f"Mapa por píxel: {n_t} píxeles evaluables; significativos tras FDR: {n_s} (suben {n_pos}, bajan {n_neg})")
    fila.update(px_eval=n_t, px_sig_fdr=n_s, px_suben=n_pos, px_bajan=n_neg)

    if graficar:
        fig, ax = plt.subplots(1, 4, figsize=(17, 3.4))
        ax[0].plot(serie.index, serie.values, ".-", lw=0.6)
        ext_idx = anom.index[(anom > UMBRAL_SD * sd).fillna(False)]
        ax[0].plot(ext_idx, serie.loc[ext_idx], "r.", ms=6, label="extremo")
        ax[0].set_yscale("log"); ax[0].set_title(f"{nombre}: chl mensual (mg/m3)"); ax[0].legend()
        ax[1].bar(cal.index, cal.values * 100); ax[1].set_title("Prob. de mes extremo (%)")
        ax[1].set_xlabel("mes calendario"); ax[1].set_xticks(range(1, 13))
        ax[2].plot(anual.index, anual["ext"] * 100, "o-"); ax[2].set_title("% meses extremos por año")
        lim = np.nanmax(np.abs(mapa)) if np.isfinite(mapa).any() else 1
        pc = ax[3].pcolormesh(lon, lat, mapa, cmap="RdBu_r", vmin=-lim, vmax=lim, shading="nearest")
        yy, xx = np.where(sig)
        ax[3].plot(lon[xx], lat[yy], "k.", ms=4)
        ax[3].set_title("Tendencia %/año (· = signif. FDR)")
        fig.colorbar(pc, ax=ax[3])
        plt.tight_layout()
        plt.savefig(f"modisa_v2_{nombre}.png", dpi=120)
        plt.close(fig)
    return fila


def abrir():
    errores = []
    for srv, ds_id in CANDIDATOS:
        url = f"{srv}/griddap/{ds_id}"
        print(f"Intentando abrir {url}...")
        try:
            ds = xr.open_dataset(url)
            var = next((v for v in VAR_CANDIDATAS if v in ds.data_vars), None)
            if var is None:
                raise ValueError(f"sin variable de clorofila en {list(ds.data_vars)}")
            print(f"Abrió: {url} | variable '{var}' | dims {dict(ds.sizes)}")
            return ds, var
        except Exception as e:  # noqa: BLE001
            errores.append((url, str(e)[:120]))
    for u, e in errores:
        print(" -", u, "->", e)
    raise SystemExit("No se pudo conectar a ningún servidor ERDDAP.")


if __name__ == "__main__":
    ds, var = abrir()
    filas = [f for f in (revisar(n, c, ds, var) for n, c in SITIOS.items()) if f]
    pd.DataFrame(filas).to_csv("modisa_v2_resumen.csv", index=False)
    print("\nGuardado: modisa_v2_<sitio>.png y modisa_v2_resumen.csv")

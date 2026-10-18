"""
Revisa si MODIS-Aqua (clorofila mensual 4 km) alcanza para bahías de cultivo peruanas.
Responde 3 preguntas por sitio:
  1) ¿Cuántos píxeles caen en la caja? (resolución vs tamaño de la bahía)
  2) ¿Qué % de píxeles-mes tiene dato? (nubes / costa / turbidez)
  3) ¿Hay tendencia significativa tras quitar la estacionalidad? (Theil-Sen + Mann-Kendall)

Uso:  pip install xarray netCDF4 pandas numpy scipy matplotlib
      python revisar_modisa_bahias.py
Las cajas son APROXIMADAS (de memoria): ajústalas mirando un mapa.
El nombre de variable/dimensiones del dataset es de memoria: si falla, imprime ds y corrige.
"""
import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats
import matplotlib.pyplot as plt

# Servidores y datasets a probar en orden de prioridad.
# NOAA OceanWatch (PIFSC) está activo, es público y responde de forma confiable.
# 'coastwatch.pfeg.noaa.gov' suele experimentar caídas o bloqueos que causan errores -68 (DAP failure) por timeout.
CANDIDATOS = [
    ("https://oceanwatch.pifsc.noaa.gov/erddap", "aqua_chla_monthly_2018_0"),  # MODIS-Aqua 4km mensual (2002-2022)
    ("https://oceanwatch.pifsc.noaa.gov/erddap", "esa-cci-chla-monthly-v6-0"), # ESA CCI Ocean Colour v6 (1997-presente, multi-sensor incl. MODIS)
    ("https://oceanwatch.pifsc.noaa.gov/erddap", "noaa_snpp_chla_monthly"),    # VIIRS 4km mensual (2012-presente)
    ("https://coastwatch.pfeg.noaa.gov/erddap", "erdMH1chlamday_R2022SQ"),     # NOAA PFEG (si está operativo)
    ("https://coastwatch.pfeg.noaa.gov/erddap", "erdMH1chlamday"),
]
VAR_CANDIDATAS = ["chlor_a", "chlorophyll", "chla"]

# (lat_min, lat_max, lon_min, lon_max)
SITIOS = {
    "sechura": (-6.0, -5.2, -81.2, -80.6),
    "samanco": (-9.5, -9.0, -78.8, -78.3),
    "paracas": (-14.1, -13.6, -76.5, -76.0),
}
INICIO, FIN = "2003-01-01", "2025-12-31"


def cargar(ds, var, caja):
    la0, la1, lo0, lo1 = caja
    da = ds[var].sel(time=slice(INICIO, FIN))

    # ERDDAP puede devolver latitud ascendente o descendente
    lat = da["latitude"].values
    lat_sl = slice(la0, la1) if lat[0] < lat[-1] else slice(la1, la0)

    # Longitudes: algunos datasets usan [-180, 180] y otros [0, 360]
    lon = da["longitude"].values
    if lon.min() >= 0 and lo0 < 0:
        lo0_sel, lo1_sel = lo0 + 360, lo1 + 360
    else:
        lo0_sel, lo1_sel = lo0, lo1
    lon_sl = slice(lo0_sel, lo1_sel) if lon[0] < lon[-1] else slice(lo1_sel, lo0_sel)

    da = da.sel(latitude=lat_sl, longitude=lon_sl)
    if "altitude" in da.dims:
        da = da.squeeze("altitude", drop=True)
    return da.load()


def mann_kendall_theilsen(serie):
    s = serie.dropna()
    if len(s) < 24:
        return None
    t = (s.index.year + (s.index.month - 0.5) / 12).values
    tau, p = stats.kendalltau(t, s.values)
    slope, intercept, lo, hi = stats.theilslopes(s.values, t)
    return dict(n=len(s), tau=tau, p=p, pendiente_por_anio=slope, ic_lo=lo, ic_hi=hi)


def revisar(nombre, caja, ds, var):
    da = cargar(ds, var, caja)
    ny, nx = da.sizes["latitude"], da.sizes["longitude"]
    print(f"\n=== {nombre} ===")
    print(f"Píxeles en la caja: {ny} x {nx} = {ny*nx} (paso ~{abs(float(da.latitude[1]-da.latitude[0])):.3f}°)")

    valido = da.notnull()
    pct_total = float(valido.mean()) * 100
    print(f"% píxeles-mes con dato: {pct_total:.1f}%")
    por_mes = valido.groupby("time.month").mean(dim=["time", "latitude", "longitude"]) * 100
    print("% con dato por mes calendario:",
          {int(m): round(float(v)) for m, v in zip(por_mes["month"].values, por_mes.values)})
    px_con_dato = int((valido.mean("time") > 0.5).sum())
    print(f"Píxeles con dato en >50% de los meses (agua usable): {px_con_dato}")

    serie = da.mean(dim=["latitude", "longitude"], skipna=True).to_series()
    serie.index = pd.to_datetime(serie.index)
    # ciclo estacional + anomalías (en log10, la clorofila es log-normal)
    logs = np.log10(serie.where(serie > 0))
    clim = logs.groupby(logs.index.month).transform("mean")
    anom = logs - clim
    res = mann_kendall_theilsen(anom)
    if res is None:
        print("Serie demasiado corta/vacía para tendencia.")
        return serie, anom
    print(f"Tendencia de anomalía log10(chl): {res['pendiente_por_anio']:+.4f}/año "
          f"[{res['ic_lo']:+.4f}, {res['ic_hi']:+.4f}], tau={res['tau']:+.2f}, p={res['p']:.3f}, n={res['n']}")
    print("Significativa (p<0.05)" if res["p"] < 0.05 else "NO significativa (p>=0.05)")
    return serie, anom


def abrir():
    errores = []
    for srv, ds_id in CANDIDATOS:
        url = f"{srv}/griddap/{ds_id}"
        print(f"Intentando abrir {url}...")
        try:
            ds = xr.open_dataset(url)
            var = next((v for v in VAR_CANDIDATAS if v in ds.data_vars), None)
            if var is None:
                raise ValueError(f"No se encontró variable de clorofila en {list(ds.data_vars)}")
            print(f"Abrió: {url}")
            print(f"Variable seleccionada: '{var}'")
            print("Dimensiones:", dict(ds.sizes))
            return ds, var
        except Exception as e:  # noqa: BLE001
            errores.append((url, str(e)[:120]))
    print("No abrió ninguno. Errores:")
    for u, e in errores:
        print(" -", u, "->", e)
    raise SystemExit("No se pudo conectar a ningún servidor ERDDAP disponible.")


if __name__ == "__main__":
    ds, var = abrir()
    fig, axes = plt.subplots(len(SITIOS), 1, figsize=(9, 3 * len(SITIOS)), sharex=True)
    for ax, (nombre, caja) in zip(np.atleast_1d(axes), SITIOS.items()):
        serie, anom = revisar(nombre, caja, ds, var)
        ax.plot(serie.index, serie.values, ".-", lw=0.6)
        ax.set_title(f"{nombre}: clorofila mensual (mg/m3)")
        ax.set_yscale("log")
    plt.tight_layout()
    plt.savefig("modisa_bahias.png", dpi=120)
    print("\nGuardado: modisa_bahias.png")

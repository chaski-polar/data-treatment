"""
Nutrientes (nitrato, fosfato), clorofila-a y temperatura del mar en una zona.
Fuente: Copernicus Marine (cuenta gratuita). SIN PROBAR: ajusta lo que haga falta.

Dependencias: pip install copernicusmarine xarray netCDF4 pandas matplotlib

Son productos de MODELO/REANALISIS (no mediciones directas). Etiquétalos así.
"""
import copernicusmarine as cm
import matplotlib.pyplot as plt
import pandas as pd

cm.login()  # pide usuario y contraseña de tu cuenta gratuita de Copernicus Marine

# (oeste, sur, este, norte). Elige una zona:
ZONAS = {
    "peru": (-85, -20, -70, -3),             # mar peruano (aproximado)
    "peninsula": (-70, -69, -55, -61),       # Península Antártica (aproximado)
}
ZONA = "peru"
W, S, E, N = ZONAS[ZONA]

# Periodo: los productos "my" (reanálisis) llevan unos meses de retraso.
# Si da error de fechas, retrocede el final del rango.
INICIO, FIN = "2020-01-01", "2022-12-31"

COMUN = dict(
    minimum_longitude=W, maximum_longitude=E,
    minimum_latitude=S, maximum_latitude=N,
    start_datetime=INICIO, end_datetime=FIN,
    minimum_depth=0, maximum_depth=2,   # solo capa superficial
)

# 1) Biogeoquímica mensual (reanálisis 0.25°): clorofila, nitrato, fosfato
bgc = cm.open_dataset(
    dataset_id="cmems_mod_glo_bgc_my_0.25deg_P1M-m",
    variables=["chl", "no3", "po4"],
    **COMUN,
)

# 2) Temperatura (reanálisis físico diario 0.25°, GREP) -> se promedia a mensual
# Este producto trae varios miembros del ensamble, así que "thetao" a secas
# no existe. Se abre sin filtrar variables y se detecta el nombre real.
# Media del ensamble: "cmems_mod_glo_phy-mnstd_my_0.25deg_P1D-m"
# Miembros por separado: "cmems_mod_glo_phy-all_my_0.25deg_P1D-m"
fis = cm.open_dataset(
    dataset_id="cmems_mod_glo_phy-mnstd_my_0.25deg_P1D-m",
    **COMUN,
)
print("Variables disponibles:", list(fis.data_vars))
VAR_T = next(v for v in fis.data_vars if v.startswith("thetao") and "std" not in v)
print("Usando como temperatura:", VAR_T)


def serie_mensual(da):
    """Promedio espacial de la capa superficial -> serie con índice mensual."""
    if "depth" in da.dims:
        da = da.isel(depth=0)
    s = da.mean(["latitude", "longitude"]).to_series()
    s.index = s.index.to_period("M")
    return s


temp_mensual = fis[VAR_T].resample(time="1MS").mean()

df = pd.DataFrame({
    "clorofila (mg/m3)": serie_mensual(bgc["chl"]),
    "nitrato (mmol/m3)": serie_mensual(bgc["no3"]),
    "fosfato (mmol/m3)": serie_mensual(bgc["po4"]),
    "temperatura (°C)": serie_mensual(temp_mensual),
}).dropna()

print(df.head())
print("\nCorrelaciones (solo exploratorias):")
print(df.corr().round(2))

df.index = df.index.to_timestamp()
df.plot(subplots=True, figsize=(10, 8), marker="o", title=f"Zona: {ZONA}")
plt.tight_layout()
plt.show()

# Para meses recientes (modelo operativo) los IDs que aparecen en el catálogo son:
#   nutrientes: cmems_mod_glo_bgc-nut_anfc_0.25deg_P1M-m
#   biología (clorofila): cmems_mod_glo_bgc-bio_anfc_0.25deg_P1M-m
# Revisa sus variables con print(cm.open_dataset(dataset_id=...)).

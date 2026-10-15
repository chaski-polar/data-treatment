"""
Ver clorofila-a (MODIS-Aqua L3m, NASA OBPG) frente a la costa de Perú.
SIN PROBAR: ajusta si algún nombre de variable o colección difiere.

Dependencias: pip install earthaccess xarray netCDF4 matplotlib
"""
from pathlib import Path

import earthaccess
import matplotlib.pyplot as plt
import xarray as xr
from matplotlib.colors import LogNorm

earthaccess.login(persist=True)

# (oeste, sur, este, norte): recuadro aproximado del mar peruano
BBOX = (-85, -20, -70, -3)
PERIODO = ("2025-01-01", "2025-12-31")

# La colección mezcla diario, 8 días, mensual, 4 km y 9 km.
# Para los meses más recientes prueba short_name="MODISA_L3m_CHL_NRT".
res = earthaccess.search_data(
    short_name="MODISA_L3m_CHL",
    temporal=PERIODO,
    bounding_box=BBOX,
)
mensual = [
    g for g in res
    if any("L3m.MO.CHL.chlor_a.4km" in link for link in g.data_links())
]
print(f"{len(res)} granules encontrados -> {len(mensual)} mensuales de 4 km")

# paths = earthaccess.download(mensual, "data_chl")

paths = Path("./data_chl").glob("*.nc")


# Recortar cada mes al recuadro
w, s, e, n = BBOX
series = {}
for p in sorted(paths, key=str):
    ds = xr.open_dataset(p)
    # nombre típico: AQUA_MODIS.20250101_20250131.L3m.MO.CHL.chlor_a.4km.nc
    mes = Path(str(p)).name.split(".")[1][:6]
    series[mes] = ds["chlor_a"].sortby("lat").sel(lat=slice(s, n), lon=slice(w, e))

print("Meses cargados:", list(series))

# Mapa del último mes + serie temporal (mediana: la clorofila es muy asimétrica)
ultimo = list(series)[-1]
fig, ax = plt.subplots(1, 2, figsize=(13, 5))

series[ultimo].plot(
    ax=ax[0], norm=LogNorm(vmin=0.05, vmax=20), cmap="viridis",
    cbar_kwargs={"label": "chlor_a (mg/m³)"},
)
ax[0].set_title(f"Clorofila-a, {ultimo}")

medianas = {m: float(v.median(skipna=True)) for m, v in series.items()}
ax[1].plot(list(medianas), list(medianas.values()), marker="o")
ax[1].set_title("Mediana de clorofila-a en el recuadro")
ax[1].set_ylabel("mg/m³")
ax[1].tick_params(axis="x", rotation=45)

plt.tight_layout()
plt.show()

# Si algo falla, inspecciona un archivo:
# print(xr.open_dataset(paths[0]))

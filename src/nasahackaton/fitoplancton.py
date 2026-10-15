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

BBOX = (-85, -20, -70, -3)
PERIODO = ("2025-01-01", "2025-12-31")

def search_monthly_granules():
    """Busca los granules MODIS mensuales de 4 km."""
    earthaccess.login(persist=True)
    results = earthaccess.search_data(
        short_name="MODISA_L3m_CHL",
        temporal=PERIODO,
        bounding_box=BBOX,
    )
    return [
        granule for granule in results
        if any("L3m.MO.CHL.chlor_a.4km" in link for link in granule.data_links())
    ]


def load_monthly_series(data_dir: str = "data_chl"):
    """Carga y recorta los NetCDF mensuales descargados."""
    west, south, east, north = BBOX
    series = {}
    for path in sorted(Path(data_dir).glob("*.nc"), key=str):
        with xr.open_dataset(path) as dataset:
            month = path.name.split(".")[1][:6]
            series[month] = dataset["chlor_a"].sortby("lat").sel(
                lat=slice(south, north),
                lon=slice(west, east),
            ).load()
    return series


def plot_series(series) -> None:
    """Grafica el mapa del último mes y la mediana temporal."""
    if not series:
        raise ValueError("No se encontraron archivos NetCDF en data_chl.")
    latest = next(reversed(series))
    figure, axes = plt.subplots(1, 2, figsize=(13, 5))
    series[latest].plot(
        ax=axes[0], norm=LogNorm(vmin=0.05, vmax=20), cmap="viridis",
        cbar_kwargs={"label": "chlor_a (mg/m³)"},
    )
    axes[0].set_title(f"Clorofila-a, {latest}")
    medians = {month: float(value.median(skipna=True)) for month, value in series.items()}
    axes[1].plot(list(medians), list(medians.values()), marker="o")
    axes[1].set_title("Mediana de clorofila-a")
    axes[1].set_ylabel("mg/m³")
    axes[1].tick_params(axis="x", rotation=45)
    plt.tight_layout()
    plt.show()


def main() -> None:
    monthly = search_monthly_granules()
    print(f"Granules encontrados: {len(monthly)} mensuales de 4 km")
    plot_series(load_monthly_series())


if __name__ == "__main__":
    main()

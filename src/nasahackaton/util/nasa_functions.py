import requests
import pandas as pd
import earthaccess
import rasterio
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm


def power(lat, lon, start, end, params="RH2M,PRECTOTCORR,T2M,WS2M"):
    """Fetch climate data from NASA POWER API."""
    r = requests.get(
        "https://power.larc.nasa.gov/api/temporal/daily/point",
        params=dict(parameters=params, community="AG",
                    latitude=lat, longitude=lon,
                    start=start, end=end, format="JSON"),
    ).json()
    d = r["properties"]["parameter"]
    return pd.DataFrame(d).astype(float)


def download_earthaccess_data(bbox, temporal, output_dir="./data"):
    """Download satellite data from EarthAccess."""
    earthaccess.login(persist=True)
    results = earthaccess.search_data(
        short_name="OPERA_L3_DSWX-S1_V1",
        bounding_box=bbox,
        temporal=temporal,
    )
    earthaccess.download(results[:3], output_dir)


def _extract_water_files(files):
    """Extract water layer files from list."""
    return [f for f in files if "WTR" in f.name]


def _plot_raster_data(arr, title, figsize=(7, 7)):
    """Plot raster data with custom colormap."""
    nodata = 255
    m = np.ma.masked_equal(arr, nodata)
    cmap = ListedColormap(["#e8e4d8", "#1f78b4", "#7fbfe8"])
    norm = BoundaryNorm([-0.5, 0.5, 1.5, 2.5], cmap.N)
    cmap.set_bad("white")
    
    plt.figure(figsize=figsize)
    plt.imshow(m, cmap=cmap, norm=norm, interpolation="nearest")
    plt.title(title, fontsize=8)
    plt.show()


def _analyze_water_coverage(files):
    """Analyze water coverage statistics for each file."""
    stats = []
    for f in files:
        with rasterio.open(f) as src:
            a = src.read(1, out_shape=(src.height // 8, src.width // 8))
        valid = (a != 255).mean() * 100
        agua = np.isin(a, [1, 2]).mean() * 100
        stats.append((f.name[:45], valid, agua))
        print(f"{f.name[:45]:45s} valido={valid:.0f}% agua={agua:.2f}%")
    return stats


def open_with_rasterio(files):
    """Process and visualize raster files."""
    wtr = _extract_water_files(files)
    print(f"Found {len(wtr)} water layer files")
    
    if not wtr:
        return
    
    # Read first file
    with rasterio.open(wtr[0]) as src:
        print(f"CRS: {src.crs}, Resolution: {src.res}, Shape: {src.shape}")
        print(f"Bounds: {src.bounds}")
        print(f"Metadata: {src.tags()}")
        
        arr = src.read(1, out_shape=(src.height // 10, src.width // 10))
    
    # Peek at data distribution
    vals, counts = np.unique(arr, return_counts=True)
    print("\nData distribution:")
    for v, c in zip(vals, counts):
        print(f"  Value {v}: {c} pixels ({100*c/arr.size:.1f}%)")
    
    # Display simple plot
    plt.imshow(arr, interpolation="nearest")
    plt.colorbar()
    plt.title(wtr[0].name[:60])
    plt.show()
    
    # Display colorful plot
    _plot_raster_data(arr, wtr[0].name[:60])
    
    # Analyze coverage
    _analyze_water_coverage(wtr)


if __name__ == "__main__":
    files = sorted(Path("./data").glob("*.tif"))
    print(f"Total files: {len(files)}\n")
    open_with_rasterio(files)

"""Análisis básico de capas raster OPERA DSWx-S1."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import rasterio
from matplotlib.colors import BoundaryNorm, ListedColormap


def water_files(files: Iterable[Path]) -> list[Path]:
    """Selecciona archivos que contienen la capa de agua."""
    return [path for path in files if "WTR" in path.name]


def water_coverage(files: Iterable[Path]) -> list[tuple[str, float, float]]:
    """Calcula cobertura válida y porcentaje de agua por archivo."""
    stats = []
    for path in files:
        with rasterio.open(path) as source:
            array = source.read(
                1,
                out_shape=(max(1, source.height // 8), max(1, source.width // 8)),
            )
        valid = float((array != 255).mean() * 100)
        water = float(np.isin(array, [1, 2]).mean() * 100)
        stats.append((path.name, valid, water))
    return stats


def plot_water_layer(array: np.ndarray, title: str, figsize: tuple[int, int] = (7, 7)) -> None:
    """Muestra una capa de agua con una paleta legible."""
    masked = np.ma.masked_equal(array, 255)
    cmap = ListedColormap(["#e8e4d8", "#1f78b4", "#7fbfe8"])
    cmap.set_bad("white")
    norm = BoundaryNorm([-0.5, 0.5, 1.5, 2.5], cmap.N)
    _, axis = plt.subplots(figsize=figsize)
    axis.imshow(masked, cmap=cmap, norm=norm, interpolation="nearest")
    axis.set_title(title, fontsize=8)
    plt.show()


def inspect_water_files(files: Iterable[Path]) -> list[tuple[str, float, float]]:
    """Inspecciona la primera capa y devuelve estadísticas de todas las capas."""
    layers = water_files(files)
    if not layers:
        print("No se encontraron capas WTR.")
        return []

    with rasterio.open(layers[0]) as source:
        print(f"CRS: {source.crs}, resolución: {source.res}, forma: {source.shape}")
        print(f"Bounds: {source.bounds}")
        array = source.read(
            1,
            out_shape=(max(1, source.height // 10), max(1, source.width // 10)),
        )

    values, counts = np.unique(array, return_counts=True)
    print("Distribución de datos:")
    for value, count in zip(values, counts):
        print(f"  Valor {value}: {count} píxeles ({100 * count / array.size:.1f}%)")

    plot_water_layer(array, layers[0].name[:60])
    return water_coverage(layers)

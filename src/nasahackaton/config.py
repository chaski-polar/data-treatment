"""Configuración compartida para los experimentos del desafío."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# Raíz del repo (…/data_treatment), dos niveles por encima de este paquete.
PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class BoundingBox:
    """Caja geográfica en el orden oeste, sur, este, norte."""

    west: float
    south: float
    east: float
    north: float

    def as_tuple(self) -> tuple[float, float, float, float]:
        return self.west, self.south, self.east, self.north


NISAR_ZONES = {
    "tumbes_piura": BoundingBox(-81.0, -5.5, -80.0, -3.3),
    "titicaca": BoundingBox(-70.5, -17.0, -68.5, -15.0),
    "ucayali": BoundingBox(-75.0, -9.0, -73.5, -7.0),
}

# Costa peruana ~Castillo et al. 2018 (3°23′S–18°21′S), caja usada en Exp. B.
PERU_OCEAN = BoundingBox(west=-85.0, south=-18.35, east=-70.0, north=-3.38)

POWER_LOCATIONS = {
    "tumbes": (-3.57, -80.45),
    "piura": (-5.19, -80.63),
    "puno": (-15.84, -70.02),
    "pucallpa": (-8.38, -74.55),
}

import requests, pandas as pd
import earthaccess
import rasterio
import matplotlib.pyplot as plt

import re
import collections
from pathlib import Path
import numpy as np

from matplotlib.colors import ListedColormap, BoundaryNorm

from nasahackaton.util.nasa_functions import power


earthaccess.login(persist=True)

# for d in earthaccess.search_datasets(keyword="NISAR", count=20):
#     print(d.get_umm("ShortName"), "|", d.get_umm("EntryTitle"))

zonas = {
    "tumbes_piura": (-81.0, -5.5, -80.0, -3.3),
    "titicaca":     (-70.5, -17.0, -68.5, -15.0),
    "ucayali":      (-75.0, -9.0, -73.5, -7.0),
}
# for nombre, bbox in zonas.items():
#     r = earthaccess.search_data(short_name="NISAR_L2_GCOV_PROVISIONAL_V1",
#                                 bounding_box=bbox,
#                                 temporal=("2026-06-17", "2026-10-10"))
#     print(nombre, len(r))



def resumen(r):
    fechas = collections.Counter()
    for g in r:
        n = g["meta"]["native-id"]
        m = re.search(r"(\d{8})T\d{6}", n)
        fechas[m.group(1) if m else "?"] += 1
    return fechas

for nombre, bbox in zonas.items():
    r = earthaccess.search_data(
        short_name="NISAR_L2_GCOV_PROVISIONAL_V1",
        bounding_box=bbox,
        temporal=("2026-06-17", "2026-10-11"),
    )
    f = resumen(r)
    print(nombre, len(r), "granules |", len(f), "fechas distintas")
    print(r[0]["meta"]["native-id"])      # mira el formato del nombre
    print(r[0].size, "MB")              # tamaño de un granule


for nombre, bbox in zonas.items():
    b = earthaccess.search_data(short_name="NISAR_L2_GCOV_BETA_V1",
                                bounding_box=bbox,
                                temporal=("2025-10-01", "2026-02-28"))
    s = earthaccess.search_data(short_name="NISAR_L3_SME2_PROVISIONAL_V1",
                                bounding_box=bbox,
                                temporal=("2026-06-17", "2026-10-11"))
    print(nombre, "beta:", len(b), "| humedad suelo:", len(s))


# import h5py
# def tree(name, obj):
#     print(name, getattr(obj, "shape", ""))
# with h5py.File("ruta/al/archivo.h5") as f:
#     f.visititems(tree)


for nombre, (lat, lon) in {"tumbes": (-3.57, -80.45),
                           "piura": (-5.19, -80.63),
                           "puno": (-15.84, -70.02),
                           "pucallpa": (-8.38, -74.55)}.items():
    d = power(lat, lon, "20260617", "20261008", params="PRECTOTCORR")
    d = d[d["PRECTOTCORR"] > -900]
    print(nombre, "días con >1 mm:", (d["PRECTOTCORR"] > 1).sum(),
          "| total mm:", round(d["PRECTOTCORR"].sum(), 1))


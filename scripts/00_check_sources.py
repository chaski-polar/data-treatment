"""Comprueba dependencias y credenciales sin descargar grandes archivos."""

from __future__ import annotations

import importlib.util


def main() -> None:
    for name in ("copernicusmarine", "earthaccess", "xarray", "pandas", "pyarrow"):
        status = "OK" if importlib.util.find_spec(name) else "FALTA"
        print(f"{name}: {status}")
    print("Copernicus: ejecutar `copernicusmarine login` una sola vez antes de descargar.")
    print("NASA Ocean Color: requiere configuración de Earthdata para búsquedas autenticadas.")


if __name__ == "__main__":
    main()


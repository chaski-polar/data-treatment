"""Herramientas del proyecto NASA Space Apps.

La importación de ``main`` es perezosa para que los scripts de preparación
puedan importar un submódulo sin cargar Earthaccess, Rasterio y Copernicus a
la vez.
"""


def main() -> None:
    """Punto de entrada legado del proyecto."""
    from nasahackaton.main import main as run

    run()


__all__ = ["main"]

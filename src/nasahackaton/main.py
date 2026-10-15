import collections
import re

from nasahackaton.config import NISAR_ZONES, POWER_LOCATIONS
from nasahackaton.sources.earthdata import search_nisar
from nasahackaton.sources.power import fetch_daily


def summarize_granules(results):
    """Cuenta granules por fecha de adquisición."""
    fechas = collections.Counter()
    for granule in results:
        native_id = granule["meta"]["native-id"]
        m = re.search(r"(\d{8})T\d{6}", native_id)
        fechas[m.group(1) if m else "?"] += 1
    return fechas


def report_nisar() -> None:
    """Consulta la cobertura NISAR de las zonas configuradas."""
    for name, zone in NISAR_ZONES.items():
        results = search_nisar(
            zone.as_tuple(),
            temporal=("2026-06-17", "2026-10-11"),
        )
        dates = summarize_granules(results)
        print(f"{name}: {len(results)} granules | {len(dates)} fechas distintas")


def report_rainfall() -> None:
    """Resume lluvia NASA POWER en las ciudades de interés."""
    for name, (latitude, longitude) in POWER_LOCATIONS.items():
        data = fetch_daily(
            latitude,
            longitude,
            "20260617",
            "20261008",
            parameters="PRECTOTCORR",
        )
        data = data[data["PRECTOTCORR"] > -900]
        print(
            f"{name}: días con >1 mm: {(data['PRECTOTCORR'] > 1).sum()} "
            f"| total mm: {data['PRECTOTCORR'].sum():.1f}"
        )


def main() -> None:
    report_nisar()
    report_rainfall()


if __name__ == "__main__":
    main()

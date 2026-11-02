"""Descarga secuencial de fuentes externas para el panel peruano.

Ejemplos:

    python scripts/01_download_data.py --dry-run
    python scripts/01_download_data.py --source noaa nsidc
    python scripts/01_download_data.py --source copernicus --start 1998-01-01 --end 2024-12-31

Copernicus usa ``subset`` porque permite recortar variables, espacio, tiempo y
profundidad. NOAA y NSIDC usan descargas HTTPS/ERDDAP y no requieren cuenta.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from nasahackaton.config import PERU_OCEAN, PROJECT_ROOT
from nasahackaton.sources.noaa import WOA_VARS, fetch_pdo, woa23_monthly_path

COPERNICUS_PHYSICS = "cmems_mod_glo_phy_my_0.083deg_P1M-m"
COPERNICUS_BGC = "cmems_mod_glo_bgc_my_0.25deg_P1M-m"
NSIDC_SOUTH_DAILY = (
    "https://noaadata.apps.nsidc.org/NOAA/G02135/south/daily/data/"
    "S_seaice_extent_daily_v4.0.csv"
)


def download_url(url: str, target: Path, *, dry_run: bool = False, force: bool = False) -> Path:
    """Descarga una URL a un archivo temporal y luego la publica atómicamente."""
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.stat().st_size > 0 and not force:
        print(f"SKIP existente: {target}")
        return target
    print(f"GET {url}\n -> {target}")
    if dry_run:
        return target
    temporary = target.with_suffix(target.suffix + ".part")
    with requests.get(url, stream=True, timeout=120) as response:
        response.raise_for_status()
        with temporary.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)
    temporary.replace(target)
    return target


def download_noaa(args: argparse.Namespace, manifest: list[dict[str, Any]]) -> None:
    """Descarga PDO y climatologías mensuales WOA23."""
    pdo_path = PROJECT_ROOT / "data" / "raw" / "noaa" / f"pdo_monthly_{args.start[:4]}_{args.end[:4]}.csv"
    if not (pdo_path.exists() and pdo_path.stat().st_size > 0 and not args.force):
        if args.dry_run:
            print(f"PLAN PDO PSL: {args.start} a {args.end} -> {pdo_path}")
        else:
            pdo = fetch_pdo(start=args.start, end=args.end, source="psl")
            pdo_path.parent.mkdir(parents=True, exist_ok=True)
            pdo.to_csv(pdo_path, header=True, index_label="date")
            print(f"OK PDO: {len(pdo)} filas -> {pdo_path}")
    else:
        print(f"SKIP existente: {pdo_path}")
    manifest.append({"source": "NOAA PSL PDO", "path": str(pdo_path), "start": args.start, "end": args.end})

    for month in range(1, 13):
        for variable in ("nitrate", "phosphate", "silicate"):
            if args.dry_run:
                code = WOA_VARS[variable][1]
                target = PROJECT_ROOT / "data" / "raw" / "woa23" / f"woa23_all_{code}{month:02d}_01.nc"
                print(f"PLAN WOA23: {variable} mes {month:02d} -> {target}")
            else:
                target = woa23_monthly_path(variable, month, PROJECT_ROOT / "data" / "raw" / "woa23")
                print(f"OK WOA23: {target}")
            manifest.append({"source": "NOAA WOA23", "variable": variable, "month": month, "path": str(target)})


def download_nsidc(args: argparse.Namespace, manifest: list[dict[str, Any]]) -> None:
    target = PROJECT_ROOT / "data" / "raw" / "nsidc" / "S_seaice_extent_daily_v4.0.csv"
    download_url(NSIDC_SOUTH_DAILY, target, dry_run=args.dry_run, force=args.force)
    manifest.append({"source": "NSIDC G02135", "url": NSIDC_SOUTH_DAILY, "path": str(target)})


def download_copernicus(args: argparse.Namespace, manifest: list[dict[str, Any]]) -> None:
    """Descarga física y biogeoquímica en dos NetCDF separados."""
    if args.dry_run:
        print("PLAN Copernicus: requiere credenciales configuradas con copernicusmarine.login()")
        return
    import copernicusmarine

    output = PROJECT_ROOT / "data" / "raw" / "copernicus"
    common = {
        "start_datetime": args.start,
        "end_datetime": args.end,
        "minimum_longitude": PERU_OCEAN.west,
        "maximum_longitude": PERU_OCEAN.east,
        "minimum_latitude": PERU_OCEAN.south,
        "maximum_latitude": PERU_OCEAN.north,
        "minimum_depth": 0,
        "maximum_depth": 5,
        "output_directory": str(output),
        "disable_progress_bar": False,
    }
    requests_to_make = [
        (COPERNICUS_PHYSICS, ["thetao", "so"], f"physics_{args.start}_{args.end}.nc"),
        (COPERNICUS_BGC, ["chl", "no3", "po4", "o2", "phyc"], f"biogeochemistry_{args.start}_{args.end}.nc"),
    ]
    for dataset_id, variables, filename in requests_to_make:
        target = output / filename
        if target.exists() and target.stat().st_size > 0 and not args.force:
            print(f"SKIP existente: {target}")
            continue
        result = copernicusmarine.subset(
            dataset_id=dataset_id,
            variables=variables,
            output_filename=filename,
            **common,
        )
        path = getattr(result, "file_path", target)
        print(f"OK Copernicus {dataset_id}: {path}")
        manifest.append({"source": dataset_id, "variables": variables, "path": str(path)})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", nargs="+", choices=("copernicus", "noaa", "nsidc"), default=["copernicus", "noaa", "nsidc"])
    parser.add_argument("--start", default="1998-01-01")
    parser.add_argument("--end", default="2024-12-31")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="vuelve a descargar archivos existentes")
    args = parser.parse_args()
    manifest: list[dict[str, Any]] = []
    for source in args.source:
        if source == "copernicus":
            download_copernicus(args, manifest)
        elif source == "noaa":
            download_noaa(args, manifest)
        elif source == "nsidc":
            download_nsidc(args, manifest)
    manifest_path = PROJECT_ROOT / "data" / "raw" / "download_manifest.json"
    if not args.dry_run:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(
                {"created_at": datetime.now(timezone.utc).isoformat(), "requests": manifest},
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        print(f"Manifiesto: {manifest_path}")


if __name__ == "__main__":
    main()


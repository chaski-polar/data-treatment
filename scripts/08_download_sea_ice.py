"""Descarga concentración espacial de hielo antártico desde NSIDC/Earthdata."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import earthaccess
import requests


NSIDC_MONTHLY_INDEX = "https://noaadata.apps.nsidc.org/NOAA/G02202_V6/south/monthly/"
MONTHLY_PATTERN = re.compile(r"href=[\"'](?P<name>sic_pss25_(?P<ym>\d{6})_[^\"']+\.nc)[\"']")


def _download_monthly_https(start: str, end: str, output: Path) -> list[str]:
    """Fallback público de NOAA@NSIDC cuando CMR no devuelve granules.

    G02202 V6 publica los NetCDF mensuales del hemisferio sur en un índice
    HTTPS oficial. Se descargan solo los meses solicitados y se conservan los
    archivos ya existentes para permitir reanudar una descarga interrumpida.
    """
    response = requests.get(NSIDC_MONTHLY_INDEX, timeout=120)
    response.raise_for_status()
    start_ym = start[:7].replace("-", "")
    end_ym = end[:7].replace("-", "")
    names = sorted(
        match.group("name")
        for match in MONTHLY_PATTERN.finditer(response.text)
        if start_ym <= match.group("ym") <= end_ym
    )
    downloaded: list[str] = []
    output.mkdir(parents=True, exist_ok=True)
    for name in names:
        target = output / name
        if target.exists() and target.stat().st_size > 0:
            downloaded.append(str(target))
            continue
        temporary = target.with_suffix(target.suffix + ".part")
        with requests.get(urljoin(NSIDC_MONTHLY_INDEX, name), stream=True, timeout=120) as item:
            item.raise_for_status()
            with temporary.open("wb") as handle:
                for chunk in item.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        handle.write(chunk)
        temporary.replace(target)
        downloaded.append(str(target))
    return downloaded


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default="1998-01-01")
    parser.add_argument("--end", default="2025-12-31")
    parser.add_argument("--short-name", default="G02202")
    parser.add_argument("--version", default="6", help="versión de G02202 en CMR")
    parser.add_argument("--output", type=Path, default=Path("data/raw/nsidc/g02202"))
    parser.add_argument("--limit", type=int, default=0, help="0 = todos los granules encontrados")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    granules = []
    selected = []
    if not args.dry_run:
        earthaccess.login(persist=True)
        granules = earthaccess.search_data(
            short_name=args.short_name,
            version=args.version,
            temporal=(args.start, args.end),
            bounding_box=(-180.0, -90.0, 180.0, -30.0),
            count=-1,
        )
        selected = granules if args.limit == 0 else granules[:args.limit]
    record = {
        "source": "NSIDC/Earthdata",
        "dataset_id": args.short_name,
        "start": args.start,
        "end": args.end,
        "granules_found": None if args.dry_run else len(granules),
        "granules_selected": None if args.dry_run else len(selected),
        "spatial_filter": [-180.0, -90.0, 180.0, -30.0],
        "output": str(args.output),
        "status": "planned" if args.dry_run else "searched",
    }
    if not args.dry_run:
        args.output.mkdir(parents=True, exist_ok=True)
        if selected:
            paths = earthaccess.download(selected, str(args.output))
            record["downloaded_files"] = len(paths)
            record["method"] = "earthaccess"
            record["status"] = "downloaded"
        else:
            paths = _download_monthly_https(args.start, args.end, args.output)
            record["downloaded_files"] = len(paths)
            record["method"] = "NOAA@NSIDC HTTPS monthly fallback"
            record["status"] = "downloaded_https_fallback" if paths else "no_granules"
            print(
                "ADVERTENCIA: CMR no devolvió granules para G02202; "
                f"se usó el índice HTTPS oficial y se encontraron {len(paths)} meses."
            )
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = args.output / "sea_ice_download_manifest.json"
    manifest.write_text(
        json.dumps({"created_at": datetime.now(timezone.utc).isoformat(), "request": record}, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(record, ensure_ascii=False))
    print(f"Manifest: {manifest}")


if __name__ == "__main__":
    main()

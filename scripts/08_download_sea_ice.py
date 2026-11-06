"""Descarga concentración espacial de hielo antártico desde NSIDC/Earthdata."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import earthaccess


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default="1998-01-01")
    parser.add_argument("--end", default="2025-12-31")
    parser.add_argument("--short-name", default="G02202")
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
            temporal=(args.start, args.end),
            bounding_box=(-180.0, -90.0, 180.0, -30.0),
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
        paths = earthaccess.download(selected, str(args.output))
        record["downloaded_files"] = len(paths)
        record["status"] = "downloaded"
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

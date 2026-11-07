"""Descarga corrientes superficiales OSCAR desde NASA PO.DAAC/Earthdata."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import earthaccess

from nasahackaton.config import CONNECTIVITY_REGIONS


DATASET_ID = "OSCAR_L4_OC_FINAL_V2.0"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--regions", nargs="+", choices=sorted(CONNECTIVITY_REGIONS), default=sorted(CONNECTIVITY_REGIONS))
    parser.add_argument("--start", default="1998-01-01")
    parser.add_argument("--end", default="2025-12-31")
    parser.add_argument("--output", type=Path, default=Path("data/raw/oscar"))
    parser.add_argument("--limit", type=int, default=0, help="0 = todos los granules encontrados")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.dry_run:
        earthaccess.login(persist=True)
    records = []
    for region in args.regions:
        box = CONNECTIVITY_REGIONS[region]
        granules = []
        selected = []
        if not args.dry_run:
            granules = earthaccess.search_data(
                short_name=DATASET_ID,
                temporal=(args.start, args.end),
                bounding_box=box.as_tuple(),
            )
            selected = granules if args.limit == 0 else granules[:args.limit]
        record = {
            "source": "NASA PO.DAAC/Earthdata",
            "dataset_id": DATASET_ID,
            "region": region,
            "bounding_box": box.__dict__,
            "start": args.start,
            "end": args.end,
            "granules_found": None if args.dry_run else len(granules),
            "granules_selected": None if args.dry_run else len(selected),
            "status": "planned" if args.dry_run else "searched",
        }
        if not args.dry_run:
            target = args.output / region
            target.mkdir(parents=True, exist_ok=True)
            if selected:
                paths = earthaccess.download(selected, str(target))
                record["downloaded_files"] = len(paths)
                record["status"] = "downloaded"
            else:
                record["downloaded_files"] = 0
                record["status"] = "no_granules"
                print(f"ADVERTENCIA: OSCAR no devolvió granules para {region}; se continúa.")
        records.append(record)
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = args.output / "oscar_download_manifest.json"
    manifest.write_text(
        json.dumps({"created_at": datetime.now(timezone.utc).isoformat(), "records": records}, indent=2),
        encoding="utf-8",
    )
    for record in records:
        print(record["status"], record["region"], record["granules_found"])
    print(f"Manifest: {manifest}")


if __name__ == "__main__":
    main()

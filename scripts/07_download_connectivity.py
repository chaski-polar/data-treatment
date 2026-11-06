"""Descarga campos CMEMS para la conectividad Antártida–Pacífico–Humboldt.

Este pipeline es independiente del descargador peruano existente. Genera
subconjuntos mensuales por región y conserva los campos verticales necesarios
para una primera evaluación exploratoria de masas de agua y circulación.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from nasahackaton.config import CONNECTIVITY_REGIONS
from nasahackaton.sources.copernicus import subset_connectivity_region


PHYSICS = "cmems_mod_glo_phy_my_0.083deg_P1M-m"
BGC = "cmems_mod_glo_bgc_my_0.25deg_P1M-m"
PHYSICS_3D = ("thetao", "so", "uo", "vo")
PHYSICS_2D = ("zos", "mlotst")
BGC_VARS = ("chl", "no3", "po4", "o2", "phyc")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _request(
    *,
    region: str,
    dataset_id: str,
    variables: tuple[str, ...],
    start: str,
    end: str,
    output: Path,
    maximum_depth: float | None,
    force: bool,
    dry_run: bool,
) -> dict[str, object]:
    box = CONNECTIVITY_REGIONS[region]
    record: dict[str, object] = {
        "source": "Copernicus Marine",
        "dataset_id": dataset_id,
        "variables": list(variables),
        "region": region,
        "bounding_box": box.__dict__,
        "start": start,
        "end": end,
        "minimum_depth": 0 if maximum_depth is not None else None,
        "maximum_depth": maximum_depth,
        "path": str(output),
    }
    if output.exists() and output.stat().st_size > 0 and not force:
        record.update({"status": "existing", "sha256": _sha256(output)})
        return record
    if dry_run:
        record["status"] = "planned"
        return record
    try:
        subset_connectivity_region(
            dataset_id=dataset_id,
            variables=variables,
            start=start,
            end=end,
            box=box,
            output_path=output,
            minimum_depth=0 if maximum_depth is not None else None,
            maximum_depth=maximum_depth,
        )
        record.update({"status": "downloaded", "sha256": _sha256(output)})
    except Exception as exc:  # keep all failures in the manifest
        record.update({"status": "error", "error": f"{type(exc).__name__}: {exc}"})
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--regions", nargs="+", choices=sorted(CONNECTIVITY_REGIONS), default=sorted(CONNECTIVITY_REGIONS))
    parser.add_argument("--start", default="1998-01-01")
    parser.add_argument("--end", default="2025-12-01")
    parser.add_argument("--physics-max-depth", type=float, default=1000.0)
    parser.add_argument("--bgc-max-depth", type=float, default=500.0)
    parser.add_argument("--output", type=Path, default=Path("data/raw/connectivity"))
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    records: list[dict[str, object]] = []
    for region in args.regions:
        region_dir = args.output / region
        records.append(_request(
            region=region, dataset_id=PHYSICS, variables=PHYSICS_3D,
            start=args.start, end=args.end,
            output=region_dir / "physics_3d_monthly.nc",
            maximum_depth=args.physics_max_depth, force=args.force, dry_run=args.dry_run,
        ))
        records.append(_request(
            region=region, dataset_id=PHYSICS, variables=PHYSICS_2D,
            start=args.start, end=args.end,
            output=region_dir / "physics_surface_monthly.nc",
            maximum_depth=None, force=args.force, dry_run=args.dry_run,
        ))
        records.append(_request(
            region=region, dataset_id=BGC, variables=BGC_VARS,
            start=args.start, end=args.end,
            output=region_dir / "biogeochemistry_monthly.nc",
            maximum_depth=args.bgc_max_depth, force=args.force, dry_run=args.dry_run,
        ))

    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "pipeline": "connectivity_cmems_v1",
        "records": records,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    manifest_path = args.output / "connectivity_download_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    for record in records:
        print(record["status"], record["region"], record["dataset_id"], record["variables"])
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()

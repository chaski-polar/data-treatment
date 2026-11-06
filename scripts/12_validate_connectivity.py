"""Valida cobertura espacial, temporal y vertical de los NetCDF de conectividad."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import xarray as xr

from nasahackaton.config import CONNECTIVITY_REGIONS


EXPECTED = {
    "physics_3d_monthly.nc": {"variables": {"thetao", "so", "uo", "vo"}, "depth": True},
    "physics_surface_monthly.nc": {"variables": {"zos", "mlotst"}, "depth": False},
    "biogeochemistry_monthly.nc": {"variables": {"chl", "no3", "po4", "o2", "phyc"}, "depth": True},
}


def _coord_bounds(ds: xr.Dataset, name: str) -> tuple[float | str | None, float | str | None]:
    if name not in ds.coords:
        return None, None
    values = ds[name].values
    if name in {"time", "valid_time"}:
        values = pd.to_datetime(values)
        return str(values.min()), str(values.max())
    return float(values.min()), float(values.max())


def validate_file(
    path: Path,
    region: str,
    expected: dict[str, object],
    *,
    legacy_fallback: bool = False,
) -> dict[str, object]:
    record: dict[str, object] = {
        "region": region,
        "path": str(path),
        "exists": path.exists(),
        "status": "missing",
        "legacy_fallback": legacy_fallback,
    }
    if not path.exists():
        return record
    try:
        with xr.open_dataset(path) as ds:
            variables = set(ds.data_vars)
            missing = sorted(set(expected["variables"]) - variables)
            depth_min, depth_max = _coord_bounds(ds, "depth")
            time_min, time_max = _coord_bounds(ds, "time")
            if time_min is None:
                time_min, time_max = _coord_bounds(ds, "valid_time")
            record.update({
                "status": (
                    "ok"
                    if not missing
                    else "partial_legacy"
                    if legacy_fallback
                    else "invalid"
                ),
                "dimensions": {key: int(value) for key, value in ds.sizes.items()},
                "variables": sorted(variables),
                "missing_variables": missing,
                "time_min": time_min,
                "time_max": time_max,
                "depth_min": depth_min,
                "depth_max": depth_max,
                "latitude_min": _coord_bounds(ds, "latitude")[0],
                "latitude_max": _coord_bounds(ds, "latitude")[1],
                "longitude_min": _coord_bounds(ds, "longitude")[0],
                "longitude_max": _coord_bounds(ds, "longitude")[1],
                "expected_depth": bool(expected["depth"]),
            })
    except Exception as exc:
        record.update({"status": "error", "error": f"{type(exc).__name__}: {exc}"})
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/raw/connectivity"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/tables/connectivity_quality_report.json"))
    parser.add_argument("--legacy-peru-input", type=Path, default=Path("data/raw/copernicus"))
    args = parser.parse_args()

    records: list[dict[str, object]] = []
    for region in CONNECTIVITY_REGIONS:
        for filename, expected in EXPECTED.items():
            path = args.input / region / filename
            if not path.exists() and region == "peru_humboldt":
                legacy_names = {
                    "physics_3d_monthly.nc": "physics_b.nc",
                    "physics_surface_monthly.nc": "ssh_b.nc",
                    "biogeochemistry_monthly.nc": "biogeochemistry_b.nc",
                }
                path = args.legacy_peru_input / legacy_names[filename]
            records.append(validate_file(
                path,
                region,
                expected,
                legacy_fallback=region == "peru_humboldt" and path.parent == args.legacy_peru_input,
            ))

    summary = {
        "n_files": len(records),
        "n_ok": sum(record["status"] == "ok" for record in records),
        "n_missing": sum(record["status"] == "missing" for record in records),
        "n_invalid": sum(record["status"] in {"invalid", "error"} for record in records),
        "n_partial_legacy": sum(record["status"] == "partial_legacy" for record in records),
    }
    payload = {"summary": summary, "files": records}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    print(f"Reporte: {args.output}")


if __name__ == "__main__":
    main()

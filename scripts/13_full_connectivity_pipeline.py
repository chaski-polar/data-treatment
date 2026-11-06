"""Orquestador completo de descarga, procesamiento e inventario.

Este archivo está pensado para ejecutarse desde Google Colab o desde el repo
local. No reemplaza los scripts individuales: los coordina, conserva sus
manifiestos y genera un informe final para decidir qué datos se deben subir,
descargar o excluir.

Ejemplos:

    python scripts/13_full_connectivity_pipeline.py --mode inventory
    python scripts/13_full_connectivity_pipeline.py --mode all
    python scripts/13_full_connectivity_pipeline.py --mode process --skip-ice --skip-oscar
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from nasahackaton.config import CONNECTIVITY_REGIONS  # noqa: E402


CMEMS_FILES = ("physics_3d_monthly.nc", "physics_surface_monthly.nc", "biogeochemistry_monthly.nc")
EXPECTED_CMEMS = [
    (region, ROOT / "data/raw/connectivity" / region / filename)
    for region in CONNECTIVITY_REGIONS
    for filename in CMEMS_FILES
]


def _bytes(path: Path) -> int:
    return path.stat().st_size if path.is_file() else 0


def _human(size: int) -> str:
    value = float(size)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if value < 1024 or unit == "TiB":
            return f"{value:.2f} {unit}"
        value /= 1024
    return f"{size} B"


def _status(path: Path) -> str:
    if path.is_file() and path.stat().st_size > 0:
        return "downloaded"
    if path.exists():
        return "temporary_or_empty"
    return "missing"


def _inventory() -> dict[str, object]:
    required: list[dict[str, object]] = []
    for region, path in EXPECTED_CMEMS:
        size = _bytes(path)
        required.append({
            "category": "CMEMS connectivity",
            "region": region,
            "path": str(path.relative_to(ROOT)),
            "status": _status(path),
            "size_bytes": size,
            "size_human": _human(size),
            "covered_by_script": True,
        })

    for category, base, regions in (
        ("NSIDC G02202 sea ice", ROOT / "data/raw/nsidc/g02202", ["antarctic"]),
        ("NASA PO.DAAC OSCAR", ROOT / "data/raw/oscar", sorted(CONNECTIVITY_REGIONS)),
    ):
        for region in regions:
            target = base if region == "antarctic" else base / region
            files = [
                p for p in target.rglob("*")
                if p.is_file() and p.suffix.lower() in {".nc", ".nc4", ".h5", ".hdf5"}
            ] if target.exists() else []
            size = sum(_bytes(p) for p in files)
            required.append({
                "category": category,
                "region": region,
                "path": str(target.relative_to(ROOT)),
                "status": "downloaded" if files else "missing",
                "size_bytes": size,
                "size_human": _human(size),
                "covered_by_script": True,
            })

    # Sources useful for interpretation but not downloaded by this orchestrator.
    not_covered = [
        ("Argo profiles", ROOT / "data/raw/argo", "not covered by current script"),
        ("WOA23 climatology", ROOT / "data/raw/woa23", "already available; climatology only"),
        ("NSIDC G02135 aggregate extent", ROOT / "data/raw/nsidc/S_seaice_extent_daily_v4.0.csv", "already available; not spatial concentration"),
        ("NASA/OC-CCI ocean colour", ROOT / "data/raw/ocean_color", "already available; not required by CMEMS connectivity run"),
        ("IMARPE/RAM biological response", ROOT / "data/biomasa_cruceros.csv", "already available; biological response, not connectivity field"),
    ]
    for category, path, note in not_covered:
        if path.is_dir():
            files = [p for p in path.rglob("*") if p.is_file()]
            size = sum(_bytes(p) for p in files)
        else:
            size = _bytes(path)
        required.append({
            "category": category,
            "region": "—",
            "path": str(path.relative_to(ROOT)),
            "status": "available" if size else "missing",
            "size_bytes": size,
            "size_human": _human(size),
            "covered_by_script": False,
            "note": note,
        })

    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "records": sorted(required, key=lambda row: int(row["size_bytes"]), reverse=True),
    }


def _run(script: str, args: list[str]) -> int:
    command = [sys.executable, str(ROOT / "scripts" / script), *args]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    print("RUN", " ".join(command))
    result = subprocess.run(command, cwd=ROOT, env=env)
    return result.returncode


def _write_report(inventory: dict[str, object]) -> Path:
    quality_path = ROOT / "data/processed/tables/connectivity_quality_report.json"
    panel_path = ROOT / "data/processed/tables/connectivity_panel_monthly.csv"
    quality = json.loads(quality_path.read_text()) if quality_path.exists() else {}
    panel = pd.read_csv(panel_path, parse_dates=["date"]) if panel_path.exists() else pd.DataFrame()

    lines = [
        "# ANCHOVETA 360 — reporte del pipeline de conectividad",
        "",
        f"Generado: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "## Estado de archivos",
        "",
        "| Categoría | Región | Estado | Tamaño | Cubierto por script | Archivo/directorio | Nota |",
        "|---|---|---:|---:|---:|---|---|",
    ]
    for row in inventory["records"]:
        lines.append(
            f"| {row['category']} | {row['region']} | {row['status']} | "
            f"{row['size_human']} | {row['covered_by_script']} | `{row['path']}` | "
            f"{row.get('note', '')} |"
        )
    lines.extend([
        "",
        "## Validación",
        "",
        f"- Archivos esperados: {quality.get('summary', {}).get('n_files', 'no ejecutada')}",
        f"- Válidos: {quality.get('summary', {}).get('n_ok', 'no ejecutada')}",
        f"- Faltantes: {quality.get('summary', {}).get('n_missing', 'no ejecutada')}",
        f"- Parciales heredados: {quality.get('summary', {}).get('n_partial_legacy', 'no ejecutada')}",
        "",
        "## Panel procesado",
        "",
    ])
    if panel.empty:
        lines.append("El panel aún no existe o no pudo leerse.")
    else:
        region_summary = (
            panel.groupby("region", as_index=True)
            .agg(n_months=("date", "nunique"), first_date=("date", "min"), last_date=("date", "max"))
        )
        lines.extend([
            f"- Filas: {len(panel)}",
            f"- Regiones: {', '.join(sorted(panel['region'].dropna().unique()))}",
            f"- Fecha mínima: {panel['date'].min().date()}",
            f"- Fecha máxima: {panel['date'].max().date()}",
            "",
            "Cobertura temporal por región:",
            "",
        ])
        lines.extend(
            f"- `{region}`: {int(row.n_months)} meses ({row.first_date.date()} a {row.last_date.date()})"
            for region, row in region_summary.iterrows()
        )
        lines.extend([
            "",
            "El panel permite análisis exploratorio solamente en regiones y capas "
            "que tengan cobertura válida. Las regiones con datos faltantes no se "
            "rellenan automáticamente.",
        ])
        full_period = (
            panel.groupby("region")["date"].nunique().min() >= 300
            and panel["date"].nunique() >= 300
            and {"peninsula_antarctica", "south_pacific_intermediate", "peru_humboldt"}
            <= set(panel["region"].dropna().unique())
        )
    if panel.empty:
        full_period = False
    lines.extend([
        "",
        "## Conclusión automática",
        "",
        (
            "Con los archivos actuales sí se puede ejecutar una evaluación exploratoria "
            "para Bellingshausen–Pacífico Sur intermedio–Humboldt, pero no una prueba "
            "temporal completa de conectividad antártica: la Península Antártica solo "
            "tiene una observación mensual y faltan regiones/productos adicionales."
            if not full_period else
            "Existe una cobertura temporal común suficiente para la evaluación exploratoria "
            "entre una caja antártica, el Pacífico Sur y Humboldt."
        ),
        "La presencia de un archivo no demuestra conectividad: se deben comparar "
        "anomalías, capas verticales, corrientes y cobertura temporal. La relación "
        "con anchoveta sigue siendo exploratoria y depende de la respuesta biológica "
        "disponible.",
    ])
    report_path = ROOT / "data/processed/tables/connectivity_pipeline_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("inventory", "download", "process", "all"), default="all")
    parser.add_argument("--regions", nargs="+", choices=sorted(CONNECTIVITY_REGIONS), default=sorted(CONNECTIVITY_REGIONS))
    parser.add_argument("--start", default="1998-01-01")
    parser.add_argument("--end", default="2025-12-01")
    parser.add_argument("--physics-max-depth", default="1000")
    parser.add_argument("--bgc-max-depth", default="500")
    parser.add_argument("--skip-ice", action="store_true")
    parser.add_argument("--skip-oscar", action="store_true")
    parser.add_argument(
        "--skip-legacy-copernicus",
        action="store_true",
        help="no descargar los productos CMEMS peruanos heredados en data/raw/copernicus",
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    inventory = _inventory()
    (ROOT / "data/processed/tables/connectivity_file_inventory.json").write_text(
        json.dumps(inventory, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    if args.mode in {"download", "all"}:
        common = ["--regions", *args.regions, "--start", args.start, "--end", args.end,
                  "--physics-max-depth", args.physics_max_depth, "--bgc-max-depth", args.bgc_max_depth]
        if args.force:
            common.append("--force")
        _run("07_download_connectivity.py", common)
        if not args.skip_legacy_copernicus:
            _run(
                "02_download_experiment_b.py",
                [
                    "--start", args.start,
                    "--end", args.end,
                    "--skip-occci",
                    "--skip-nasa",
                    "--skip-era5",
                    *( ["--force"] if args.force else [] ),
                ],
            )
        if not args.skip_ice:
            _run("08_download_sea_ice.py", ["--start", args.start, "--end", args.end])
        if not args.skip_oscar:
            _run("09_download_oscar.py", ["--regions", *args.regions, "--start", args.start, "--end", args.end])
    if args.mode in {"process", "all"}:
        _run("11_build_connectivity_panel.py", [])
        _run("12_validate_connectivity.py", [])
    inventory = _inventory()
    report = _write_report(inventory)
    print(f"Inventory: {ROOT / 'data/processed/tables/connectivity_file_inventory.json'}")
    print(f"Report: {report}")


if __name__ == "__main__":
    main()

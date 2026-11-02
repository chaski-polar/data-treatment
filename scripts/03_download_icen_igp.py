"""Descarga y normaliza el ICEN oficial publicado por el IGP/ENFEN."""

from __future__ import annotations

import argparse
import io
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd


URL = "http://met.igp.gob.pe/datos/ICEN.txt"
PAGE_URL = "http://met.igp.gob.pe/datos/lista_eventos_ICEN.html"
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW = ROOT / "data/raw/igp/ICEN.txt"
DEFAULT_CSV = ROOT / "data/raw/igp/icen_monthly.csv"


def download(url: str, target: Path) -> None:
    request = Request(url, headers={"User-Agent": "nasahackaton-data-pipeline/1.0"})
    with urlopen(request, timeout=60) as response:  # noqa: S310 - URL is an explicit public source
        target.write_bytes(response.read())


def parse_icen(source: Path) -> pd.DataFrame:
    rows = []
    for line in source.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip() or line.lstrip().startswith("%"):
            continue
        fields = line.split()
        if len(fields) != 3:
            continue
        year, month, value = fields
        try:
            year_i, month_i, value_f = int(year), int(month), float(value)
        except ValueError:
            continue
        if not 1 <= month_i <= 12:
            continue
        rows.append({"year": year_i, "month": month_i, "icen": value_f})
    if not rows:
        raise ValueError(f"No se encontraron filas ICEN en {source}")
    frame = pd.DataFrame(rows).sort_values(["year", "month"]).drop_duplicates(["year", "month"])
    frame["date"] = pd.to_datetime(dict(year=frame["year"], month=frame["month"], day=1))
    frame["source"] = "IGP/ENFEN; ICEN basado en ERSSTv5"
    frame["source_url"] = URL
    return frame[["date", "year", "month", "icen", "source", "source_url"]]


def parse_events(page_bytes: bytes) -> pd.DataFrame:
    tables = pd.read_html(io.BytesIO(page_bytes))
    event_tables = [
        table for table in tables
        if list(table.columns)[:6] == [
            "Año inicial", "Mes inicial", "Año final",
            "Mes final", "Duración", "Magnitud",
        ]
    ]
    if len(event_tables) != 2:
        raise ValueError(f"Se esperaban 2 tablas de eventos y se encontraron {len(event_tables)}")
    frames = []
    for event_type, table in zip(("el_nino_costero", "la_nina_costera"), event_tables):
        current = table.copy()
        current.columns = ["year_start", "month_start", "year_end", "month_end", "duration_months", "magnitude"]
        current["year_end"] = pd.to_numeric(current["year_end"], errors="coerce")
        current["month_end"] = pd.to_numeric(current["month_end"], errors="coerce")
        current["start_date"] = pd.to_datetime(
            dict(year=current["year_start"], month=current["month_start"], day=1),
            errors="coerce",
        )
        current["end_date"] = pd.to_datetime(
            dict(year=current["year_end"], month=current["month_end"], day=1),
            errors="coerce",
        ) + pd.offsets.MonthEnd(1)
        current["event_type"] = event_type
        frames.append(current[["event_type", "start_date", "end_date", "duration_months", "magnitude"]])
    return pd.concat(frames, ignore_index=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=URL)
    parser.add_argument("--raw", type=Path, default=DEFAULT_RAW)
    parser.add_argument("--output", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--events-output", type=Path, default=ROOT / "data/raw/igp/icen_events.csv")
    parser.add_argument("--page-url", default=PAGE_URL)
    parser.add_argument("--no-download", action="store_true")
    args = parser.parse_args()
    args.raw.parent.mkdir(parents=True, exist_ok=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if not args.no_download:
        download(args.url, args.raw)
    frame = parse_icen(args.raw)
    frame.to_csv(args.output, index=False, date_format="%Y-%m-%d")
    page_request = Request(args.page_url, headers={"User-Agent": "nasahackaton-data-pipeline/1.0"})
    with urlopen(page_request, timeout=60) as response:  # noqa: S310 - explicit public source
        events = parse_events(response.read())
    args.events_output.parent.mkdir(parents=True, exist_ok=True)
    events.to_csv(args.events_output, index=False, date_format="%Y-%m-%d")
    print(f"ICEN guardado: {args.output} ({len(frame)} meses, {frame.date.min().date()}–{frame.date.max().date()})")
    print(f"Eventos guardados: {args.events_output} ({len(events)} eventos)")


if __name__ == "__main__":
    main()

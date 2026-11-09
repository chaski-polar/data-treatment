# data-treatment

Descarga, preparación y análisis de datos ambientales y pesqueros para estudiar
asociaciones entre variables del océano Austral, el sistema de la Corriente de
Humboldt y la anchoveta peruana (*Engraulis ringens*).

Los resultados son **asociaciones exploratorias**, no pruebas de causalidad ni
de transporte físico entre la Antártida y el Perú.

## Estructura

| Carpeta | Contenido |
|---|---|
| `src/nasahackaton/` | Paquete Python: fuentes, descargas, transformaciones y modelos |
| `scripts/` | Scripts numerados del pipeline (descarga → paneles → experimentos) |
| `analysis_r/` | Pipeline estadístico en R (contraste H0/H1); ver `analysis_r/README.md` |
| `data/` | Datos versionados pequeños; `data/punto1_anchoveta/` tiene desembarques, cuotas y biomasa con un `LEEME.md` por fuente |
| `docs/` | Metodología, reportes e informe del análisis exploratorio |

## Instalación

Python (requiere [uv](https://docs.astral.sh/uv/); instala Python 3.14 si falta):

```bash
uv sync
uv run python scripts/<script>.py
```

R (4.x, solo para `analysis_r/`):

```bash
Rscript analysis_r/00_install_packages.R
```

## Reproducir el análisis exploratorio

`data/processed/` no se versiona, así que los paneles intermedios deben
regenerarse con los scripts de `scripts/`. Para repetir solo los modelos con el
panel ya usado en el informe:

```bash
Rscript analysis_r/04_exploratory_models.R \
  --panel analysis_r/data/exploratory_nointerp/exploratory_cruise_panel_used.csv \
  --out-dir <carpeta_de_salida>
```

## Fuentes

Cada conjunto de datos indica su fuente en su `LEEME.md` o en
`docs/metodologia.md`. Fuentes principales: IMARPE (cruceros y biomasa), BCRP
(desembarques), PRODUCE (cuotas y temporadas), RAM Legacy v4.44, NOAA PSL/CPC
(Niño 1+2, PDO, AAO/SAM), NSIDC (hielo marino antártico), ESA OC-CCI
(clorofila), Copernicus Marine y World Ocean Atlas 2023.

## Limitaciones

Ver `docs/informe_analisis_exploratorio_h1_h0.md` (sección 4.4). En resumen:
pocos cruceros con fechas completas, resultados sensibles a la estructura
temporal y respuestas biológicas que no deben combinarse entre sí.

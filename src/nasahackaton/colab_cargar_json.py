# ANCHOVETA 360: carga y revisión del JSON de datos en Google Colab.
# Copiar cada bloque "# %%" en una celda distinta.

# %% 1. Subir el archivo desde el equipo (o usar la celda 1b para Drive)
from google.colab import files
subido = files.upload()  # elegir estructura_datos_anchoveta360.json
RUTA = next(iter(subido))

# %% 1b. Alternativa: leerlo desde Google Drive
# from google.colab import drive
# drive.mount("/content/drive")
# RUTA = "/content/drive/MyDrive/ANCHOVETA360/estructura_datos_anchoveta360.json"

# %% 2. Leer el JSON
import json
import pandas as pd

with open(RUTA, encoding="utf-8") as fh:
    datos = json.load(fh)
print("Secciones:", list(datos))

# %% 3. Revisar que la estructura sea correcta
errores = []
for clave in ["meses_inicio", "frecuencia", "fuentes", "variables", "zonas", "series"]:
    if clave not in datos:
        errores.append(f"Falta la sección '{clave}'")

meses = pd.period_range(datos["meses_inicio"], datos.get("meses_fin", datos["meses_inicio"]), freq="M")
for variable, por_zona in datos.get("series", {}).items():
    if variable not in datos.get("variables", {}):
        errores.append(f"La variable '{variable}' no está descrita en 'variables'")
    for zona, valores in por_zona.items():
        if zona not in datos.get("zonas", {}):
            errores.append(f"La zona '{zona}' de '{variable}' no está en 'zonas'")
        if "meses_fin" in datos and len(valores) != len(meses):
            errores.append(f"{variable}/{zona}: {len(valores)} valores, se esperaban {len(meses)} (de {meses[0]} a {meses[-1]})")
for nombre, var in datos.get("variables", {}).items():
    if var.get("fuente") not in datos.get("fuentes", {}):
        errores.append(f"La fuente de '{nombre}' no está en 'fuentes'")

print("Sin errores" if not errores else "\n".join(errores))

# %% 4. Convertir las series a una tabla (una fila por mes, una columna por variable y zona)
def series_a_tabla(datos, seccion="series"):
    columnas = {}
    for variable, por_zona in datos.get(seccion, {}).items():
        if variable.startswith("_"):
            continue
        for zona, valores in por_zona.items():
            columnas[f"{variable}__{zona}"] = pd.Series(valores, dtype="float")
    tabla = pd.DataFrame(columnas)
    tabla.index = pd.period_range(datos["meses_inicio"], periods=len(tabla), freq="M").to_timestamp()
    return tabla

tabla = series_a_tabla(datos)
tabla.head()

# %% 5. Ver fuentes, zonas y hallazgos
display(pd.DataFrame(datos["fuentes"]).T[["nombre", "tipo", "cobertura_temporal"]])
display(pd.DataFrame(datos["zonas"]).T[["nombre", "region", "escala", "lat", "lon"]])
display(pd.DataFrame(datos.get("hallazgos", []))[["id", "titulo", "estado"]])

# %% 6. Guardar el JSON (por ejemplo, después de agregar datos) y descargarlo
with open("datos_anchoveta360.json", "w", encoding="utf-8") as fh:
    json.dump(datos, fh, ensure_ascii=False, indent=2)
files.download("datos_anchoveta360.json")

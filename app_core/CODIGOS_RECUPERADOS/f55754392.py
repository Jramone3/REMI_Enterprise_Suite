# clasificador_versiones.py — Clasificación de versiones antiguas y respaldos

import os
import json

RUTA_SALON = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "biblioteca_remi",
    "salon_versiones"
)

RUTA_INDICE = os.path.join(RUTA_SALON, "index_versiones.json")

def cargar_indice_versiones():
    if not os.path.exists(RUTA_INDICE):
        return {}
    try:
        with open(RUTA_INDICE, "r") as f:
            return json.load(f)
    except:
        return {}

def guardar_indice_versiones(indice):
    with open(RUTA_INDICE, "w") as f:
        json.dump(indice, f, indent=2, ensure_ascii=False)

def registrar_version(ruta):
    indice = cargar_indice_versiones()

    if "versiones" not in indice:
        indice["versiones"] = []

    if ruta not in indice["versiones"]:
        indice["versiones"].append(ruta)

    guardar_indice_versiones(indice)
    return f"Versión registrada: {ruta}"

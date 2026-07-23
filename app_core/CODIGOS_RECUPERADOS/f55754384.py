# clasificador_scripts.py — Clasificación de scripts patrimoniales

import os
import json

RUTA_SALON = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "biblioteca_remi",
    "salon_scripts"
)

RUTA_INDICE = os.path.join(RUTA_SALON, "index_scripts.json")

def cargar_indice_scripts():
    if not os.path.exists(RUTA_INDICE):
        return {}
    try:
        with open(RUTA_INDICE, "r") as f:
            return json.load(f)
    except:
        return {}

def guardar_indice_scripts(indice):
    with open(RUTA_INDICE, "w") as f:
        json.dump(indice, f, indent=2, ensure_ascii=False)

def registrar_script(ruta):
    indice = cargar_indice_scripts()

    if "scripts" not in indice:
        indice["scripts"] = []

    if ruta not in indice["scripts"]:
        indice["scripts"].append(ruta)

    guardar_indice_scripts(indice)
    return f"Script registrado: {ruta}"

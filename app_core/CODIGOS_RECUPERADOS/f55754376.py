# clasificador_proyectos.py — Clasificación de proyectos patrimoniales

import os
import json

RUTA_SALON = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "biblioteca_remi",
    "salon_proyectos"
)

RUTA_INDICE = os.path.join(RUTA_SALON, "index_proyectos.json")

def cargar_indice_proyectos():
    if not os.path.exists(RUTA_INDICE):
        return {}
    try:
        with open(RUTA_INDICE, "r") as f:
            return json.load(f)
    except:
        return {}

def guardar_indice_proyectos(indice):
    with open(RUTA_INDICE, "w") as f:
        json.dump(indice, f, indent=2, ensure_ascii=False)

def registrar_proyecto(ruta):
    indice = cargar_indice_proyectos()

    if "proyectos" not in indice:
        indice["proyectos"] = []

    if ruta not in indice["proyectos"]:
        indice["proyectos"].append(ruta)

    guardar_indice_proyectos(indice)
    return f"Proyecto registrado: {ruta}"

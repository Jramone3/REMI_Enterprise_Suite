# clasificador_memoria.py — Clasificación de memoria histórica

import os
import json

RUTA_SALON = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "biblioteca_remi",
    "salon_memoria_historica"
)

RUTA_INDICE = os.path.join(RUTA_SALON, "index_memoria.json")

def cargar_indice_memoria():
    if not os.path.exists(RUTA_INDICE):
        return {}
    try:
        with open(RUTA_INDICE, "r") as f:
            return json.load(f)
    except:
        return {}

def guardar_indice_memoria(indice):
    with open(RUTA_INDICE, "w") as f:
        json.dump(indice, f, indent=2, ensure_ascii=False)

def registrar_memoria(ruta):
    indice = cargar_indice_memoria()

    if "memoria" not in indice:
        indice["memoria"] = []

    if ruta not in indice["memoria"]:
        indice["memoria"].append(ruta)

    guardar_indice_memoria(indice)
    return f"Memoria histórica registrada: {ruta}"

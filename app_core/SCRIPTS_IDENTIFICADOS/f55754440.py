# mapa_biblioteca.py — Mapa maestro de la Biblioteca Patrimonial REMI

import os
import json

BASE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "biblioteca_remi"
)

SALONES = {
    "corpus": "corpus",
    "memoria": "memoria",
    "scripts": "salon_scripts",
    "proyectos": "salon_proyectos",
    "versiones": "salon_versiones",
    "librerias": "salon_librerias",
    "memoria_historica": "salon_memoria_historica"
}

def obtener_mapa():
    mapa = {}
    for nombre, carpeta in SALONES.items():
        ruta = os.path.join(BASE, carpeta)
        indice = None

        # Buscar archivo index dentro del salón
        for archivo in os.listdir(ruta):
            if archivo.startswith("index") and archivo.endswith(".json"):
                with open(os.path.join(ruta, archivo), "r") as f:
                    indice = json.load(f)

        mapa[nombre] = {
            "ruta": ruta,
            "indice": indice if indice else {}
        }

    return mapa

# clasificador_librerias.py — Clasificación de librerías del sistema y programas

import os
import json

RUTA_SALON = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "biblioteca_remi",
    "salon_librerias"
)

RUTA_INDICE = os.path.join(RUTA_SALON, "index_librerias.json")

def cargar_indice_librerias():
    if not os.path.exists(RUTA_INDICE):
        return {}
    try:
        with open(RUTA_INDICE, "r") as f:
            return json.load(f)
    except:
        return {}

def guardar_indice_librerias(indice):
    with open(RUTA_INDICE, "w") as f:
        json.dump(indice, f, indent=2, ensure_ascii=False)

def clasificar_libreria(ruta):
    ruta_lower = ruta.lower()

    if "/usr/lib" in ruta_lower or "/lib" in ruta_lower:
        return "librerias_sistema"

    if "site-packages" in ruta_lower or "dist-packages" in ruta_lower:
        return "librerias_python"

    if "share" in ruta_lower or "bin" in ruta_lower:
        return "librerias_programas"

    if "old" in ruta_lower or "backup" in ruta_lower:
        return "librerias_duplicadas"

    return "librerias_desconocidas"

def registrar_libreria(ruta):
    indice = cargar_indice_librerias()
    categoria = clasificar_libreria(ruta)

    if categoria not in indice:
        indice[categoria] = []

    if ruta not in indice[categoria]:
        indice[categoria].append(ruta)

    guardar_indice_librerias(indice)
    return f"Librería registrada en: {categoria}"

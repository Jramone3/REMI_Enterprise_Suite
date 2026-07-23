# clasificador_biblioteca.py — Clasificación patrimonial de archivos

import os
import json

RUTA_BIBLIOTECA = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "biblioteca_remi"
)
RUTA_INDICE = os.path.join(RUTA_BIBLIOTECA, "biblioteca_index.json")

def cargar_indice():
    if not os.path.exists(RUTA_INDICE):
        return {}
    try:
        with open(RUTA_INDICE, "r") as f:
            return json.load(f)
    except:
        return {}

def guardar_indice(indice):
    with open(RUTA_INDICE, "w") as f:
        json.dump(indice, f, indent=2, ensure_ascii=False)

def clasificar_ruta_basico(ruta):
    ruta_lower = ruta.lower()

    # Librerías
    if any(ext in ruta_lower for ext in [".so", ".dll", ".a", ".la"]):
        from .clasificador_librerias import registrar_libreria
        registrar_libreria(ruta)
        return "librerias"

    # Scripts
    if any(ext in ruta_lower for ext in [".py", ".sh", ".bash", ".js"]):
        from .clasificador_scripts import registrar_script
        registrar_script(ruta)
        return "scripts"

    # Proyectos (carpetas o archivos con nombres típicos)
    if any(pal in ruta_lower for pal in ["proyecto", "project", "src", "build"]):
        from .clasificador_proyectos import registrar_proyecto
        registrar_proyecto(ruta)
        return "proyectos"

    # Memoria histórica
    if any(pal in ruta_lower for pal in ["memoria", "diario", "historial", "bitacora"]):
        from .clasificador_memoria import registrar_memoria
        registrar_memoria(ruta)
        return "memoria_historica"

    # Versiones antiguas
    if any(pal in ruta_lower for pal in ["old", "backup", "respaldo", "v1", "v2", "v3"]):
        from .clasificador_versiones import registrar_version
        registrar_version(ruta)
        return "versiones"

    # Corpus documental
    if any(ext in ruta_lower for ext in [".txt", ".md", ".pdf"]):
        return "corpus"

    # Por defecto
    return "utiles"

def registrar_archivo_en_biblioteca(ruta_original):
    indice = cargar_indice()
    categoria = clasificar_ruta_basico(ruta_original)

    if categoria not in indice:
        indice[categoria] = []

    if ruta_original not in indice[categoria]:
        indice[categoria].append(ruta_original)

    guardar_indice(indice)
    return f"Archivo registrado en categoría: {categoria}"

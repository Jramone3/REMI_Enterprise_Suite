# escaneo_seguro.py — Escaneo incremental y reanudable del bosque patrimonial

import os
import json

RUTA_LEGADO = "/mnt/sda7/REMI"
ARCHIVO_PROGRESO = "progreso_escaneo.json"

def cargar_progreso():
    if not os.path.exists(ARCHIVO_PROGRESO):
        return {"ultima_ruta": None, "completado": False}
    try:
        with open(ARCHIVO_PROGRESO, "r") as f:
            return json.load(f)
    except:
        return {"ultima_ruta": None, "completado": False}

def guardar_progreso(ultima_ruta, completado=False):
    progreso = {
        "ultima_ruta": ultima_ruta,
        "completado": completado
    }
    with open(ARCHIVO_PROGRESO, "w") as f:
        json.dump(progreso, f, indent=2)

def generar_lista_archivos():
    rutas = []
    for raiz, _, archivos in os.walk(RUTA_LEGADO):
        for archivo in archivos:
            rutas.append(os.path.join(raiz, archivo))
    return rutas

def escanear_por_lotes(tamano_lote=200):
    """
    Recorre el bosque por lotes de archivos.
    Guarda progreso para poder reanudar si se interrumpe.
    """
    progreso = cargar_progreso()
    rutas = generar_lista_archivos()

    if progreso["completado"]:
        return "Escaneo ya completado anteriormente."

    ultima_ruta = progreso["ultima_ruta"]
    empezar = False if ultima_ruta else True

    procesados = 0
    for ruta in rutas:
        if not empezar:
            if ruta == ultima_ruta:
                empezar = True
            continue

        # Aquí podrías hacer análisis ligero del archivo si quieres
        # Por ahora solo "lo tocamos" para que el SO lo cachee
        try:
            with open(ruta, "rb") as f:
                f.read(1024)
        except:
            pass

        procesados += 1
        ultima_ruta = ruta

        if procesados >= tamano_lote:
            guardar_progreso(ultima_ruta, completado=False)
            return f"Lote procesado. Última ruta: {ultima_ruta}"

    # Si llegamos aquí, terminamos todo el bosque
    guardar_progreso(ultima_ruta, completado=True)
    return "Escaneo completo del bosque."

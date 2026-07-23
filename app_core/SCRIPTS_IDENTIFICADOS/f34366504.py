# publicador_remi.py
# Módulo 8 – Preparación de Publicación Patrimonial
# Custodio: jramonrivasg | Fecha: 2025-11-14

import os
import shutil

origen = os.path.expanduser("~/documentacion/demo_remi/REMI_resumen_final.txt")
destino = os.path.expanduser("~/documentacion/publicaciones/REMI_resumen_publicado.txt")

def preparar_publicacion(origen, destino):
    try:
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        shutil.copy(origen, destino)
        print(f"[✔] Archivo preparado para publicación oficial en: {destino}")
    except Exception as e:
        print(f"[✘] Error al preparar publicación: {e}")

if __name__ == "__main__":
    preparar_publicacion(origen, destino)

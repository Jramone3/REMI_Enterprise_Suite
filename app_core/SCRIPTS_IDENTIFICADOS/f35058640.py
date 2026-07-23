# verificador_publicacion_remi.py
# Módulo 9 – Verificación de Publicación Patrimonial
# Custodio: jramonrivasg | Fecha: 2025-11-14

import hashlib
import os

original = os.path.expanduser("~/documentacion/demo_remi/REMI_resumen_final.txt")
publicado = os.path.expanduser("~/documentacion/publicaciones/REMI_resumen_publicado.txt")

def calcular_sha256(ruta):
    with open(ruta, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def verificar_integridad(original, publicado):
    try:
        hash_original = calcular_sha256(original)
        hash_publicado = calcular_sha256(publicado)
        if hash_original == hash_publicado:
            print(f"[✔] Integridad verificada. Huella: {hash_original}")
        else:
            print("[✘] El archivo publicado no coincide con el original.")
            print(f"Huella original:  {hash_original}")
            print(f"Huella publicado: {hash_publicado}")
    except Exception as e:
        print(f"[✘] Error al verificar integridad: {e}")

if __name__ == "__main__":
    verificar_integridad(original, publicado)

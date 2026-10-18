#!/usr/bin/env python3
import os
import shutil

PATH_APP = "/home/ramon/Escritorio/Proyecto_Remi_IA_App"

print("🧹 [REMI OPTIMIZER]: Iniciando purga de cachés y entropía en sda5...")

# Carpetas de caché de desarrollo que el i5-650 no necesita almacenar en los backups
caches_a_eliminar = [
    ".next", "out", ".cache", "dist", "build", 
    ".npm/_cacache", ".yarn/cache"
]

contador_eliminados = 0

for raiz, dirs, archivos in os.walk(PATH_APP):
    for carpeta in list(dirs):
        if carpeta in caches_a_eliminar:
            ruta_completa = os.path.join(raiz, carpeta)
            try:
                print(f"🗑️ Eliminando caché muerta: {carpeta} en {raiz}")
                shutil.rmtree(ruta_completa)
                contador_eliminados += 1
            except Exception as e:
                print(f"⚠️ No se pudo eliminar {carpeta}: {e}")

print(f"\n✅ [OPTIMIZACIÓN LISTA]: Se purgaron {contador_eliminados} bloques de entropía.")
print("💾 El almacenamiento local para backups ha sido aligerado.")

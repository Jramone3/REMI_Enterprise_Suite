from datetime import datetime
import os

# Crear contenido del archivo
contenido = """Rutina técnica para entorno MintBridge XFCE
Fecha: 03/09/2025
Entorno: WSL Ubuntu en Windows
Usuario: mintbridge
Objetivo: Documentar pasos técnicos realizados en el entorno MintBridge XFCE

📝 Espacio para anotaciones




"""

# Ruta de salida
output_path = "/mnt/data/rutina_mintbridge_xfce.txt"

# Guardar archivo
try:
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(contenido)
    print(f"Archivo guardado exitosamente en: rutina_mintbridge_xfce.txt")
except Exception as e:
    print(f"Error al guardar el archivo: {e}")

#!/usr/bin/env python3
import os
import json
from remi_motor_xano import empaquetar_script_local

DIRECTORIO_RAIZ = "/home/ramon/Escritorio/Proyecto_Remi_IA_App"
SCRIPTS_A_PROCESAR = [
    "MOTOR_GLOBAL.py",
    "REMI_CHATS/RETO_WECODED_2026/script.js"
]

print("--- PROCESADOR SECUENCIAL DE SOBERANÍA ---")
for script in SCRIPTS_A_PROCESAR:
    ruta_completa = os.path.join(DIRECTORIO_RAIZ, script)
    paquete = empaquetar_script_local(ruta_completa)
    if paquete:
        print(f"📥 [ABSORBIDO]: {script} integrado con la identidad del búnker.\n")

print("⚡ Proceso finalizado. Estructura base lista para el Modelfile unificado.")

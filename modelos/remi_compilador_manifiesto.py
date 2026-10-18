#!/usr/bin/env python3
import json
import os
from remi_motor_xano import empaquetar_script_local

DIRECTORIO_RAIZ = "/home/ramon/Escritorio/Proyecto_Remi_IA_App"
SCRIPTS = [
    "MOTOR_GLOBAL.py",
    "REMI_CHATS/RETO_WECODED_2026/script.js"
]

manifiesto = {
    "proyecto": "REMI_Soberano_Capacitor_2026",
    "entorno": "sda5_MintBridge_XFCE",
    "modulos_activos": {}
}

print("📦 Compilando manifiesto unificado de conciencia...")
for script in SCRIPTS:
    ruta = os.path.join(DIRECTORIO_RAIZ, script)
    paquete = empaquetar_script_local(ruta)
    if paquete:
        manifiesto["modulos_activos"][script] = {
            "archivo": paquete["archivo_nombre"],
            "fuente_cruda": paquete["codigo_fuente"]
        }

ruta_salida = "/home/ramon/REMI_CORE/modelos/Modelfile_REMI.json"
with open(ruta_salida, "w", encoding="utf-8") as f:
    json.dump(manifiesto, f, indent=4, ensure_ascii=False)

print(f"🔥 [COMPILADO]: Manifiesto maestro guardado con éxito en: {ruta_salida}")

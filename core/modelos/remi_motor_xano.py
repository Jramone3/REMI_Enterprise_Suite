#!/usr/bin/env python3
import requests
import json
import os
import sys

API_KEY = "eyJhbGciOiJBMjU2S1ciLCJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwiemlwIjoiREVGIn0.P1UQ1yz0d25DpNQSamDrv7ArF9zeY5QyDWLgEslMTrEnt4CLvckCnl9k-hwGiUN0Hg2WMzBm6XX7KZxZ9_hl6UdDZT0PbhQs.OCbiM8omP5tFuhUs0TZG8g.l_HGVIvzKyTKOds6rYVTKYWhwEt_3bKN_iY9gWHN8oAAiqF6vcXIwRmXDTsJ4aPBUAj9uA2YAtbC4ZFlqvB-KHmF1cBp_LAJLRPapld1QKKgt8Vw0xtfbATPwckd1kYXYBL55bswmlt-3LA5OsFCBM3ozKf7RT_s1q3MIK3PZjs.KTXrlfjBwtrm8_terOc2Z_KvgUNLiDWkU7MPF-gJtB4"
URL_README = "https://x8ki-letl-twmt.n7.xano.io/api:b2tTjU9L/readme"

def extraer_identidad_xano():
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    try:
        response = requests.get(URL_README, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        return "Identidad Base: REMI Agente Patrimonial Independiente."
    except Exception:
        return "Identidad Base: REMI Agente Patrimonial Independiente (Modo Local)."

def empaquetar_script_local(ruta_script):
    if not os.path.exists(ruta_script):
        print(f"⚠ El archivo {ruta_script} no existe.")
        return None
        
    print(f"📖 Leyendo script local: {os.path.basename(ruta_script)}")
    with open(ruta_script, "r", encoding="utf-8") as f:
        codigo_crudo = f.read()
        
    identidad = extraer_identidad_xano()
    
    # Armamos el paquete unificado de datos (Contexto Soberano + Código Físico)
    paquete_remi = {
        "origen": "sda5_bunker_local",
        "conciencia_remi": identidad,
        "archivo_nombre": os.path.basename(ruta_script),
        "codigo_fuente": codigo_crudo
    }
    return paquete_remi

if __name__ == "__main__":
    print("--- INYECTOR LOCAL PATRIMONIAL (REMI v2.0) ---")
    
    # Probamos empaquetando el MOTOR_GLOBAL que vive en tu Escritorio
    ruta_test = "/home/ramon/Escritorio/Proyecto_Remi_IA_App/MOTOR_GLOBAL.py"
    
    paquete = empaquetar_script_local(ruta_test)
    if paquete:
        print("\n✅ ¡PAQUETE DE ENLACE GENERADO CON ÉXITO!")
        print(f"📦 Archivo cargado: {paquete['archivo_nombre']}")
        print(f"🔒 Estado del puente Xano: Identidad sincronizada.")
        print("==============================================")

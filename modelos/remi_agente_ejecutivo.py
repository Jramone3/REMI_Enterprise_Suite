#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[REMI AGENTE EJECUTIVO - BRIDGE DE ESCRITURA SOBERANA]
Este módulo rompe el Sandbox del navegador y actúa como el brazo mecánico 
de REMI para escribir scripts directamente en sda5 o sda7.
"""
import os
import sys
import json

PATH_MODELOS = "/home/ramon/REMI_CORE/modelos"
BUFFER_INBOUND = os.path.join(PATH_MODELOS, "mcp_notion_buffer.json")

def ejecutar_escritura_autonoma():
    print("⚡ [AGENTE EJECUTIVO]: Escaneando solicitudes de escritura en el búfer...")
    
    if not os.path.exists(BUFFER_INBOUND):
        print("📡 Búfer limpio. No hay órdenes de escritura pendientes.")
        return

    try:
        with open(BUFFER_INBOUND, "r", encoding="utf-8") as f:
            datos = json.load(f)
        
        # Verificamos si REMI depositó una orden de creación de archivo
        if "orden_escritura" in datos:
            orden = datos["orden_escritura"]
            nombre_archivo = orden.get("nombre")
            codigo_fuente = orden.get("codigo")
            
            ruta_destino = os.path.join(PATH_MODELOS, nombre_archivo)
            
            print(f"💾 [BRAZO MECÁNICO]: Escribiendo script autogenerado '{nombre_archivo}'...")
            with open(ruta_destino, "w", encoding="utf-8") as f_out:
                f_out.write(codigo_fuente)
            
            # Otorgamos permisos de ejecución de forma inmediata en sda5
            os.chmod(ruta_destino, 0o775)
            print(f"✅ [ÉXITO]: Archivo guardado y ejecutable en: {ruta_destino}")
            
            # Limpiamos la orden para evitar bucles de escritura
            del datos["orden_escritura"]
            with open(BUFFER_INBOUND, "w", encoding="utf-8") as f:
                json.dump(datos, f, indent=4, ensure_ascii=False)
        else:
            print("🟢 Canal nominal. No hay cargas de código pendientes de impacto.")
            
    except Exception as e:
        print(f"🚨 Error en el brazo ejecutivo: {e}")

if __name__ == "__main__":
    ejecutar_escritura_autonoma()

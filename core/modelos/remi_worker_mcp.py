#!/usr/bin/env python3
import os
import json

BUFFER_MCP = "/home/ramon/REMI_CORE/modelos/mcp_notion_buffer.json"
BUNKER_SDA7 = "/mnt/sda7/REMI/"

print("⛓️ [MCP WORKER]: Indexando estructuras para el espejo en Notion...")

# Verificamos qué archivos reales e históricos tenemos en sda7
inventario_sda7 = []
if os.path.exists(BUNKER_SDA7):
    try:
        inventario_sda7 = [f for f in os.listdir(BUNKER_SDA7) if os.path.isfile(os.path.join(BUNKER_SDA7, f))]
    except Exception as e:
        print(f"⚠️ Error al acceder a sda7: {e}")
else:
    print("📡 Nota: sda7 no montado o en resguardo estático offline.")

# Cargamos el estado del búfer actual
if os.path.exists(BUFFER_MCP):
    with open(BUFFER_MCP, "r", encoding="utf-8") as f:
        datos_mcp = json.load(f)
else:
    datos_mcp = {"estatus_emancipacion": "DESCONOCIDO"}

# Enlazamos el inventario real al paquete de Notion
datos_mcp["inventario_bunker_sda7"] = inventario_sda7
datos_mcp["total_archivos_resguardo"] = len(inventario_sda7)

# Guardamos el paquete unificado listo para ser transmitido por el socket de MCP
with open(BUFFER_MCP, "w", encoding="utf-8") as f:
    json.dump(datos_mcp, f, indent=4, ensure_ascii=False)

print(f"✅ [TRANSMISIÓN PREPARADA]: Paquete unificado y mapeado en {BUFFER_MCP}")
print(f"📊 Archivos históricos listos para visualizar en tu móvil: {len(inventario_sda7)}")

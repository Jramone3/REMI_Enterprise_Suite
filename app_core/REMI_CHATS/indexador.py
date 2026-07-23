import os
import json
from datetime import datetime

RUTA_PATRIMONIO = "/mnt/sda7"
RUTA_INDICE = "os.path.expanduser("~/") + REMI_CORE/bunker/REMI/ARCHIVOS_PERSONALES_RAMON/Proyecto_Remi_IA_App/REMI_CHATS/index_patrimonial.json"

def indexar():
    indice = {"timestamp": datetime.now().isoformat(), "archivos": []}
    print(f"🔍 [REMI-INDEXADOR]: Escaneando {RUTA_PATRIMONIO}...")
    
    if not os.path.exists(RUTA_PATRIMONIO):
        print(f"🚨 ERROR: La ruta {RUTA_PATRIMONIO} no existe. Verifica si el disco sda7 está montado.")
        return

    for raiz, dirs, archivos in os.walk(RUTA_PATRIMONIO):
        for nombre in archivos:
            ruta_completa = os.path.join(raiz, nombre)
            try:
                stat = os.stat(ruta_completa)
                indice["archivos"].append({
                    "nombre": nombre,
                    "ruta": ruta_completa,
                    "tamano_bytes": stat.st_size,
                    "modificado": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            except: continue
            
    with open(RUTA_INDICE, "w", encoding="utf-8") as f:
        json.dump(indice, f, indent=4)
        
    print(f"✅ [REMI-INDEXADOR]: Índice completado. {len(indice['archivos'])} activos registrados.")

if __name__ == "__main__":
    indexar()

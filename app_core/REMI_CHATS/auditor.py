import json
import os

INDICE_PATH = "index_patrimonial.json"
OBJETIVO = "INVESTIGACION_ZHI_FRAUD"

def auditar():
    with open(INDICE_PATH, "r") as f:
        data = json.load(f)
    
    print(f"⚖️ [REMI-AUDITOR]: Verificando coherencia en sector: {OBJETIVO}")
    
    anomalias = []
    for activo in data["archivos"]:
        if OBJETIVO in activo["ruta"]:
            # Regla de Coherencia 1: Archivos vacíos son sospechosos de corrupción
            if activo["tamano_bytes"] == 0:
                anomalias.append(f"ALERTA: Activo vacío detectado: {activo['nombre']}")
            
    if not anomalias:
        print("✅ [REMI-AUDITOR]: No se detectaron anomalías estructurales graves. Coherencia confirmada.")
    else:
        for a in anomalias:
            print(a)

if __name__ == "__main__":
    auditar()

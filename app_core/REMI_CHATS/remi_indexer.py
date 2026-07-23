#!/usr/bin/env python3
import os
import json
import re

# Ruta principal de trabajo en el búnker (sda7)
BUNKER_PATH = os.path.expanduser("~/REMI_CORE/bunker/REMI")
OUTPUT_INDEX = os.path.join(BUNKER_PATH, "remi_agenda_index.json")

# Patrones para identificar órdenes ejecutivas dentro del código o textos
PATTERNS = [
    re.compile(r'(?:#|//|/\*)\s*(?:ORDEN|TODO|REQUERIMIENTO|TAREA):\s*(.*)', re.IGNORECASE),
]

def scan_bunker():
    orders = []
    order_id = 1

    print(f"🔍 Escaneando archivos de desarrollo en: {BUNKER_PATH}...")
    
    for root, _, files in os.walk(BUNKER_PATH):
        for file in files:
            if file.endswith(('.py', '.txt', '.json', '.js', '.md')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            for pattern in PATTERNS:
                                match = pattern.search(line)
                                if match:
                                    orders.append({
                                        "id": order_id,
                                        "archivo": os.path.relpath(file_path, BUNKER_PATH),
                                        "linea": line_num,
                                        "instruccion": match.group(1).strip()
                                    })
                                    order_id += 1
                except Exception as e:
                    continue

    # Guardar el índice estructurado para la consulta de REMI
    with open(OUTPUT_INDEX, 'w', encoding='utf-8') as out:
        json.dump(orders, out, indent=4, ensure_ascii=False)

    print(f"✅ Agenda de Cabecera generada con éxito: {len(orders)} órdenes registradas en {OUTPUT_INDEX}")

if __name__ == "__main__":
    scan_bunker()

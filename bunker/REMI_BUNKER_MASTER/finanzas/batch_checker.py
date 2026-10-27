#!/usr/bin/env python3
import json
from datetime import datetime

def batch_check():
    json_path = "/mnt/sda7/finanzas/banned_entities.json"
    targets_path = "/mnt/sda7/finanzas/targets.txt"
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            restricted_entities = json.load(f)
    except FileNotFoundError:
        print(f"[Error] No se encontró la base de datos: {json_path}")
        return

    try:
        with open(targets_path, 'r', encoding='utf-8') as f:
            targets = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[Error] No se encontró el archivo de objetivos: {targets_path}")
        return

    today = datetime.now().date()
    print(f"\n[Binance Compliance Scan] Analizando {len(targets)} entidades (Fecha: {today})")
    print("-" * 65)

    for target in targets:
        query_lower = target.lower()
        matched = False
        for date_str, entities in restricted_entities.items():
            for entity in entities:
                if query_lower in entity.lower() or entity.lower() in query_lower:
                    print(f"[!] Alerta: '{target}' coincide con entidad restringida -> {entity} ({date_str})")
                    matched = True
        if not matched:
            print(f"[OK] {target} sin coincidencias de riesgo.")
    print("-" * 65)

if __name__ == "__main__":
    batch_check()

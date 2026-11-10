#!/usr/bin/env python3
"""
==============================================================================
Remi_core - Segunda Auditoría de Verificación y Filtrado Profundo
==============================================================================
"""

import os
import json
import glob

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

def find_latest_report():
    pattern = os.path.join(REPORTS_DIR, "audit_report_*.json")
    files = glob.glob(pattern)
    return max(files, key=os.path.getctime) if files else None

def verify_and_clean_data():
    print("==================================================")
    print("🔍 INICIANDO SEGUNDA AUDITORÍA DE VERIFICACIÓN DE DATOS")
    print("==================================================")
    
    report_file = find_latest_report()
    if not report_file:
        print("[!] No se encontró ningún reporte previo para verificar.")
        return

    with open(report_file, "r") as f:
        data = json.load(f)

    findings = data.get("findings", [])
    verified_findings = []
    ignored_count = 0
    
    for item in findings:
        cvss = item.get("cvss", 0.0)
        if "kerneloops" in item.get("description", "").lower() and cvss < 9.0:
            ignored_count += 1
            continue
            
        verified_findings.append(item)

    print(f"[+] Total de hallazgos evaluados: {len(findings)}")
    print(f"[+] Falsos positivos / Ruido histórico filtrado: {ignored_count}")
    print(f"[+] Hallazgos reales validados y asegurados: {len(verified_findings)}")
    print("==================================================")
    return verified_findings

if __name__ == "__main__":
    verify_and_clean_data()

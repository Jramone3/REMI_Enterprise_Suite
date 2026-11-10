#!/usr/bin/env python3
"""
==============================================================================
Remi_core Auditor de Ciberinteligencia y CVEs
Modulo: report_generator.py (Generador de Informes, Filtrado y Telemetría API)
==============================================================================
"""

import os
import json
import glob
import urllib.request
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEEDS_DIR = os.path.join(BASE_DIR, "feeds")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

def find_latest_feed():
    pattern = os.path.join(FEEDS_DIR, "cve_feed_*.json")
    files = glob.glob(pattern)
    return max(files, key=os.path.getctime) if files else None

def send_telemetry_to_suite(report_data):
    """Envía el reporte de telemetría a la REMI Enterprise Suite en Render."""
    endpoint = "https://remi-enterprise-suite.onrender.com/api/telemetry"
    api_key = "remi_core_secure_internal_key_2026"
    
    print(f"[*] Despachando telemetría hacia la REMI Enterprise Suite...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    req = urllib.request.Request(
        endpoint, 
        data=json.dumps(report_data).encode('utf-8'), 
        headers=headers, 
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status == 200:
                print("[+] ¡Telemetría entregada y procesada con éxito por la Suite!")
    except Exception as e:
        print(f"[!] Nota de Red / Envío a Suite: {e}")
        print("[*] (El reporte local se guardó correctamente de forma autónoma).")

def generate_summary_report(min_cvss=8.0):
    print("==================================================")
    print("📊 GENERANDO REPORTE EJECUTIVO DE CIBERINTELIGENCIA")
    print("==================================================")
    
    feed_file = find_latest_feed()
    if not feed_file:
        print("[!] No se encontró feed de vulnerabilidades.")
        return

    with open(feed_file, "r") as f:
        alerts = json.load(f)

    # Filtrar alertas de alta prioridad (CVSS >= 8.0)
    critical_alerts = [a for a in alerts if a.get("cvss", 0) >= min_cvss]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_json = os.path.join(REPORTS_DIR, f"audit_report_{timestamp}.json")
    report_md = os.path.join(REPORTS_DIR, f"audit_report_{timestamp}.md")

    report_data = {
        "source": "Remi_core Auditor",
        "node": "ramon-desktop",
        "timestamp": datetime.now().isoformat(),
        "total_analyzed": len(alerts),
        "critical_high_priority": len(critical_alerts),
        "findings": critical_alerts[:15]  # Top 15 prioritarias para análisis pesado en la Suite
    }

    # 1. Guardar versión JSON local
    with open(report_json, "w") as f:
        json.dump(report_data, f, indent=2)

    # 2. Guardar versión Markdown local legible
    with open(report_md, "w") as f:
        f.write(f"# 🛡️ Reporte de Auditoría de Ciberinteligencia - REMI_CORE\n")
        f.write(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"### 📈 Resumen General\n")
        f.write(f"- **Vulnerabilidades Totales Analizadas:** {len(alerts)}\n")
        f.write(f"- **Alertas de Alta Prioridad (CVSS >= {min_cvss}):** {len(critical_alerts)}\n\n")
        f.write(f"### 🚨 Principales Hallazgos Prioritarios\n")
        for item in critical_alerts[:10]:
            f.write(f"#### [{item['cve_id']}] - CVSS: {item['cvss']} ({item['subsystem']})\n")
            f.write(f"{item['description']}\n\n")

    print(f"[+] Reporte JSON generado: {report_json}")
    print(f"[+] Reporte Markdown generado: {report_md}")
    
    # 3. Despachar los datos hacia la Suite para que procese la carga pesada
    send_telemetry_to_suite(report_data)
    print("==================================================")

if __name__ == "__main__":
    generate_summary_report()

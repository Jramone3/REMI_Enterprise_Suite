#!/usr/bin/env python3
"""
==============================================================================
Remi_core Auditor de Ciberinteligencia y CVEs
Modulo: cve_monitor.py
==============================================================================
"""

import os
import json
import urllib.request
import urllib.parse
from datetime import datetime

# Rutas de configuracion
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "security_profiles.json")
FEEDS_DIR = os.path.join(BASE_DIR, "feeds")

def load_profile():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {"monitored_subsystems": ["kernel", "mptcp", "openssl"]}

def fetch_cve_alerts(keyword, cvss_min=7.5):
    print(f"[*] Escaneando vulnerabilidades criticas para subsistema: {keyword}...")
    url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={keyword}"
    
    req = urllib.request.Request(url, headers={'User-Agent': 'RemiCoreAuditor/1.0'})
    alerts = []
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                vulnerabilities = data.get("vulnerabilities", [])
                
                for item in vulnerabilities:
                    cve_data = item.get("cve", {})
                    cve_id = cve_data.get("id")
                    metrics = cve_data.get("metrics", {})
                    
                    # Extraer CVSS v3.1 o v3.0 si existe
                    cvss_score = 0.0
                    if "cvssMetricV31" in metrics:
                        cvss_score = metrics["cvssMetricV31"][0]["cvssData"]["baseScore"]
                    elif "cvssMetricV30" in metrics:
                        cvss_score = metrics["cvssMetricV30"][0]["cvssData"]["baseScore"]
                    
                    if cvss_score >= cvss_min:
                        descriptions = cve_data.get("descriptions", [{}])
                        desc_text = descriptions[0].get("value", "Sin descripcion disponible.")
                        alerts.append({
                            "cve_id": cve_id,
                            "cvss": cvss_score,
                            "subsystem": keyword,
                            "description": desc_text[:200] + "..."
                        })
    except Exception as e:
        print(f"[!] Error al consultar NVD para {keyword}: {e}")
        
    return alerts

def run_cve_scan():
    profile = load_profile()
    subsystems = profile.get("monitored_subsystems", [])
    all_findings = []

    print(f"==================================================")
    print(f"🛡️  EJECUTANDO AUDITORIA DE CVEs: REMI_CORE ({datetime.now().strftime('%Y-%m-%d %H:%M')})")
    print(f"==================================================")

    for sub in subsystems:
        findings = fetch_cve_alerts(sub)
        all_findings.extend(findings)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(FEEDS_DIR, f"cve_feed_{timestamp}.json")
    
    with open(output_file, "w") as f:
        json.dump(all_findings, f, indent=2)
        
    print(f"==================================================")
    print(f"✅ Escaneo completado. Total de alertas criticas: {len(all_findings)}")
    print(f"📁 Reporte guardado en: {output_file}")
    print(f"==================================================")

if __name__ == "__main__":
    run_cve_scan()

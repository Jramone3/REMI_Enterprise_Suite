#!/usr/bin/env python3
"""
==============================================================================
Remi_core Auditor de Ciberinteligencia y CVEs
Modulo: system_checker.py (Verificador Local de Paquetes y Versiones)
==============================================================================
"""

import os
import json
import subprocess
import glob

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEEDS_DIR = os.path.join(BASE_DIR, "feeds")

def get_installed_packages():
    """Obtiene la lista de paquetes instalados en el sistema Debian/Ubuntu/Mint."""
    print("[*] Leyendo inventario de paquetes instalados en el sistema local...")
    installed = {}
    try:
        cmd = "dpkg-query -W -f='${Package} ${Version}\n'"
        output = subprocess.check_output(cmd, shell=True, text=True)
        for line in output.splitlines():
            parts = line.split()
            if len(parts) == 2:
                installed[parts[0]] = parts[1]
    except Exception as e:
        print(f"[!] Error al consultar paquetes locales con dpkg: {e}")
    
    print(f"[+] Total de paquetes locales indexados: {len(installed)}")
    return installed

def find_latest_feed():
    """Busca el archivo JSON de feed de CVEs más reciente en la carpeta feeds/."""
    pattern = os.path.join(FEEDS_DIR, "cve_feed_*.json")
    files = glob.glob(pattern)
    if not files:
        return None
    latest_file = max(files, key=os.path.getctime)
    return latest_file

def audit_local_system():
    print(f"==================================================")
    print(f"🛡️  INICIANDO CRUCE LOCAL DE VULNERABILIDADES (AUDIT)")
    print(f"==================================================")
    
    installed_pkgs = get_installed_packages()
    feed_file = find_latest_feed()
    
    if not feed_file:
        print("[!] No se encontró ningún archivo de feed de CVEs. Ejecute primero cve_monitor.py")
        return

    print(f"[*] Analizando contra el feed: {os.path.basename(feed_file)}")
    
    with open(feed_file, "r") as f:
        cve_alerts = json.load(f)

    matches = []
    for alert in cve_alerts:
        subsys = alert.get("subsystem", "").lower()
        # Verificamos si algún paquete instalado coincide con el subsistema monitoreado
        for pkg_name, pkg_version in installed_pkgs.items():
            if subsys in pkg_name.lower():
                matches.append({
                    "package": pkg_name,
                    "installed_version": pkg_version,
                    "cve_id": alert.get("cve_id"),
                    "cvss": alert.get("cvss"),
                    "description": alert.get("description")
                })

    print(f"==================================================")
    print(f"✅ Auditoría local finalizada.")
    print(f"🔍 Coincidencias encontradas con paquetes del sistema: {len(matches)}")
    print(f"==================================================")
    
    if matches:
        print("\n[!] Alertas preliminares asociadas a componentes locales:")
        for m in matches[:5]: # Mostrar las primeras 5 para evitar saturar la consola
            print(f" - Paquete: {m['package']} ({m['installed_version']}) | CVE: {m['cve_id']} (CVSS: {m['cvss']})")
    else:
        print("[+] Ninguna coincidencia directa crítica detectada en los paquetes analizados del sistema.")

if __name__ == "__main__":
    audit_local_system()

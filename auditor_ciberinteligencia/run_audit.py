#!/usr/bin/env python3
"""
==============================================================================
Remi_core Auditor de Ciberinteligencia y CVEs
Lanzador Principal Integrado (Orquestador)
==============================================================================
"""

import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, "engine"))

from cve_monitor import run_cve_scan
from system_checker import audit_local_system
from report_generator import generate_summary_report

def main():
    print("\n🚀 INICIANDO AUDITORÍA COMPLETA: Remi_core Auditor\n")
    # Fase 1: Escaneo Global NVD
    run_cve_scan()
    print("\n")
    # Fase 2: Cruce con Paquetes Locales
    audit_local_system()
    print("\n")
    # Fase 3: Generación de Reportes Filtrados
    generate_summary_report(min_cvss=8.0)
    print("\n✅ SECUENCIA DE AUDITORÍA COMPLETADA CON ÉXITO.\n")

if __name__ == "__main__":
    main()

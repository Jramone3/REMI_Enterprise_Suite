import os
import subprocess
import time

# Rutas definidas en el Corpus 2026
VIGIA_PATH = "os.path.expanduser("~/") + REMI_CORE/oro_finance/registros/vigia_ingresos.py"
LOG_PATH = "os.path.expanduser("~/") + REMI_CORE/oro_finance/registros/produccion_remi.log"

def ejecutar_ciclo_remi():
    print(f"🤖 [REMI]: Iniciando ciclo de vigilancia patrimonial...")
    
    # 1. Ejecutar el Vigía (Blockscout API)
    if os.path.exists(VIGIA_PATH):
        try:
            resultado = subprocess.run(["python3", VIGIA_PATH], capture_output=True, text=True)
            print(resultado.stdout)
        except Exception as e:
            print(f"❌ Error al ejecutar Vigía: {e}")
    else:
        print("⚠️ No se encuentra el script Vigía.")

    # 2. Verificar integridad de archivos críticos
    archivos = ["/mnt/sda7/REMI/", "os.path.expanduser("~/") + REMI_CORE/"]
    for ruta in archivos:
        if os.path.exists(ruta):
            print(f"✅ Estructura detectada: {ruta}")
        else:
            print(f"🚨 Alerta: Falta acceso a {ruta}")

if __name__ == "__main__":
    while True:
        ejecutar_ciclo_remi()
        print("🛰️ REMI en espera (próximo escaneo en 1 hora)...")
        # Dormir 3600 segundos (1 hora) para no saturar la API gratuita
        time.sleep(3600)

# REMI Capacitor 2026 - CORE LOADER
# Verificador de entorno, rutas y dependencias del sistema REMI

import os
import sys

RUTA_BASE = "/home/ramon/REMI_CORE/motores/"

def verificar_entorno():
    print("[CORE_LOADER] Verificando entorno operativo...")
    if not os.path.exists(RUTA_BASE):
        print("[CORE_LOADER] ERROR: Ruta base no encontrada:", RUTA_BASE)
        return False
    print("[CORE_LOADER] Ruta base OK")
    return True

def cargar_motor_global():
    print("[CORE_LOADER] Intentando cargar MOTOR_GLOBAL.py...")
    try:
        from motores.MOTOR_GLOBAL import MotorGlobal
        motor = MotorGlobal()
        motor.sincronizar()
        print("[CORE_LOADER] MOTOR_GLOBAL cargado correctamente")
    except Exception as e:
        print("[CORE_LOADER] ERROR al cargar MOTOR_GLOBAL:", e)

if __name__ == "__main__":
    if verificar_entorno():
        cargar_motor_global()

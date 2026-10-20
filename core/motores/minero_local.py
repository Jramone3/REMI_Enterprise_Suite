#!/usr/bin/env python3
import os
import time
from pathlib import Path

# Ruta Patrimonial Real y Activa en sda5
BASE = Path("/home/ramon/REMI_CORE")
LOG = Path("/home/ramon/REMI_CORE/logs/minero.log")

def log(msg):
    try:
        with open(LOG, "a") as f:
            f.write(f"[MINERO] {time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")
    except Exception as e:
        print(f"Error escribiendo log: {e}")

print("🪙 Minero Local: Inicializando escaneo de patrimonio activo en sda5...")

while True:
    if BASE.exists():
        archivos = sum(len(files) for _, _, files in os.walk(BASE))
        log(f"Indexación patrimonial activa: {archivos} archivos detectados en sda5.")
    else:
        log(f"Alerta: Núcleo Capacitor {BASE} no detectado en sda5.")
    time.sleep(30)

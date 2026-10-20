#!/usr/bin/env python3
import subprocess
import time
import os
from pathlib import Path

BASE = Path("/home/ramon/REMI_CORE")
LOG = BASE / "logs/motor_global.log"

BALIZA = BASE / "motores/baliza_fase1.py"
MINERO = BASE / "motores/minero_local.py"

def log(msg):
    with open(LOG, "a") as f:
        f.write(f"[MOTOR_GLOBAL] {time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")

def lanzar_baliza():
    subprocess.Popen(["python3", str(BALIZA)])

def lanzar_minero():
    subprocess.Popen(["python3", str(MINERO)])

if __name__ == "__main__":
    log("Motor Global iniciado.")
    lanzar_baliza()
    lanzar_minero()

    while True:
        log("Ciclo lógico activo.")
        time.sleep(20)

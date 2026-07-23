# modo_emergencia.py — Manejo de cortes eléctricos y reanudación segura

import os
import time
from .escaneo_seguro import cargar_progreso, escanear_por_lotes

BITACORA = "bitacora_emergencia.log"

def registrar_evento(mensaje):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{timestamp}] {mensaje}\n"
    with open(BITACORA, "a") as f:
        f.write(linea)

def revisar_estado_escaneo():
    progreso = cargar_progreso()
    if progreso["completado"]:
        return "Escaneo completo previamente."
    if progreso["ultima_ruta"]:
        return f"Escaneo incompleto. Última ruta: {progreso['ultima_ruta']}"
    return "Escaneo no iniciado."

def reanudar_escaneo_seguro(tamano_lote=300):
    estado = revisar_estado_escaneo()
    registrar_evento(f"Intentando reanudar escaneo. Estado: {estado}")
    resultado = escanear_por_lotes(tamano_lote=tamano_lote)
    registrar_evento(f"Resultado reanudación: {resultado}")
    return resultado

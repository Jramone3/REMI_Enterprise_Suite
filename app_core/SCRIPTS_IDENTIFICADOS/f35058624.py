# validador_csv_viewer.py
# Módulo 12 – Validación de CSV Patrimonial
# Custodio: jramonrivasg | Fecha: 2025-11-14

import pandas as pd
import os

# Ruta del archivo CSV patrimonial
ruta_csv = os.path.expanduser("~/documentacion/demo_remi/REMI_eventos.csv")

def validar_csv(ruta):
    try:
        df = pd.read_csv(ruta)
        print("[✔] CSV cargado correctamente.")
        print(f"Columnas detectadas: {list(df.columns)}")
        print(f"Total de eventos registrados: {len(df)}")
    except Exception as e:
        print(f"[✘] Error al cargar CSV: {e}")

if __name__ == "__main__":
    validar_csv(ruta_csv)

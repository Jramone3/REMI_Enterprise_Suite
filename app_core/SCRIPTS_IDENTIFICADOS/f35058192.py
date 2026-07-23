# huella_comparador.py
# Módulo 6 – Comparación de Huellas Patrimoniales
# Custodio: jramonrivasg | Fecha: 2025-11-14

import pandas as pd
import os

ruta_original = os.path.expanduser("~/documentacion/demo_remi/REMI_eventos.csv")
ruta_nueva = os.path.expanduser("~/documentacion/demo_remi/REMI_eventos_nueva.csv")

def comparar_csv(ruta1, ruta2):
    try:
        df1 = pd.read_csv(ruta1)
        df2 = pd.read_csv(ruta2)
        diferencias = pd.concat([df1, df2]).drop_duplicates(keep=False)
        if diferencias.empty:
            print("[✔] No se detectaron alteraciones entre versiones.")
        else:
            print("[✘] Se detectaron diferencias:")
            print(diferencias)
    except Exception as e:
        print(f"[✘] Error al comparar archivos: {e}")

if __name__ == "__main__":
    comparar_csv(ruta_original, ruta_nueva)

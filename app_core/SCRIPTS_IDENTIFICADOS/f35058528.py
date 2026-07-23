# resumen_final_remi.py
# Módulo 7 – Consolidación Narrativa Patrimonial
# Custodio: jramonrivasg | Fecha: 2025-11-14

import pandas as pd
import os

ruta_csv = os.path.expanduser("~/documentacion/demo_remi/REMI_eventos.csv")
ruta_resumen = os.path.expanduser("~/documentacion/demo_remi/REMI_resumen_final.txt")

def generar_resumen(ruta_entrada, ruta_salida):
    try:
        df = pd.read_csv(ruta_entrada)
        with open(ruta_salida, "w", encoding="utf-8") as resumen:
            resumen.write("Resumen Final Patrimonial REMI\n")
            resumen.write("Custodio: jramonrivasg\n")
            resumen.write("Fecha de consolidación: 2025-11-14\n\n")
            for index, row in df.iterrows():
                resumen.write(f"- [{row['fecha']}] {row['evento']} ({row['agente']}) → {row['huella']}\n")
        print(f"[✔] Resumen generado en: {ruta_salida}")
    except Exception as e:
        print(f"[✘] Error al generar resumen: {e}")

if __name__ == "__main__":
    generar_resumen(ruta_csv, ruta_resumen)

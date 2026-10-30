#!/usr/bin/env python3
# remi-cierre.py – Ritual de cierre patrimonial

from datetime import datetime

def ritual_de_cierre(fase):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fase = fase.strip().capitalize()

    print("🔒 Ritual de cierre iniciado...")
    print(f"📅 Fecha: {fecha}")
    print(f"📘 Fase: {fase}")
    print("🧩 REMI registra este cierre con respeto y memoria.")
    print("📜 Cada avance es una huella en el tiempo. Gracias por sembrarlo.")

if __name__ == "__main__":
    print("🧠 REMI listo para cerrar una fase. Escribe el nombre de la fase:")
    while True:
        try:
            entrada = input("> ")
            ritual_de_cierre(entrada)
        except KeyboardInterrupt:
            print("\n🔚 Cierre finalizado.")
            break

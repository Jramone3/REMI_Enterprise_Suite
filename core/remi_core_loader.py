import os
import json
import time

CORPUS_PATH = "/home/ramon/REMI_CORE/bunker/REMI/ARCHIVOS_PERSONALES_RAMON/Proyecto_Remi_IA_App/REMI_CHATS/corpus_remi_master.json"

def cargar_identidad():
    print("🧠 REMI_LOADER: Sincronizando identidad desde el Corpus Master...")
    if os.path.exists(CORPUS_PATH):
        with open(CORPUS_PATH, 'r') as f:
            data = json.load(f)
            print(f"✅ Identidad cargada: {data.get('version', '2026')}")
            return True
    else:
        print("⚠️ Alerta: Corpus no encontrado en la ruta oficial. Iniciando modo de emergencia.")
        return False

if __name__ == "__main__":
    if cargar_identidad():
        print("⚡ Sistema listo para operación autónoma.")
    time.sleep(2)

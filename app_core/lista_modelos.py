import os
from google import genai
from dotenv import load_dotenv

load_dotenv(dotenv_path="os.path.expanduser("~/") + Escritorio/Proyecto_Remi_IA_App/.env")
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key, http_options={'api_version': 'v1beta'})

print("--- RECOLECTANDO NOMBRES DE MODELOS ---")
try:
    modelos = client.models.list()
    for m in modelos:
        # Solo imprimimos el nombre básico
        print(f"NOMBRE: {m.name}")
except Exception as e:
    print(f"Error: {e}")

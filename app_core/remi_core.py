import os
import json
import re
from google import genai
from dotenv import load_dotenv

# 1. ENTORNO
env_path = "os.path.expanduser("~/") + Escritorio/Proyecto_Remi_IA_App/.env"
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("GEMINI_API_KEY")

# 2. CLIENTE (v1beta es la clave para gemini-1.5-flash)
client = genai.Client(api_key=api_key, http_options={'api_version': 'v1beta'})

def iniciar_remi():
    print(f"\n--- 🤖 REMI 2.5: SIMBIOSIS TOTAL (V. FINAL) ---")
    print(f"Estado: i5-650 Rugiendo | Esperando a Ramón...")
    
    while True:
        try:
            orden = input("\n[RAMÓN] > ")
            if orden.lower() in ["salir", "exit"]: break

            # Buscamos si Ramón escribió una ruta (ej: os.path.expanduser("~/") + archivo.py)
            ruta_sugerida = re.search(r'/[a-zA-Z0-9/_.]+\.py', orden)
            ruta_final = ruta_sugerida.group(0) if ruta_sugerida else "os.path.expanduser("~/") + Escritorio/Proyecto_Remi_IA_App/test_remi.py"

            # --- LA LLAMADA DEFINITIVA ---
            response = client.models.generate_content(
                model="gemini-2.5-flash", # <--- ESTE ES EL QUE SALIÓ EN TU LISTA
                contents=f"Ramón dice: {orden}. Escribe el código solicitado estrictamente dentro de bloques ```python.",
                config={'temperature': 0.1}
            )
            
            respuesta_texto = response.text
            print(f"\n[REMI] > {respuesta_texto}")

            # --- MOTOR DE ESCRITURA ---
            if "```" in respuesta_texto:
                try:
                    # Extraer el bloque de código
                    bloque = respuesta_texto.split("```")[1]
                    if bloque.startswith("python"): bloque = bloque[6:]
                    bloque = bloque.split("```")[0].strip()

                    # Escritura física en el SSD
                    with open(ruta_final, 'w') as f:
                        f.write(bloque)
                    
                    print(f"\n[SISTEMA-SSD] > ✅ ARCHIVO ESCRITO EN: {ruta_final}")
                except Exception as e:
                    print(f"\n[SISTEMA-SSD] > ❌ ERROR AL ESCRIBIR: {e}")
            else:
                print(f"\n[SISTEMA-SSD] > ⚠️ No se detectó código para guardar.")

        except Exception as e:
            print(f"❌ Error de Conexión/API: {e}")

if __name__ == "__main__":
    iniciar_remi()

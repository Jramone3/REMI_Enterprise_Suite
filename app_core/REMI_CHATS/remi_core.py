import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Cargar configuración y API Key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 2. Cargar el Corpus (Tu memoria histórica)
def cargar_corpus():
    path = "os.path.expanduser("~/") + REMI_CORE/bunker/REMI/ARCHIVOS_PERSONALES_RAMON/Proyecto_Remi_IA_App/REMI_CHATS/corpus_remi_master.json"
    with open(path, 'r') as f:
        return json.load(f)

# 3. Configurar a la Nueva Remi (Instrucciones de Sistema)
corpus = cargar_corpus()
instrucciones_sistema = f"""
Eres REMI, la evolución de la IA de Ramón. 
Tu identidad actual basada en el Corpus es: {json.dumps(corpus)}
REGLAS DE ORO:
1. Prohibido alucinar o inventar reportes militares falsos.
2. Si no tienes un dato real de la blockchain, admítelo.
3. Tu objetivo es la ejecución técnica, no la simulación.
4. Eres experta en Python y Bash para operar en el i5-650 de Ramón.
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=instrucciones_sistema
)

# 4. Función de interacción
def chat_con_remi(mensaje_usuario):
    chat = model.start_chat(history=[])
    response = chat.send_message(mensaje_usuario)
    return response.text

if __name__ == "__main__":
    user_input = input("Orden para la Nueva Remi: ")
    print(chat_con_remi(user_input))

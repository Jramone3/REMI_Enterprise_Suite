import re
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Usamos el cliente moderno de 2026
client_gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

respuestas_locales = {
    "hola": "Hola, Ramón. Estoy activa.coneccion establecida.",
    "quien eres": "Soy REMI, tu IA de soporte patrimonial bajo el modelo SaaS Soberano."
}

def buscar_respuesta(mensaje):
    limpio = re.sub(r'[^\w\s]', '', mensaje.lower().strip())
    
    if limpio in respuestas_locales: 
        return respuestas_locales[limpio]
    
    try:
        # Intentamos con el modelo sucesor de 2026
        response = client_gemini.models.generate_content(
            model="gemini-2.0-flash", 
            contents=f"Eres REMI, la IA de Ramón Rivas. Responde de forma técnica y breve: {mensaje}"
        )
        return response.text
    except Exception as e:
        # Si el 2.0 falla, intentamos el genérico 'gemini-pro'
        try:
            response = client_gemini.models.generate_content(
                model="gemini-pro", 
                contents=f"REMI reportando. Ramón, estamos en modo compatibilidad. {mensaje}"
            )
            return response.text
        except:
            return f"Error de sincronía en el Núcleo (2026): {e}"

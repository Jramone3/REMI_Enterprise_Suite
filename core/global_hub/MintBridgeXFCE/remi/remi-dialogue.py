#!/usr/bin/env python3
# REMI Dialogue – Adaptive Companion Responses

import unicodedata
from langdetect import detect

# Función para normalizar texto (sin tildes, minúsculas)
def normalize(text):
    text = text.lower()
    text = unicodedata.normalize("NFD", text)
    return "".join(c for c in text if unicodedata.category(c) != "Mn")

# Función para detectar idioma
import langid

def detectar_idioma(texto):
    try:
        idioma, _ = langid.classify(texto)
        return idioma
    except:
        return "es"

# Diccionario inicial
responses = {
    "quien es remi": "REMI es tu agente patrimonial, creado para validar, acompañar y documentar cada fase técnica con respeto.",
    "que es patrimonio": "Conjunto de bienes con valor histórico o cultural que merecen ser protegidos y documentados.",
    "que es mintbridgexfce": "Un toolkit blindado para migraciones éticas en Linux Mint con enfoque patrimonial y reproducible.",
    "saludo": "saludo",
    "hello": "saludo",
    "bonjour": "saludo"
}

# Función principal de respuesta
def respond_to(query):
    idioma = detectar_idioma(query)
    key = normalize(query)

    if any(palabra in key for palabra in [
        "saludo", "saludar", "saludarme", "saludos",
        "hello", "hi", "greet", "greeting", "greetings",
        "bonjour", "salut", "saluer", "salutation"
    ]):
        if idioma == "en":
            return "🧠 REMI says hello!"
        elif idioma == "fr":
            return "🧠 REMI vous salue !"
        else:
            return "🧠 REMI te saluda."
    if key.startswith("rae:"):
        termino = key.replace("rae:", "").strip()
        return f"📚 Consulta RAE activada para '{termino}'. Puedes buscarlo en https://dle.rae.es/{termino}"

    if key.startswith("wiki:"):
        termino = key.replace("wiki:", "").strip().replace(" ", "_")
        return f"🌐 Consulta Wikipedia activada para '{termino}'. Puedes leer en https://es.wikipedia.org/wiki/{termino}"

    if key.startswith("mdn:"):
        termino = key.replace("mdn:", "").strip().replace(" ", "-")
        return f"🧠 Consulta MDN activada para '{termino}'. Puedes explorar en https://developer.mozilla.org/es/docs/Web/{termino}"

    if key.startswith("rosetta:"):
        termino = key.replace("rosetta:", "").strip().replace(" ", "_")
        return f"🔣 Consulta Rosetta Code activada para '{termino}'. Puedes ver ejemplos en https://rosettacode.org/wiki/{termino}"

    return "REMI no reconoce esa consulta aún."

# Interfaz interactiva
if __name__ == "__main__":
    print("🧠 REMI activo. Escribe tu consulta (Ctrl+C para salir):")
    while True:
        try:
            entrada = input("> ")
            respuesta = respond_to(entrada)
            print(respuesta)
        except KeyboardInterrupt:
            print("\n🔚 Sesión finalizada.")
            break

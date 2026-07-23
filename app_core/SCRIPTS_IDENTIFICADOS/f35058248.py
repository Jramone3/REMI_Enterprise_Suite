# manejador_seguridad_tokens.py
# Módulo 13 – Auditoría de Seguridad Patrimonial REMI
# Custodio: jramonrivasg | Fecha: 2025-11-14

import os

# Tokens patrimoniales trazados
AUTH0_TOKEN = os.getenv("AUTH0_TOKEN")
OPENAI_TOKEN = os.getenv("OPENAI_TOKEN")
POSTGRES_TOKEN = os.getenv("POSTGRES_TOKEN")

def validar_tokens():
    tokens = {
        "Auth0": AUTH0_TOKEN,
        "OpenAI": OPENAI_TOKEN,
        "PostgreSQL": POSTGRES_TOKEN
    }
    for nombre, valor in tokens.items():
        if valor:
            print(f"[✔] Token {nombre} trazado correctamente.")
        else:
            print(f"[✘] Token {nombre} no encontrado. Revisar .env.local")

if __name__ == "__main__":
    validar_tokens()

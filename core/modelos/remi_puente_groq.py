#!/usr/bin/env python3
import os
import requests

GROQ_API_KEY = "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"
URL_GROQ = "https://api.groq.com/openai/v1/chat/completions"

def consulta_hipervelocidad(prompt_sistema, prompt_usuario):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "mixtral-8x7b-32768", # El motor masivo que no congelará el i5-650
        "messages": [
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": prompt_usuario}
        ],
        "temperature": 0.2
    }
    
    try:
        response = requests.post(URL_GROQ, json=data, headers=headers)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"⚠ Error de conexión con Groq: Status {response.status_code}"
    except Exception as e:
        return f"⚠ Fallo crítico en el puente: {str(e)}"

if __name__ == "__main__":
    print("🧠 [REMI_PUENTE]: Probando conexión con el motor masivo de Groq...")
    sys_prompt = "Eres REMI 2026, operando en modo hipervelocidad."
    user_prompt = "Confirma estado de conexión y velocidad."
    resultado = consulta_hipervelocidad(sys_prompt, user_prompt)
    print(resultado)

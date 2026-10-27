#!/usr/bin/env python3
"""
REMI_CORE - Token Gateway Local (Ollama)
Ajustado con mayor tolerancia de tiempo para la carga inicial del modelo.
"""

import sys
import json
import urllib.request
import urllib.error

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "qwen2.5:3b"  # O puedes cambiar a "remi:3b"

def send_local_prompt(prompt, model=DEFAULT_MODEL):
    print(f"[*] Enrutando petición a Ollama local (Modelo: {model})... (Esto puede tardar unos segundos si carga en frío)")
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            OLLAMA_ENDPOINT, 
            data=data, 
            headers={"Content-Type": "application/json"}, 
            method="POST"
        )
        
        # Aumentamos el timeout a 180 segundos para evitar cortes por carga en frío
        with urllib.request.urlopen(req, timeout=180) as response:
            result = json.loads(response.read().decode("utf-8"))
            return "[OLLAMA SUCCESS]:", result.get("response", "")
            
    except urllib.error.URLError as e:
        return "[ERROR]", f"No se pudo conectar con Ollama en {OLLAMA_ENDPOINT}. Detalle: {e}"
    except Exception as e:
        return "[ERROR]", f"Error inesperado: {e}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 remi_token_gateway.py 'Tu mensaje o prompt aquí'")
        sys.exit(1)
        
    user_prompt = sys.argv[1]
    status, response = send_local_prompt(user_prompt)
    print(status)
    print(response)

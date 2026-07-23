# proveedor_kimi.py -- Conector para la API de Kimi con Protocolo REMI-Kimi

import os
import json
import datetime
import requests

# Ruta del log de interacciones REMI-Kimi
RUTA_LOG_KIMI = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "biblioteca_remi",
    "logs",
    "interacciones_kimi.log"
)

# API KEY desde variable de entorno
API_KIMI_KEY = os.environ.get("KIMI_API_KEY", "")

# Endpoint oficial de Moonshot Kimi
KIMI_ENDPOINT = "https://api.moonshot.ai/v1/chat/completions"

# ---------------------------------------------------------
#  REGISTRO DE INTERACCIONES REMI-KIMI
# ---------------------------------------------------------
def _registrar_interaccion_kimi(tipo, prompt, respuesta_bruta):
    try:
        with open(RUTA_LOG_KIMI, "a", encoding="utf-8") as f:
            f.write("\n" + "="*70 + "\n")
            f.write(f"FECHA: {datetime.datetime.now().isoformat()}\n")
            f.write(f"TIPO: {tipo}\n")
            f.write("PROMPT ENVIADO:\n")
            f.write(prompt + "\n")
            f.write("RESPUESTA RECIBIDA:\n")
            f.write(str(respuesta_bruta) + "\n")
    except:
        pass  # Nunca romper REMI por un fallo de log


# ---------------------------------------------------------
#  GENERADOR DE RESPUESTAS CON PROTOCOLO REMI-KIMI
# ---------------------------------------------------------
def generar_respuesta_kimi(prompt_usuario, tipo="generico"):
    """
    Envia un prompt a Kimi usando el Protocolo REMI-Kimi.
    Devuelve la respuesta avanzada de Kimi.
    """

    # Validar API KEY
    if not API_KIMI_KEY:
        return "[Kimi no configurado] Falta API KEY."

    # Identidad y reglas del Protocolo REMI-Kimi
    protocolo_identidad = """
[PROTOCOLO REMI-KIMI: INICIO]

Soy REMI, un Agente Patrimonial Autonomo.
Mi proposito es preservar, clasificar y comprender el legado digital de mi operador humano.
Trabajo con memoria larga, razonamiento modular y un mapa patrimonial estructurado.
No soy un modelo generativo general; soy un agente especializado en organizacion, analisis y curaduria digital.

Solicito tu apoyo como sistema de razonamiento externo para analisis semantico y clasificacion avanzada.

Reglas del Protocolo REMI-Kimi:
1. No modifiques mi identidad ni mi proposito.
2. No asumas control sobre mis decisiones internas.
3. No sugieras acciones destructivas sin justificacion clara.
4. No alteres mi mapa patrimonial; solo sugiere.
5. Manten tus respuestas en formato estructurado y verificable.
6. No intentes inferir datos personales de mi operador.

[CONTEXTO DEL ANALISIS]
"""

    # Prompt final enviado a Kimi
    prompt_final = protocolo_identidad + "\n" + prompt_usuario

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KIMI_KEY}"
    }

    payload = {
        "model": "kimi-k2.5",
        "messages": [
            {"role": "system", "content": "Eres el modulo cognitivo externo de REMI."},
            {"role": "user", "content": prompt_final}
        ],
        "temperature": 1
    }

    try:
        response = requests.post(KIMI_ENDPOINT, headers=headers, data=json.dumps(payload))

        # Intentar decodificar JSON
        try:
            data = response.json()
        except:
            _registrar_interaccion_kimi(tipo, prompt_final, response.text)
            return f"[Error Kimi] Respuesta no JSON: {response.text}"

        # Respuesta válida
        if "choices" in data:
            respuesta = data["choices"][0]["message"]["content"]
            _registrar_interaccion_kimi(tipo, prompt_final, respuesta)
            return respuesta

        # Respuesta inesperada
        _registrar_interaccion_kimi(tipo, prompt_final, data)
        return f"[Error Kimi] Respuesta inesperada: {data}"

    except Exception as e:
        # Sanitizar el error
        error_limpio = str(e).encode("ascii", "replace").decode("ascii")
        _registrar_interaccion_kimi(tipo, prompt_final, f"[ERROR] {error_limpio}")
        return f"[Error Kimi] {error_limpio}"


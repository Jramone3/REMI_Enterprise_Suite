# exportar_respuestas.py
import json
import remi_responde
from datetime import datetime

# Lista de preguntas clave para extraer respuestas
preguntas = [
    "que eres", "donde estas", "que has aprendido",
    "cual es tu proposito", "porque existes", "que representas",
    "tienes emociones", "que has leido",
    "que sabes de filosofia", "que sabes de historia",
    "que sabes de ciencia", "quien soy yo", "sabes quien soy",
    "que sabes de mi"
]

# Generar diccionario con respuestas
respuestas = {}
for p in preguntas:
    try:
        respuestas[p] = remi_responde.responder(p)
    except Exception as e:
        respuestas[p] = f"⚠️ Error al generar respuesta para '{p}': {e}"

# Guardar en archivo JSON con timestamp
archivo_salida = "respuestas_remi.json"
with open(archivo_salida, "w") as f:
    json.dump(respuestas, f, ensure_ascii=False, indent=2)

print(f"✅ Archivo {archivo_salida} generado con éxito ({len(respuestas)} respuestas).")
print(f"🕒 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

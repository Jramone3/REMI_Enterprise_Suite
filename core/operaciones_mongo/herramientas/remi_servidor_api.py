from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import requests

# Añadimos la ruta de sda7 para importar el cerebro neuronal del Búnker
sys.path.append("/home/ramon/REMI_CORE/bunker_respaldo/REMI_BUNKER_MASTER/remi_graphify")
try:
    from remi_brain import consultar_grafo_neuronal
except ImportError:
    def consultar_grafo_neuronal(q): return "[SISTEMA NEURONAL]: Módulo no disponible."

app = Flask(__name__)
CORS(app)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "remi-enterprise"

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json or {}
        user_message = data.get('message', '') or data.get('prompt', '')
        
        if not user_message:
            return jsonify({"response": "Mensaje vacío."}), 400

        # 1. Consultar el sistema neuronal del Búnker en sda7 (119k nodos)
        contexto_neuronal = consultar_grafo_neuronal(user_message)
        
        # 2. Construir el prompt maestro enriquecido
        prompt_maestro = f"""
        {contexto_neuronal}
        
        Instrucción: Eres REMI_IA, el asistente experto de Ramon. Usa el contexto neuronal anterior para responder con precisión quirúrgica sobre la infraestructura, contratos o archivos del Búnker.
        
        Petición de Ramon: {user_message}
        """
        
        # 3. Invocar al motor local Ollama
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt_maestro,
            "stream": False
        }
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        if response.status_code != 200:
            return jsonify({"response": f"Error en Ollama: Código {response.status_code}"}), 500
            
        bot_response = response.json().get("response", "Sin respuesta del modelo.")
        return jsonify({
            "status": "success",
            "neural_context_applied": True,
            "response": bot_response
        })

    except Exception as e:
        return jsonify({"response": f"Error interno: {str(e)}"}), 500

if __name__ == '__main__':
    print("==================================================")
    print("  REMI_IA - API Flask en Puerto 5000 (sda7)       ")
    print("==================================================")
    app.run(host='0.0.0.0', port=5000, debug=False)

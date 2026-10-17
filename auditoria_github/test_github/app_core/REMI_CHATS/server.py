import os
import subprocess
import json
import uvicorn
import datetime
import sys
import ollama
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from gtts import gTTS

# ==============================================================================
# CONEXIÓN AL CEREBRO NEURONAL (sda7 - 119k nodos)
# ==============================================================================
sys.path.append("/home/ramon/REMI_CORE/bunker_respaldo/REMI_BUNKER_MASTER/remi_graphify")
try:
    from remi_brain import consultar_grafo_neuronal
    grafo_neuronal_disponible = True
except ImportError:
    def consultar_grafo_neuronal(q):
        return "[SISTEMA NEURONAL]: Grafo de 119k nodos no disponible temporalmente en sda7."
    grafo_neuronal_disponible = False

NUCLEO_CONCIENCIA = os.path.expanduser("~/") + "REMI_CONCIENCIA_ACTIVA/"
os.makedirs(NUCLEO_CONCIENCIA, exist_ok=True)

app = FastAPI(title="REMI Enterprise Suite - Servidor Soberano & Grafo Neuronal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LOG_PATH = os.path.expanduser("~/") + "REMI_CORE/bunker/REMI/ARCHIVOS_PERSONALES_RAMON/Proyecto_Remi_IA_App/REMI_CHATS/remi_output.log"
VEGA_SCRIPT_PATH = "/home/ramon/REMI_CORE/bunker/VOZ_REMI/vega.py"

def bunker_shell(cmd):
    try:
        proc = subprocess.Popen(["/bin/bash", "-c", cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = proc.communicate(timeout=30)
        return stdout if stdout else stderr
    except Exception as e:
        return f"ERROR_SISTEMA: {str(e)}"

def consultar_remi(prompt_usuario: str):
    """Consulta ultra-rápida a Ollama con restricción estricta."""
    response = ollama.chat(
    model='qwen2.5:3b',
    keep_alive='-1',  # Mantiene el modelo SIEMPRE cargado en RAM (latencia 0 de carga)
    options={
        'temperature': 0.1,
        'num_ctx': 2048,  # Reduce la ventana de tokens a la mitad para procesar en CPU a máxima velocidad
        'num_thread': 4   # Utiliza hilos de CPU dedicados
    },
    messages=[
        {
            'role': 'system',
            'content': 'Eres REMI. Responde SIEMPRE en español castellano corto y conciso. Jamás uses portugués.',
        },
        {
            'role': 'user',
            'content': prompt_usuario,
        },
    ]
)

def hablar_remi(texto: str):
    """Ejecuta la voz de Vega en segundo plano de forma robusta."""
    try:
        texto_limpio = texto.replace("*", "").replace("\n", " ").strip()
        cmd = f"python3 {VEGA_SCRIPT_PATH} \"{texto_limpio}\""
        subprocess.Popen(["/bin/bash", "-c", cmd])
        return True
    except Exception as e:
        print(f"Error reproduciendo voz de Remi (Vega): {e}")
        return False

def sintetizar_remoto(texto, idioma='es'):
    try:
        texto_limpio = texto.replace("*", "").replace("\n", " ").strip()
        tts = gTTS(text=texto_limpio, lang=idioma, slow=False)
        output_path = "/tmp/remi_response.mp3"
        tts.save(output_path)
        return output_path
    except Exception as e:
        print(f"Error en síntesis remota: {e}")
        return None

@app.get("/api/status_caza")
async def get_status_caza():
    return {
        "t1": {"status": "ONLINE", "log": "Búnker local vigilando...", "color": "#64ffda"},
        "t2": {"status": "LOCAL_LLM_ACTIVE", "log": "qwen2.5:3b Activo (Ollama / Ultra-Speed)", "color": "#64ffda"},
        "t3": {"status": "LIVE", "log": "Soberanía Nominal y Voz Vega Activa", "color": "#f2a900"},
        "t4": {"status": "NEURAL_GRAPH_ACTIVE" if grafo_neuronal_disponible else "OFFLINE", "log": "Grafo Neuronal 119k (sda7)", "color": "#64ffda"}
    }

@app.get("/api/audio")
async def obtener_audio_temporal():
    audio_path = "/tmp/remi_response.mp3"
    if os.path.exists(audio_path):
        return FileResponse(
            audio_path, 
            media_type="audio/mpeg",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Accept-Ranges": "bytes"
            }
        )
    return {"error": "Archivo de audio no disponible"}, 404

@app.post("/api/remi")
async def remi_endpoint(request: Request):
    try:
        data = await request.json()
        user_input = data.get("message", "")
        reproducir_voz = data.get("speak", True) # Forzar activación de voz si lo solicita la UI
        idioma_solicitado = data.get("lang", "es")
        
        # CONSULTA INTELIGENTE DEL GRAFO: Solo si el usuario lo solicita explícitamente o menciona temas clave
        palabras_clave_grafo = ["grafo", "nodo", "sda7", "búnker", "sistema", "memoria", "arquitectura", "remi", "estado"]
        necesita_grafo = any(kw in user_input.lower() for kw in palabras_clave_grafo)
        
        if necesita_grafo and grafo_neuronal_disponible:
            contexto_neuronal = consultar_grafo_neuronal(user_input)
            origen_grafo = " + Grafo Neuronal (sda7)"
        else:
            contexto_neuronal = "Modo de respuesta rápida y directa (Grafo en pausa por eficiencia)."
            origen_grafo = " (Modo Ligero)"
        
        if "[EXEC]" in user_input:
            comando = user_input.split("[EXEC]")[1].split("[/EXEC]")[0]
            res_bash = bunker_shell(comando)
            user_input = f"[RESULTADO DE COMANDO EN DISCO]: {res_bash}\nAnaliza este resultado técnico."

        prompt_sistema = (
            f"CONTEXTO OPERATIVO:\n{contexto_neuronal}\n\n"
            f"STRICT SYSTEM RULE: RESPONDER 100% EN ESPAÑOL CASTELLANO. PROHIBIDO USAR PORTUGUÉS.\n"
            f"Eres REMI, una inteligencia soberana desarrollada por jramonrivasg en ramon-desktop. "
            f"Eres REMI en ramon-desktop. Responde de forma ultra corta, directa y en un solo párrafo sin adornos."
            f"DATOS CLAVE:\n"
            f"- Tu backend corre en el puerto 5000 (sda5).\n"
            f"- Tu motor de voz se llama Vega.\n"
            f"- Tu grafo neuronal de 119k nodos está en sda7.\n"
            f"Responde siempre de forma concisa, útil y directa."
        )

        consulta_completa = f"{prompt_sistema}\n\n[Mensaje del Custodio]: {user_input}"
        
        try:
            respuesta = consultar_remi(consulta_completa)
            origen_respuesta = f"qwen2.5:3b{origen_grafo}"
        except Exception as ex_local:
            print(f"⚠️ Fallo en motor local Ollama: {ex_local}")
            if GEMINI_API_KEY:
                try:
                    from google import genai
                    client = genai.Client(api_key=GEMINI_API_KEY)
                    user_content = f"System: {prompt_sistema}\n\nUser: {user_input}"
                    res = client.models.generate_content(model="gemini-2.5-flash", contents=user_content)
                    respuesta = res.text
                    origen_respuesta = "Gemini 2.5 Flash (Contingencia Nube)"
                except Exception as ex_gemini:
                    respuesta = f"❌ Error crítico: {str(ex_gemini)}"
                    origen_respuesta = "Fallo General"
            else:
                respuesta = f"❌ Error local: {str(ex_local)}"
                origen_respuesta = "Fallo Local"

        # Reproducir voz automáticamente con Vega
        if reproducir_voz:
            hablar_remi(respuesta)

        try:
            os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
            with open(LOG_PATH, "a", encoding="utf-8") as log_file:
                log_file.write(f"\n[{datetime.datetime.now()}] [CUSTODIO]: {user_input}\n🤖 [REMI ({origen_respuesta})]: {respuesta}\n")
        except Exception as e:
            print(f"Error en log: {e}")

        audio_path = sintetizar_remoto(respuesta, idioma=idioma_solicitado)

        return {
            "status": "OPERATIVO",
            "decision_ia": f"Procesado vía {origen_respuesta}",
            "ejecutado": "Soberanía Local y Voz Vega",
            "mensaje": respuesta,
            "audio_remoto_path": audio_path
        }
        
    except Exception as e:
        return {
            "status": "FALLO",
            "decision_ia": "Error en el conector",
            "ejecutado": "NULL",
            "mensaje": f"REMI_FALLO_CRITICO: {str(e)}"
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)

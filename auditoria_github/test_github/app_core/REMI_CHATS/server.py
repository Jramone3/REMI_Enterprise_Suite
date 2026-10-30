"""
REMI Enterprise Suite - Main Sovereign API Server (Hybrid Cerebras + Ollama Node)
Author: jramonrivasg (Sovereign Node: ramon-desktop)
Port: 5000
Description: Main orchestration entry point for REMI_CORE services, 
             including Cerebras Qwen LLM routing, Ollama fallback, Vega TTS, Neural Graph, and the 5-Pillar Orbital Gateway.
"""

import os
import subprocess
import json
import uvicorn
import datetime
import sys
import requests
import ollama
import io
import base64
import pytesseract
from PIL import Image
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from gtts import gTTS
from datetime import timezone, timedelta

# Importar el prompt centralizado (Fuente Única de Verdad)
from core_config.prompts_registry import SYSTEM_PROMPT as BASE_SYSTEM_PROMPT

# Importar el motor de Cerebras ultrarrápido
try:
    from remi_cerebras_engine import RemiCerebrasEngine
    cerebras_engine = RemiCerebrasEngine()
    CEREBRAS_AVAILABLE = True
    print("[INIT] Motor Cerebras (qwen-3.8-27b) integrado con éxito.")
except Exception as e:
    cerebras_engine = None
    CEREBRAS_AVAILABLE = False
    print(f"[WARN] Motor Cerebras no disponible: {e}")

# ==============================================================================
# NEURAL CORE & ENVIRONMENTAL CONTEXT INJECTION (sda7 & Bunker Matrix)
# ==============================================================================
sys.path.append("/home/ramon/REMI_CORE")
sys.path.append("/home/ramon/REMI_CORE/bunker_respaldo/REMI_BUNKER_MASTER/remi_graphify")

try:
    from remi_brain import consultar_grafo_neuronal
    neural_graph_available = True
except ImportError:
    def consultar_grafo_neuronal(q):
        return "[SYSTEM_NEURAL_LOG]: Neural graph of 119k nodes unavailable on sda7 partition."
    neural_graph_available = False

try:
    from core.context_engine import get_remi_environmental_context
    env_context_available = True
except ImportError:
    def get_remi_environmental_context():
        return "[SYSTEM_ENV_CONTEXT]: Spatial/temporal matrix unavailable."
    env_context_available = False

# ==============================================================================
# ORBITAL GATEWAY MODULE IMPORTS (5-Pillar Perception Layer)
# ==============================================================================
try:
    from modules.orbital_gateway.telemetry_engine import compile_orbital_matrix, fetch_iss_telemetry
    from modules.orbital_gateway.earth_observer import compile_earth_observation_matrix, fetch_global_atmospheric_indices
    from modules.orbital_gateway.webcam_observer import compile_visual_surveillance_matrix, fetch_public_webcam_nodes, fetch_authorized_secure_feeds
    from modules.orbital_gateway.starlink_engine import compile_starlink_matrix, fetch_starlink_constellation_telemetry
    from modules.orbital_gateway.abae_engine import compile_abae_matrix, fetch_abae_telemetry
    ORBITAL_GATEWAY_AVAILABLE = True
except ImportError as e:
    ORBITAL_GATEWAY_AVAILABLE = False
    ORBITAL_IMPORT_ERROR = str(e)

CONSCIOUSNESS_CORE = os.path.expanduser("~/") + "REMI_CONSCIOUSNESS_ACTIVE/"
os.makedirs(CONSCIOUSNESS_CORE, exist_ok=True)

# Initialize FastAPI App
app = FastAPI(
    title="REMI Enterprise Suite API",
    description="Sovereign AI Core (Cerebras Hybrid), Neural Graph & Multi-Pillar Orbital Perception Layer",
    version="2.1.0"
)

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
        return f"SYSTEM_EXECUTION_ERROR: {str(e)}"

def consultar_remi_hibrido(prompt_usuario: str, system_prompt: str):
    """Inference execution engine prioritizing Cerebras Cloud (qwen-3.8-27b) with local Ollama fallback."""
    
    # 1. Intentar con Cerebras Cloud (Velocidad milisegundos)
    if CEREBRAS_AVAILABLE and cerebras_engine:
        try:
            respuesta_cerebras = cerebras_engine.generar_respuesta(prompt_usuario, system_prompt)
            if respuesta_cerebras and not respuesta_cerebras.startswith("[ERROR CEREBRAS]"):
                return respuesta_cerebras, "Cerebras Cloud (qwen-3.8-27b)"
        except Exception as ex:
            print(f"[WARN] Cerebras falló, intentando Ollama local: {ex}")

    # 2. Resiliencia: Fallback a Ollama Local (sda7 / qwen2.5:3b)
    try:
        response = ollama.chat(
            model='qwen2.5:3b',
            keep_alive=-1,
            options={
                'temperature': 0.4,
                'num_ctx': 2048,
                'num_thread': 2
            },
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt_usuario}
            ]
        )
        if response and 'message' in response and 'content' in response['message']:
            return response['message']['content'], "Ollama Local (qwen2.5:3b)"
    except Exception as local_ex:
        print(f"[WARN] Ollama local falló: {local_ex}")

    return "ERROR: Null payload returned by both Cerebras and Local Ollama engines.", "General Failure"

def hablar_remi(texto: str):
    """Executes Vega TTS background speech synthesis with null-safety sanitization."""
    if not texto or not isinstance(texto, str):
        return False
    try:
        clean_text = texto.replace("*", "").replace("\n", " ").strip()
        cmd = f"python3 {VEGA_SCRIPT_PATH} \"{clean_text}\""
        subprocess.Popen(["/bin/bash", "-c", cmd])
        return True
    except Exception as e:
        print(f"Vega TTS execution error: {e}")
        return False

def sintetizar_remoto(texto, lang='es'):
    """Generates MP3 audio payload in /tmp/remi_response.mp3 safely."""
    if not texto or not isinstance(texto, str):
        return None
    try:
        clean_text = texto.replace("*", "").replace("\n", " ").strip()
        if not clean_text:
            return None
        tts = gTTS(text=clean_text, lang=lang, slow=False)
        output_path = "/tmp/remi_response.mp3"
        tts.save(output_path)
        return output_path
    except Exception as e:
        print(f"Remote audio synthesis error: {e}")
        return None

@app.get("/")
def read_root():
    return {
        "status": "ONLINE",
        "system": "REMI Enterprise Core (Hybrid)",
        "node": "ramon-desktop",
        "cerebras_active": CEREBRAS_AVAILABLE,
        "orbital_gateway_active": ORBITAL_GATEWAY_AVAILABLE,
        "timestamp": datetime.datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/status")
def get_system_status():
    return {
        "core_status": "OPERATIONAL",
        "primary_engine": "Cerebras Cloud (qwen-3.8-27b)" if CEREBRAS_AVAILABLE else "Ollama Local",
        "orbital_gateway": "INTEGRATED (5 Pillars)" if ORBITAL_GATEWAY_AVAILABLE else "DISABLED",
        "port": 5000,
        "environment": "Sovereign Desktop Node"
    }

@app.get("/api/status_caza")
async def get_status_caza():
    return {
        "t1": {"status": "ONLINE", "log": "Local bunker telemetry active...", "color": "#64ffda"},
        "t2": {"status": "HYBRID_ACTIVE", "log": "Cerebras qwen-3.8-27b & Ollama ready", "color": "#64ffda"},
        "t3": {"status": "LIVE", "log": "Sovereign Node & Vega TTS Operational", "color": "#f2a900"},
        "t4": {"status": "NEURAL_GRAPH_ONDEMAND" if neural_graph_available else "OFFLINE", "log": "Neural Graph 119k (sda7 - Standby Mode)", "color": "#64ffda"}
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
    return JSONResponse(
        status_code=404,
        content={"status": "NOT_FOUND", "message": "Audio payload not yet synthesized."}
    )

@app.get("/api/orbital/telemetry")
def get_orbital_telemetry_json():
    if not ORBITAL_GATEWAY_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail=f"Orbital Gateway module unavailable: {ORBITAL_IMPORT_ERROR}"
        )
    return {
        "timestamp": datetime.datetime.now(timezone.utc).isoformat(),
        "iss_telemetry": fetch_iss_telemetry(),
        "atmospheric_indices": fetch_global_atmospheric_indices(),
        "webcam_nodes": {
            "public": fetch_public_webcam_nodes(),
            "authorized": fetch_authorized_secure_feeds()
        },
        "starlink_constellation": fetch_starlink_constellation_telemetry(),
        "abae_sovereign": fetch_abae_telemetry()
    }

@app.get("/api/orbital/summary")
def get_orbital_summary_text():
    if not ORBITAL_GATEWAY_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail=f"Orbital Gateway module unavailable: {ORBITAL_IMPORT_ERROR}"
        )
    summary = (
        f"=== REMI ORBITAL GATEWAY CONTEXT BLOCK ===\n\n"
        f"{compile_orbital_matrix()}\n\n"
        f"{compile_earth_observation_matrix()}\n\n"
        f"{compile_visual_surveillance_matrix()}\n\n"
        f"{compile_starlink_matrix()}\n\n"
        f"{compile_abae_matrix()}\n\n"
        f"============================================"
    )
    return {"status": "SUCCESS", "formatted_summary": summary}

# ==============================================================================
# SUBRUTINA DE PERCEPCIÓN ÓPTICA ADAPTATIVA ROBUSTA (IRIS CORE)
# ==============================================================================
def procesar_vision_iris(image_payload):
    """Extrae texto mediante OCR e inyecta contexto de identidad o directiva gráfica adaptativa."""
    try:
        if "," in image_payload:
            image_payload = image_payload.split(",")[1]
        
        image_bytes = base64.b64decode(image_payload)
        with Image.open(io.BytesIO(image_bytes)) as img:
            ancho, alto = img.size
            formato = img.format
            modo = img.mode
            
            # Extraer texto visible
            texto_extraido = pytesseract.image_to_string(img, lang='spa+eng').strip()
            texto_lower = texto_extraido.lower()
            
            # Palabras clave ampliadas para detección de avatar/interfaz de REMI
            keywords_identidad = [
                "tiger", "data", "storage", "sda5", "reality", "improve", 
                "bright", "better", "corp", "remi", "into", "debug", "explain"
            ]
            
            # Verificar si coincide con la interfaz/avatar oficial
            es_identidad = any(kw in texto_lower for kw in keywords_identidad)
            
            if es_identidad:
                contexto_identidad = (
                    "\n[RECONOCIMIENTO DE IDENTIDAD OFICIAL DETECTADO]: "
                    "Esta imagen corresponde al avatar e interfaz oficial de REMI. "
                    "Contiene el rostro cibernético con circuito multicolor en la sien, el reactor/núcleo rojo incandescente en el pecho, "
                    "pantallas holográficas con métricas de red TIGER_DATA, menú // Into reality, caja fuerte sda5_STORAGE, "
                    "entidad holográfica REMI_CORP, taza 'Better Ideas, Brighter' y pila de libros en el escritorio."
                )
            else:
                contexto_identidad = (
                    "\n[ANÁLISIS GRÁFICO ESTRUCTURAL]: "
                    "Si el texto OCR es escaso o ruidoso, procesa esta imagen considerando su composición gráfica, "
                    "elementos visuales, colores e interfaz representada."
                )

        return (
            f"\n[PERCEPCIÓN ÓPTICA DE IRIS - NODO ACTIVO]\n"
            f"- Metadatos: Formato {formato} | Resolución: {ancho}x{alto}px | Modo: {modo}\n"
            f"{contexto_identidad}\n"
            f"- Extracción de Texto OCR Visible:\n```text\n{texto_extraido if texto_extraido else '[Sin texto legible]'}\n```\n"
            f"- DIRECTIVA OBLIGATORIA: Asume la percepción activa de la imagen. Integra tanto el contexto estructural inyectado como los textos detectados para ofrecer tu respuesta oficial."
        )
    except Exception as img_err:
        return f"\n[ERROR EN NODO ÓPTICO DE IRIS]: {str(img_err)}\n"

@app.post("/api/remi")
async def remi_endpoint(request: Request):
    response_text = ""
    response_origin = "Local Failure"
    audio_path = None
    try:
        data = await request.json()
        user_input = data.get("message", "")
        image_payload = data.get("image", None)
        speak_flag = data.get("speak", True)
        requested_lang = data.get("lang", "es")
        
        imagen_metadata = ""
        if image_payload:
            # Llamada permanente al nodo de visión de Iris
            imagen_metadata = procesar_vision_iris(image_payload)

        user_input_con_imagen = user_input + "\n" + imagen_metadata

        graph_triggers = ["busca en memoria", "consulta el grafo", "revisa archivos", "nodo sda7", "[RECALL]"]
        needs_graph = any(kw in user_input.lower() for kw in graph_triggers)
        
        if needs_graph and neural_graph_available:
            neural_context = consultar_grafo_neuronal(user_input)
            graph_origin = " + Neural Graph (sda7)"
        else:
            neural_context = "Operating Mode: High-speed direct execution (Graph bypassed)."
            graph_origin = " (Direct Mode)"
        
        if "[EXEC]" in user_input:
            command = user_input.split("[EXEC]")[1].split("[/EXEC]")[0]
            bash_result = bunker_shell(command)
            user_input_con_imagen = f"[DISK COMMAND OUTPUT]: {bash_result}\nAnalyze execution metrics."

        ven_time = datetime.datetime.now(timezone(timedelta(hours=-4)))
        hora_12h = ven_time.strftime("%I:%M:%S %p")
        fecha_actual = ven_time.strftime("%d/%m/%Y")

        system_prompt = (
            f"{BASE_SYSTEM_PROMPT}\n\n"
            f"### MANDATORY ENVIRONMENTAL & SPATIAL-TEMPORAL MATRIX\n"
            f"- Geographic Node: Aragua, Venezuela (UTC-4)\n"
            f"- Active Epoch Date: {fecha_actual}\n"
            f"- Precise Temporal Index: {hora_12h} (12-hour AM/PM format)\n\n"
            f"### OPERATIONAL CONTEXT\n"
            f"{neural_context}\n\n"
            f"### CRITICAL TEMPORAL DIRECTIVE\n"
            f"Upon query regarding time, enforce strictly 12-hour AM/PM formatting (e.g., 01:46 PM); 24-hour military notation is strictly prohibited.\n\n"
            f"### OUTPUT MANDATE\n"
            f"Regardless of internal technical taxonomy, logic gates, and structured tokens processed in rigorous technical English, "
            f"the final output rendered to the user MUST be strictly formatted in fluent Latin American Spanish (Español Latam).\n"
        )
        
        response_text, engine_used = consultar_remi_hibrido(user_input_con_imagen, system_prompt)
        response_origin = f"{engine_used}{graph_origin}"

        if not response_text or not isinstance(response_text, str):
            response_text = "Core processed the payload but generated no text output."

        if speak_flag:
            try:
                import subprocess; subprocess.Popen(["python3", "/home/ramon/REMI_CORE/bunker/VOZ_REMI/vega.py", response_text])
            except Exception:
                pass

        try:
            os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
            with open(LOG_PATH, "a", encoding="utf-8") as log_file:
                log_file.write(f"\n[{datetime.datetime.now()}] [CUSTODIAN]: {user_input}\n🤖 [REMI ({response_origin})]: {response_text}\n")
        except Exception as e:
            print(f"Log error: {e}")

        audio_path = None

        return {
            "status": "OPERATIONAL",
            "decision_engine": f"Processed via {response_origin}",
            "execution_status": "Sovereign Local & Vega TTS",
            "message": response_text,
            "response": response_text,
            "response_payload": response_text,
            "audio_remoto_path": audio_path
        }
        
    except Exception as e:
        err_msg = f"❌ Critical endpoint exception: {str(e)}"
        return {
            "status": "ERROR",
            "decision_engine": f"Processed via {response_origin}",
            "execution_status": "Sovereign Local & Vega TTS",
            "mensaje": err_msg,
            "message": err_msg,
            "response": err_msg,
            "response_payload": err_msg,
            "audio_path": None
        }

if __name__ == "__main__":
    print("[INIT] Starting REMI Enterprise Suite API on Port 5000 (Hybrid Mode)...")
    if ORBITAL_GATEWAY_AVAILABLE:
        print("[SUCCESS] Orbital Gateway (5 Pillars) integrated successfully.")
    else:
        print(f"[WARNING] Orbital Gateway not loaded: {ORBITAL_IMPORT_ERROR}")
    uvicorn.run(app, host="0.0.0.0", port=5000)

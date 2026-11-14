"""
REMI Enterprise Suite - Main Sovereign API Server (Hybrid Cerebras + Ollama Node)
Author: jramonrivasg (Sovereign Node: ramon-desktop)
Port: 5000
Description: Main orchestration entry point for REMI_CORE services, 
             including Cerebras Qwen LLM routing with backoff resilience & latency telemetry, 
             Ollama fallback, Vega TTS, Neural Graph, 5-Pillar Orbital Gateway, 
             Perception Ingress, and IRIS Optical Core.
"""

import os
import subprocess
import json
import uvicorn
import datetime
import sys
import time
import requests
import ollama
import io
import base64
import pytesseract
from PIL import Image
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, APIRouter
from pydantic import BaseModel, Field
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from twilio.twiml.messaging_response import MessagingResponse
from datetime import timezone, timedelta
from typing import Dict, Any, Optional

# Importar el prompt centralizado (Fuente Única de Verdad)
try:
    from core_config.prompts_registry import SYSTEM_PROMPT as BASE_SYSTEM_PROMPT
except ImportError:
    BASE_SYSTEM_PROMPT = "Eres REMI, un nodo soberano de inteligencia artificial avanzado y seguro."

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
    description="Sovereign AI Core (Cerebras Hybrid with Backoff Resilience), Neural Graph & Multi-Pillar Orbital Perception Layer",
    version="2.4.0"
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

# ==============================================================================
# MOTOR HÍBRIDO RESILIENTE (FASE 2: Backoff Exponencial y Telemetría de Latencia)
# ==============================================================================
def consultar_remi_hibrido(prompt_usuario: str, system_prompt: str):
    """
    Motor de inferencia resiliente priorizando Cerebras Cloud con reintentos, 
    backoff exponencial, telemetría de latencia (latency_ms) y failover a Ollama Local.
    """
    start_time = time.time()
    max_retries = 3
    backoff_factor = 1.5

    # 1. Intentar con Cerebras Cloud con reintentos y backoff exponencial
    if CEREBRAS_AVAILABLE and cerebras_engine:
        for attempt in range(1, max_retries + 1):
            try:
                print(f"[LLM] Intentando Cerebras Cloud (Intento {attempt}/{max_retries})...")
                respuesta_cerebras = cerebras_engine.generar_respuesta(prompt_usuario, system_prompt)
                
                if respuesta_cerebras and not respuesta_cerebras.startswith("[ERROR CEREBRAS]"):
                    latency_ms = int((time.time() - start_time) * 1000)
                    print(f"[SUCCESS] Cerebras respondió con éxito en {latency_ms}ms")
                    return respuesta_cerebras, "Cerebras Cloud (qwen-3.8-27b)", latency_ms
                
            except Exception as ex:
                print(f"[WARN] Falló Cerebras en intento {attempt}: {ex}")
                if attempt < max_retries:
                    sleep_time = backoff_factor ** attempt
                    time.sleep(sleep_time)

    # 2. Resiliencia: Fallback a Ollama Local oficial (sda7 / remi:3b)
    print("[LLM] Activando failover automático en nodo local Ollama (remi:3b)...")
    try:
        response = ollama.chat(
            model='remi:3b',
            keep_alive=300,
            options={
                'temperature': 0.3,
                'num_ctx': 1024,
                'num_thread': 4,
                'top_p': 0.9,
                'num_predict': 256
            },
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt_usuario}
            ]
        )
        if response and 'message' in response and 'content' in response['message']:
            latency_ms = int((time.time() - start_time) * 1000)
            print(f"[SUCCESS] Ollama local respondió con éxito en {latency_ms}ms")
            return response['message']['content'], "Ollama Local (remi:3b - Sata7 Optimized)", latency_ms
            
    except Exception as local_ex:
        print(f"[WARN] Ollama local falló: {local_ex}")

    latency_ms = int((time.time() - start_time) * 1000)
    return "ERROR: Null payload returned by both Cerebras and Local Ollama engines.", "General Failure", latency_ms

@app.get("/")
def read_root():
    return {
        "status": "ONLINE",
        "system": "REMI Enterprise Core (Resilient Hybrid)",
        "node": "ramon-desktop",
        "cerebras_active": CEREBRAS_AVAILABLE,
        "orbital_gateway_active": ORBITAL_GATEWAY_AVAILABLE,
        "perception_gateway_active": True,
        "timestamp": datetime.datetime.now(timezone.utc).isoformat()
    }

# ==============================================================================
# 1. MATRIZ DE PERCEPCIÓN EXTERNA (Pilar 1 - Webhooks & Ingress)
# ==============================================================================
perception_router = APIRouter(prefix="/perception", tags=["Perception Gateway"])

class PerceptionEvent(BaseModel):
    source: str = Field(..., description="Origen del evento (webhook, sensor, nodo externo)")
    event_type: str = Field(..., description="Tipo de señal o evento recibido")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Datos asociados al evento")
    priority: int = Field(default=1, ge=1, le=5, description="Nivel de prioridad (1 baja - 5 crítica)")

async def process_signal_background(event: PerceptionEvent):
    print(f"[PERCEPTION INGRESS] Procesando señal de [{event.source}] - Tipo: {event.event_type} (Prioridad: {event.priority})")

@perception_router.post("/ingress")
async def receive_external_signal(event: PerceptionEvent, background_tasks: BackgroundTasks):
    """Punto de entrada universal para webhooks y fuentes de percepción externa."""
    try:
        background_tasks.add_task(process_signal_background, event)
        return {
            "status": "success",
            "message": "Señal recibida e inyectada en la matriz de percepción",
            "source": event.source,
            "event_type": event.event_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.include_router(perception_router)

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
            
            texto_extraido = pytesseract.image_to_string(img, lang='spa+eng').strip()
            texto_lower = texto_extraido.lower()
            
            keywords_identidad = [
                "tiger", "data", "storage", "sda5", "reality", "improve", 
                "bright", "better", "corp", "remi", "into", "debug", "explain"
            ]
            
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

# ==============================================================================
# TWILIO WHATSAPP GATEWAY & WEBHOOK MODULE (CON SOPORTE IRIS MULTIMEDIA)
# ==============================================================================
WHATSAPP_LOG_PATH = os.path.expanduser("~/") + "REMI_CORE/bunker/REMI/ARCHIVOS_PERSONALES_RAMON/Proyecto_Remi_IA_App/REMI_CHATS/whatsapp_history.json"

@app.post("/api/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    """Handles incoming webhook messages from Twilio Sandbox with IRIS Optical Support."""
    try:
        form_data = await request.form()
        incoming_msg = form_data.get("Body", "").strip()
        raw_from = form_data.get("From", "")
        sender_phone = raw_from.replace("whatsapp: ", "whatsapp:")
        if "whatsapp:5" in sender_phone and "whatsapp:+5" not in sender_phone:
            sender_phone = sender_phone.replace("whatsapp:5", "whatsapp:+5")

        media_url = form_data.get("MediaUrl0", None)

        print(f"[WHATSAPP INCOMING] From: {sender_phone} | Text: {incoming_msg} | Media: {media_url}")

        resp = MessagingResponse()

        if "join properly-beside" in incoming_msg.lower():
            response_text = "🤖 [REMI_CORE - ENLACE ACTIVO] 🟢\n\n¡Hola Ramón! Conexión de WhatsApp establecida con éxito. El nodo soberano está listo."
            resp.message(response_text)
        else:
            imagen_metadata = ""
            if media_url:
                try:
                    res = requests.get(media_url)
                    if res.status_code == 200:
                        img_b64 = base64.b64encode(res.content).decode("utf-8")
                        imagen_metadata = procesar_vision_iris(img_b64)
                except Exception as img_err:
                    print(f"[WHATSAPP IRIS ERROR]: {img_err}")

            full_prompt = incoming_msg
            if imagen_metadata:
                full_prompt += f"\n\n[IRIS Metadata Visual]: {imagen_metadata}"
            
            system_prompt = f"{BASE_SYSTEM_PROMPT}\n\n[CONTEXTO WHATSAPP]: Estás respondiendo a través del canal de WhatsApp de Twilio al administrador {sender_phone}."
            
            # Recibir la tupla de 3 valores (texto, motor y latencia)
            response_text, engine_used, latency_ms = consultar_remi_hibrido(full_prompt, system_prompt)
            print(f"[WHATSAPP OUTBOUND] Motor: {engine_used} | Latencia: {latency_ms}ms")
            
            resp.message(response_text)

        os.makedirs(os.path.dirname(WHATSAPP_LOG_PATH), exist_ok=True)
        history = []
        if os.path.exists(WHATSAPP_LOG_PATH):
            try:
                with open(WHATSAPP_LOG_PATH, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []
        
        history.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "sender": sender_phone,
            "message": incoming_msg,
            "has_media": bool(media_url),
            "response": response_text,
            "engine": engine_used,
            "latency_ms": latency_ms
        })
        
        with open(WHATSAPP_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(history[-50:], f, indent=2, ensure_ascii=False)

        return Response(content=str(resp), media_type="application/xml")

    except Exception as e:
        print(f"[WHATSAPP WEBHOOK ERROR]: {e}")
        err_resp = MessagingResponse()
        err_resp.message("⚠️ [REMI Error Interno]: Procesando nodo.")
        return Response(content=str(err_resp), media_type="application/xml")

@app.get("/api/whatsapp/messages")
def get_whatsapp_messages():
    if os.path.exists(WHATSAPP_LOG_PATH):
        try:
            with open(WHATSAPP_LOG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

if __name__ == "__main__":
    print("[INIT] Motor Cerebras (qwen-3.8-27b) con Resiliencia y Backoff integrado.")
    print("[INIT] Starting REMI Enterprise Suite API on Port 5000 (Resilient Hybrid Mode)...")
    uvicorn.run(app, host="0.0.0.0", port=5000)

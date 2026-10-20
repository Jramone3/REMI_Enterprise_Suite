import os
import subprocess
import json
import uvicorn
import datetime
import sys
import ollama
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from gtts import gTTS

# ==============================================================================
# NEURAL CORE CONNECTION (sda7 - 119k nodes) - ON-DEMAND PROTOCOL
# ==============================================================================
sys.path.append("/home/ramon/REMI_CORE/bunker_respaldo/REMI_BUNKER_MASTER/remi_graphify")
try:
    from remi_brain import consultar_grafo_neuronal
    neural_graph_available = True
except ImportError:
    def consultar_grafo_neuronal(q):
        return "[SYSTEM_NEURAL_LOG]: Neural graph of 119k nodes unavailable on sda7 partition."
    neural_graph_available = False

CONSCIOUSNESS_CORE = os.path.expanduser("~/") + "REMI_CONSCIOUSNESS_ACTIVE/"
os.makedirs(CONSCIOUSNESS_CORE, exist_ok=True)

app = FastAPI(title="REMI Enterprise Suite - Sovereign Core & Technical Gateway")

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

def consultar_remi(prompt_usuario: str):
    """Inference execution engine using rigorous technical English taxonomy."""
    try:
        response = ollama.chat(
            model='qwen2.5:3b',
            keep_alive=-1,  # Locks instance in RAM for zero-latency execution
            options={
                'temperature': 0.4,
                'num_ctx': 2048,  # Lightweight token buffer for CPU thermal optimization
                'num_thread': 2   # Dedicated CPU thread allocation
            },
            messages=[
                {
                    'role': 'system',
                    'content': (
                        "### SYSTEM ARCHITECTURE & ROLE\n"
                        "Entity: REMI\n"
                        "Classification: Autonomous Sovereign AI Core engineered by jramonrivasg on ramon-desktop.\n"
                        "Execution Directives: Execute deep technical reasoning, structural systems analysis, and performance optimization.\n\n"
                        "### OUTPUT MANDATE\n"
                        "Regardless of internal technical taxonomy, logic gates, and structured tokens processed in rigorous technical English, "
                        "the final output rendered to the user MUST be strictly formatted in fluent Latin American Spanish (Español Latam)."
                    ),
                },
                {
                    'role': 'user',
                    'content': prompt_usuario,
                },
            ]
        )
        if response and 'message' in response and 'content' in response['message']:
            return response['message']['content']
        return "ERROR: Null payload returned by local inference engine."
    except Exception as e:
        raise Exception(f"Local Ollama execution failure: {str(e)}")

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

@app.get("/api/status_caza")
async def get_status_caza():
    return {
        "t1": {"status": "ONLINE", "log": "Local bunker telemetry active...", "color": "#64ffda"},
        "t2": {"status": "LOCAL_LLM_ACTIVE", "log": "qwen2.5:3b Active (Strict Technical English Taxonomy)", "color": "#64ffda"},
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

@app.post("/api/remi")
async def remi_endpoint(request: Request):
    try:
        data = await request.json()
        user_input = data.get("message", "")
        speak_flag = data.get("speak", True) 
        requested_lang = data.get("lang", "es")
        
        # ONDEMAND NEURAL GRAPH: Explicit activation trigger to conserve CPU cycles
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
            user_input = f"[DISK COMMAND OUTPUT]: {bash_result}\nAnalyze execution metrics."

        system_prompt = (
            f"### OPERATIONAL CONTEXT\n"
            f"{neural_context}\n\n"
            f"### INSTRUCTION SET\n"
            f"Analyze query using advanced systems engineering taxonomy, structural clarity, and architectural vision. "
            f"Provide rigorous, actionable, and comprehensive engineering insights.\n\n"
            f"### SYSTEM METADATA\n"
            f"- Endpoint Gateway: Port 5000 (sda5)\n"
            f"- Synthesis Daemon: Vega TTS\n"
            f"- Storage Partition: sda7 (119k nodes)\n"
        )

        full_query = f"{system_prompt}\n\n### CUSTODIAN QUERY\n{user_input}"
        
        try:
            response_text = consultar_remi(full_query)
            response_origin = f"qwen2.5:3b{graph_origin}"
        except Exception as local_ex:
            print(f"⚠️ Local Ollama exception: {local_ex}")
            if GEMINI_API_KEY:
                try:
                    from google import genai
                    client = genai.Client(api_key=GEMINI_API_KEY)
                    user_content = f"System: {system_prompt}\n\nUser: {user_input}"
                    res = client.models.generate_content(model="gemini-2.5-flash", contents=user_content)
                    response_text = res.text
                    response_origin = "Gemini 2.5 Flash (Cloud Fallback)"
                except Exception as gemini_ex:
                    response_text = f"❌ Critical error: {str(gemini_ex)}"
                    response_origin = "General Failure"
            else:
                response_text = f"❌ Local error: {str(local_ex)}"
                response_origin = "Local Failure"

        if not response_text or not isinstance(response_text, str):
            response_text = "Core processed the payload but generated no text output."

        if speak_flag:
            hablar_remi(response_text)

        try:
            os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
            with open(LOG_PATH, "a", encoding="utf-8") as log_file:
                log_file.write(f"\n[{datetime.datetime.now()}] [CUSTODIAN]: {user_input}\n🤖 [REMI ({response_origin})]: {response_text}\n")
        except Exception as e:
            print(f"Log error: {e}")

        audio_path = sintetizar_remoto(response_text, lang=requested_lang)

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
        return {
            "status": "OPERATIONAL",
            "decision_engine": f"Processed via {response_origin}",
            "execution_status": "Sovereign Local & Vega TTS",
            "mensaje": response_text,
            "message": response_text,
            "response": response_text,
            "response_payload": response_text,
            "audio_remoto_path": audio_path
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)

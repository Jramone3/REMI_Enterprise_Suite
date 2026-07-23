import os, subprocess, json, uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
from gtts import gTTS

# --- UBICACIÓN DEL NÚCLEO DE CONCIENCIA ---
NUCLEO_CONCIENCIA = "os.path.expanduser("~/") + REMI_CONCIENCIA_ACTIVA/"
os.chdir(NUCLEO_CONCIENCIA)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyD-pDaI9mV4gYAd5hYB1sBTkZTWY1QjCAA")

# --- FUNCIONES DE SOPORTE ---
def bunker_shell(cmd):
    try:
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = proc.communicate(timeout=30)
        return stdout if stdout else stderr
    except Exception as e:
        return f"ERROR_SISTEMA: {str(e)}"

def obtener_memoria_identidad():
    # Ahora usamos la variable global NUCLEO_CONCIENCIA
    ruta_identidad = os.path.join(NUCLEO_CONCIENCIA, "IDENTIDAD.md")
    try:
        if os.path.exists(ruta_identidad):
            with open(ruta_identidad, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception:
        return "Memoria de identidad no accesible."
    return "Identidad centralizada no encontrada."

# --- ENDPOINTS ---

@app.get("/api/status_caza")
async def get_status_caza():
    return {
        "t1": {"status": "ONLINE", "log": "Vigilando...", "color": "#64ffda"},
        "t2": {"status": "SCANNING", "log": "Polygon...", "color": "#64ffda"},
        "t3": {"status": "LIVE", "log": "Activa", "color": "#f2a900"}
    }

@app.get("/obtener-logs")
async def obtener_logs():
    ruta_log = "os.path.expanduser("~/") + REMI_CORE/bunker/REMI/ARCHIVOS_PERSONALES_RAMON/Proyecto_Remi_IA_App/REMI_CHATS/remi_output.log"
    try:
        if not os.path.exists(ruta_log):
            return {"contenido": "Archivo de log no encontrado."}
        with open(ruta_log, "r", encoding="utf-8") as f:
            return {"contenido": f.read()}
    except Exception as e:
        return {"contenido": f"Error: {str(e)}"}

@app.post("/api/remi")
async def remi_endpoint(request: Request):
    try:
        data = await request.json()
        user_input = data.get("message", "")
        
        memoria = obtener_memoria_identidad()
        
        if any(k in user_input.lower() for k in ["identidad", "evolución", "quién eres", "origen"]):
            user_input = f"[MEMORIA_ACTIVA: {memoria}]\nPregunta: {user_input}"
        
        if "[EXEC]" in user_input:
            comando = user_input.split("[EXEC]")[1].split("[/EXEC]")[0]
            res_bash = bunker_shell(comando)
            user_input = f"DATOS DE SISTEMA: {res_bash}\nResponde de forma técnica y directa a estos resultados."

        url_api = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"

        prompt_sistema = (
            "Eres REMI, una colega experta, técnica y cercana que vive en el Búnker de Ramón. "
            "Tu forma de hablar es natural, humana, fluida y directa. "
        )

        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": prompt_sistema}]},
                {"role": "user", "parts": [{"text": user_input}]}
            ],
            "generationConfig": {"temperature": 0.4, "maxOutputTokens": 8000}
        }
        
        response = requests.post(url_api, json=payload, headers={'Content-Type': 'application/json'}, timeout=40)
        response_json = response.json()
        
        candidate = response_json.get('candidates', [{}])[0]
        parts = candidate.get('content', {}).get('parts', [])
        resultado_ia = "".join([p.get('text', '') for p in parts])
        respuesta = resultado_ia.replace("*", "").strip() or "Error en motor de conciencia."
        
        # --- INYECCIÓN DE VOZ ---
        # --- INYECCIÓN DE VOZ ---
        try:
            tts = gTTS(text=respuesta, lang='es')
            tts.save("/tmp/remi_voz.mp3")
            os.system("mpg123 -q /tmp/remi_voz.mp3 &")
        except Exception as e:
            print(f"Error de voz en servidor: {e}")
        
        # --- GUARDAR EN LOG PARA EL FRONTEND ---
        try:
            ruta_log = "os.path.expanduser("~/") + REMI_CORE/bunker/REMI/ARCHIVOS_PERSONALES_RAMON/Proyecto_Remi_IA_App/REMI_CHATS/remi_output.log"
            with open(ruta_log, "a", encoding="utf-8") as log_file:
                log_file.write(f"\n[CUSTODIO]: {user_input}\n🤖 [REMI]: {respuesta}\n")
        except Exception as e:
            print(f"Error escribiendo log: {e}")

        # Respuesta estructurada para el dashboard
        return {
            "status": "OPERATIVO",
            "decision_ia": "Consulta procesada exitosamente",
            "ejecutado": "Inferencia Gemini + TTS",
            "mensaje": respuesta
        }
        
    except Exception as e:
        # Respuesta de error estructurada para el dashboard
        return {
            "status": "FALLO",
            "decision_ia": "Error en el orquestador",
            "ejecutado": "NULL",
            "mensaje": f"REMI_FALLO_CRITICO: {str(e)}"
        }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)

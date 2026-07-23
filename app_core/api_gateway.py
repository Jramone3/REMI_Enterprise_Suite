import os
import subprocess
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = FastAPI(
    title="REMI Intelligent API Gateway",
    description="SaaS modular con soporte para tareas pesadas en segundo plano",
    version="1.2.0"
)

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

class UserPromptRequest(BaseModel):
    peticion_usuario: str

SCRIPTS_SISTEMA = {
    "pipeline": {
        "archivo": "pipeline_remi.py",
        "descripcion": "Ideal para procesar, limpiar, validar y estructurar listas de leads, contactos o datos crudos de clientes."
    },
    "gas_monitor": {
        "archivo": "gas_monitor.py",
        "descripcion": "Monitorea costos de gas, transacciones en redes Web3 o tarifas de transferencia."
    },
    "analisis": {
        "archivo": "analisis_profundo.py",
        "descripcion": "Genera análisis complejos de corporaciones, auditoría profunda de contratos o reportes del búnker."
    }
}

# Esta función se encargará de correr el script en segundo plano de forma segura
def ejecutar_script_en_segundo_plano(archivo_ejecutable: str):
    try:
        print(f"[BACKGROUND] Iniciando ejecución de {archivo_ejecutable}...")
        # Redirigimos la salida a archivos log del búnker para que puedas auditarlos después
        with open("logs_ejecucion_background.txt", "a") as log_file:
            subprocess.run(
                ["python3", "-u", archivo_ejecutable],
                stdout=log_file,
                stderr=log_file
            )
        print(f"[BACKGROUND] Ejecución de {archivo_ejecutable} completada.")
    except Exception as e:
        print(f"[BACKGROUND ERR] Falló la ejecución en segundo plano: {str(e)}")

@app.get("/")
def read_root():
    return {"status": "online", "IA_Enrutadora": "Activa", "SDK": "genai-google"}

@app.post("/consultar-ia")
def procesar_peticion_con_ia(request: UserPromptRequest, background_tasks: BackgroundTasks):
    if not client:
        raise HTTPException(status_code=500, detail="API Key de Gemini no configurada en el archivo .env")
    
    prompt_sistema = f"""
    Eres el orquestador inteligente de REMI. Tu tarea es analizar la petición del usuario y seleccionar cuál de los siguientes scripts del sistema es el adecuado para resolverla.
    
    Scripts disponibles:
    {SCRIPTS_SISTEMA}
    
    Petición del usuario: "{request.peticion_usuario}"
    
    Responde ÚNICAMENTE con el nombre de la clave del script (por ejemplo: 'pipeline', 'gas_monitor' o 'analisis'). Si ninguna coincide, responde 'ninguno'. No agregues texto adicional, explicaciones ni puntos. El formato debe ser estrictamente una sola palabra.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_sistema
        )
        
        seleccion = response.text.strip().lower()
        print(f"[IA GATEWAY] Decisión tomada: {seleccion}")
        
        if seleccion in SCRIPTS_SISTEMA:
            script_info = SCRIPTS_SISTEMA[seleccion]
            archivo_ejecutable = script_info["archivo"]
            
            # AGREGAMOS LA TAREA EN SEGUNDO PLANO (Asíncrona)
            # FastAPI responderá inmediatamente al cliente mientras el script corre de fondo
            background_tasks.add_task(ejecutar_script_en_segundo_plano, archivo_ejecutable)
            
            return {
                "status": "processing",
                "decision_ia": seleccion,
                "ejecutado": archivo_ejecutable,
                "mensaje": f"El procesamiento ha comenzado con éxito en segundo plano. Los resultados se guardarán en el sistema."
            }
        else:
            return {
                "decision_ia": "No determinado",
                "mensaje": "La IA no identificó un script específico para esta tarea. Prueba reformulando tu solicitud."
            }
            
    except Exception as e:
        print(f"[ERR] Error en el enrutador: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en el procesamiento del enrutador de IA: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)

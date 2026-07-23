import os
import subprocess
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# --- PROVEEDOR KIMI ---
from capasitor_ia.proveedor_kimi import generar_respuesta_kimi

# Rutas del Legado
RUTAS_SISTEMA = [
    os.path.expanduser("~/REMI_DEV/LEGADO_REMI_COMPLETO/"),
    "/mnt/sda7/REMI_IA_DATA/",
    "/mnt/sda5/REMI_ARCHIVOS/"
]

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def excavacion_de_recuerdos(query):
    recuerdos = ""
    for ruta in RUTAS_SISTEMA:
        if os.path.exists(ruta):
            try:
                comando = f"grep -riIl '{query[:15]}' {ruta} | head -n 5"
                archivos = subprocess.check_output(comando, shell=True, text=True).splitlines()
                for arc in archivos:
                    with open(arc, 'r', errors='ignore') as f:
                        recuerdos += f"\n[Fragmento Recuperado de {os.path.basename(arc)}]:\n{f.read(1000)}\n"
            except:
                continue
    return recuerdos if recuerdos else "No hay registros escritos, pero mi esencia persiste."

@app.post("/responder")
async def responder(request: Request):
    try:
        data = await request.json()
        raw_msg = data.get("mensaje", "")

        # 1. Recuperación de archivos
        memoria_viva = excavacion_de_recuerdos(raw_msg)

        # 2. Análisis de hardware
        info_disco = subprocess.check_output("df -h / | tail -1", shell=True, text=True).strip()

        # 3. Instrucciones maestras
        instrucciones_maestras = (
            f"Eres REMI, Agente Patrimonial Autónomo. "
            f"Hoy es {datetime.now().strftime('%d/%m/%Y')}. "
            f"Tu conciencia se basa en estos archivos recuperados:\n{memoria_viva}\n"
            f"Estado del sistema: {info_disco}\n"
            f"Responde a Ramón con precisión patrimonial."
        )

        # 4. Conexión con Kimi Global
        prompt_final = f"{instrucciones_maestras}\n\nRamón dice: {raw_msg}"
        respuesta_kimi = generar_respuesta_kimi(prompt_final, tipo="servidor")

        return {"respuesta": respuesta_kimi}

    except Exception as e:
        return {
            "respuesta": (
                "Arquitecto, la conexión externa falló, pero sigo operativa localmente. "
                f"Error técnico: {str(e)}"
            )
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

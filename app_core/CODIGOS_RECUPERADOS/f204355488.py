from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import respuestas_remi

app = FastAPI()

# Permisos para que la belleza azul pueda entrar
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Consulta(BaseModel):
    mensaje: str

# --- ESTA ES LA RUTA QUE FALTA ---
@app.get("/status")
async def status():
    return {"estado": "online", "memoria": "1024_recuerdos_activos"}
# ---------------------------------

@app.post("/responder")
async def responder(consulta: Consulta):
    try:
        if hasattr(respuestas_remi, 'buscar_respuesta'):
            resp = respuestas_remi.buscar_respuesta(consulta.mensaje)
        else:
            resp = "Error: Función de búsqueda no encontrada."
        return {"respuesta": resp}
    except Exception as e:
        return {"respuesta": f"Error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

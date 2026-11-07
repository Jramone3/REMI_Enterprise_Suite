from fastapi import FastAPI
import os
import uvicorn

app = FastAPI(
    title="REMI Enterprise Suite - WhatsApp & Webhook Gateway",
    version="2.0.1"
)

try:
    from core.twilio_router import router as twilio_router
    app.include_router(twilio_router)
    print("[INFO] Router de Twilio cargado exitosamente.")
except Exception as e:
    print(f"[WARNING] No se pudo cargar el router de Twilio: {e}")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": "REMI_Enterprise_Suite Backend",
        "webhook_endpoint": "/api/v1/webhook"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("main_api:app", host="0.0.0.0", port=port)

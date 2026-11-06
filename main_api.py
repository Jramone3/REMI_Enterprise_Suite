from fastapi import FastAPI
from core.twilio_router import router as twilio_router

app = FastAPI(
    title="REMI Enterprise Suite - WhatsApp & Webhook Gateway",
    version="2.0.0"
)

app.include_router(twilio_router)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": "REMI_Enterprise_Suite Backend",
        "webhook_endpoint": "/api/v1/webhook"
    }

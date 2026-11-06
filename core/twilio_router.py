cat << 'EOF' > core/twilio_router.py
from fastapi import APIRouter, Form, Response
from pydantic import BaseModel, Field
from typing import Optional
import datetime
import requests
import os

router = APIRouter(prefix="/api/v1", tags=["Twilio WhatsApp"])

class TwilioInboundWebhook(BaseModel):
    From: str = Field(..., max_length=140)
    To: str = Field(..., max_length=140)
    Body: Optional[str] = ""
    MessageSid: Optional[str] = None
    AccountSid: Optional[str] = None
    
    # Soporte BSUID (WhatsApp Usernames - Junio 2026)
    ExternalUserId: Optional[str] = Field(None, max_length=140)
    ParentExternalUserId: Optional[str] = Field(None, max_length=140)

    @property
    def identity(self) -> str:
        return self.ExternalUserId or self.From

@router.post("/webhook")
async def receive_whatsapp_message(
    From: str = Form(...),
    To: str = Form(...),
    Body: Optional[str] = Form(""),
    MessageSid: Optional[str] = Form(None),
    AccountSid: Optional[str] = Form(None),
    ExternalUserId: Optional[str] = Form(None),
    ParentExternalUserId: Optional[str] = Form(None)
):
    payload = TwilioInboundWebhook(
        From=From,
        To=To,
        Body=Body,
        MessageSid=MessageSid,
        AccountSid=AccountSid,
        ExternalUserId=ExternalUserId,
        ParentExternalUserId=ParentExternalUserId
    )
    
    user_id = payload.identity
    user_message = payload.Body or ""
    print(f"[{datetime.datetime.now()}] Mensaje recibido de {user_id}: {user_message}")
    
    # Generamos la respuesta inteligente (puedes conectar tu lógica de Ollama o una respuesta dinámica de REMI)
    remi_reply = f"Hola Ramón, recibí tu mensaje: '{user_message}'. REMI_Enterprise_Suite online y operando con soporte BSUID 2026."

    # Construimos la respuesta oficial en TwiML que Twilio lee para responder al usuario en WhatsApp
    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{remi_reply}</Message>
</Response>"""
    
    return Response(content=twiml_response, media_type="application/xml")

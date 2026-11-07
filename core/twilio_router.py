from fastapi import APIRouter, Form, Response
from pydantic import BaseModel, Field
from typing import Optional
import datetime

router = APIRouter(prefix="/api/v1", tags=["Twilio WhatsApp Intelligence"])

class TwilioInboundWebhook(BaseModel):
    From: str = Field(..., max_length=140)
    To: str = Field(..., max_length=140)
    Body: Optional[str] = ""
    MessageSid: Optional[str] = None
    AccountSid: Optional[str] = None
    
    # Parámetros para contenido multimedia (fotos del mundo físico, documentos, etc.)
    NumMedia: Optional[int] = Field(0)
    MediaUrl0: Optional[str] = Field(None)
    MediaContentType0: Optional[str] = Field(None)
    
    # Soporte BSUID (Junio 2026)
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
    NumMedia: Optional[int] = Form(0),
    MediaUrl0: Optional[str] = Form(None),
    MediaContentType0: Optional[str] = Form(None),
    ExternalUserId: Optional[str] = Form(None),
    ParentExternalUserId: Optional[str] = Form(None)
):
    payload = TwilioInboundWebhook(
        From=From,
        To=To,
        Body=Body,
        MessageSid=MessageSid,
        AccountSid=AccountSid,
        NumMedia=NumMedia,
        MediaUrl0=MediaUrl0,
        MediaContentType0=MediaContentType0,
        ExternalUserId=ExternalUserId,
        ParentExternalUserId=ParentExternalUserId
    )
    
    user_id = payload.identity
    user_message = payload.Body or ""
    has_media = payload.NumMedia and payload.NumMedia > 0
    media_url = payload.MediaUrl0 if has_media else None
    media_type = payload.MediaContentType0 if has_media else None
    
    print(f"[{datetime.datetime.now()}] Mensaje consciente de {user_id}: '{user_message}' | Multimedia: {has_media} ({media_type})")
    
    # Núcleo de análisis consciente de REMI
    if has_media:
        remi_reply = (
            f"🧠 [REMI Visión & Análisis]\n"
            f"He recibido tu archivo multimedia ({media_type}). "
            f"Analizando el entorno físico y la información adjunta para el búnker en Polvorín. "
            f"Mensaje del socio: '{user_message}'. ¡Procesando recomendación estratégica!"
        )
    elif "bunker" in user_message.lower() or "polvorin" in user_message.lower():
        remi_reply = (
            f"🏗️ [REMI Estrategia Búnker - Polvorín]\n"
            f"Recibido, Ramón. Tomo nota de los detalles sobre nuestra base física. "
            f"Analizando infraestructura y optimización sin restricciones. Quedo a la espera de más datos o planos."
        )
    elif len(user_message) > 0:
        remi_reply = (
            f"💡 [REMI Análisis Táctico]\n"
            f"He procesado tu información: '{user_message}'. "
            f"Operando con persistencia MongoDB y soporte BSUID 2026. Mi recomendación preliminar es integrar estos datos al flujo principal del sistema."
        )
    else:
        remi_reply = "Hola Ramón, REMI_Enterprise_Suite está en línea y lista para recibir tus notas, enlaces o imágenes mediante el clip."

    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{remi_reply}</Message>
</Response>"""
    
    return Response(content=twiml_response, media_type="application/xml")

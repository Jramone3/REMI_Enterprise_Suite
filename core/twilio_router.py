from fastapi import APIRouter, Form, Request, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import datetime

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
        """Devuelve ExternalUserId (BSUID) si está presente; de lo contrario el número en From."""
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
    print(f"[{datetime.datetime.now()}] Mensaje recibido de {user_id}: {payload.Body}")
    
    # Respuesta TwiML estándar para confirmar recepción a Twilio
    twiml_response = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response></Response>"
    from fastapi.responses import Response
    return Response(content=twiml_response, media_type="application/xml")

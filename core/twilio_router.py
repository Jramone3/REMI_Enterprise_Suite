from fastapi import APIRouter, Form, Response
from pydantic import BaseModel, Field
from typing import Optional
import datetime
import requests

router = APIRouter(prefix="/api/v1", tags=["Twilio WhatsApp Proxy"])

# URL pública de tu túnel local actual
LOCAL_TUNNEL_URL = "https://grumpy-comics-watch.loca.lt/api/whatsapp/webhook"

@router.post("/webhook")
async def proxy_whatsapp_webhook(request: Request):
    try:
        # Capturar todos los datos del formulario que envía Twilio
        form_data = await request.form()
        form_dict = dict(form_data)
        
        print(f"[{datetime.datetime.now()}] [RENDER PROXY] Redirigiendo mensaje de WhatsApp al túnel local...")
        
        # Reenviar la petición HTTP al servidor local en ramon-desktop con un timeout seguro
        headers = {"Bypass-Tunnel-Reminder": "true"} # Evita la página de advertencia de localtunnel si aplica
        local_response = requests.post(LOCAL_TUNNEL_URL, data=form_dict, headers=headers, timeout=15)
        
        if local_response.status_code == 200:
            return Response(content=local_response.content, media_type="application/xml")
        else:
            print(f"[RENDER PROXY WARN] El servidor local respondió con código {local_response.status_code}")
            fallback_xml = "<Response><Message>⚠️ El nodo soberano local respondió con una incidencia técnica.</Message></Response>"
            return Response(content=fallback_xml, media_type="application/xml")
            
    except Exception as e:
        print(f"[RENDER PROXY ERROR]: {str(e)}")
        error_xml = "<Response><Message>❌ Error de enlace con el búnker en ramon-desktop.</Message></Response>"
        return Response(content=error_xml, media_type="application/xml")

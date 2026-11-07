from fastapi import APIRouter, Request, Response
import datetime
import requests

router = APIRouter(prefix="/api/v1", tags=["Twilio WhatsApp Proxy"])

# URL fija de tu túnel local en localtunnel
LOCAL_TUNNEL_URL = "https://remi-bunker-node.loca.lt/api/whatsapp/webhook"

@router.post("/webhook")
async def proxy_whatsapp_webhook(request: Request):
    try:
        form_data = await request.form()
        form_dict = dict(form_data)
        
        print(f"[{datetime.datetime.now()}] [RENDER PROXY] Reenviando a túnel fijo: {LOCAL_TUNNEL_URL}")
        
        headers = {"Bypass-Tunnel-Reminder": "true"}
        local_response = requests.post(LOCAL_TUNNEL_URL, data=form_dict, headers=headers, timeout=20)
        
        if local_response.status_code == 200:
            return Response(content=local_response.content, media_type="application/xml")
        else:
            print(f"[RENDER PROXY WARN] Respuesta local código {local_response.status_code}")
            fallback_xml = "<Response><Message>⚠️ Nodo local respondió con incidencia técnica.</Message></Response>"
            return Response(content=fallback_xml, media_type="application/xml")
            
    except Exception as e:
        print(f"[RENDER PROXY ERROR]: {str(e)}")
        error_xml = "<Response><Message>❌ Error de enlace con ramon-desktop.</Message></Response>"
        return Response(content=error_xml, media_type="application/xml")

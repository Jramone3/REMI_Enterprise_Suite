with open("server.py", "r", encoding="utf-8") as f:
    code = f.read()

new_webhook = '''@app.post("/api/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    """Handles incoming webhook messages from Twilio Sandbox with IRIS Optical Support."""
    try:
        form_data = await request.form()
        incoming_msg = form_data.get("Body", "").strip()
        sender_phone = form_data.get("From", "")
        media_url = form_data.get("MediaUrl0", None)

        print(f"[WHATSAPP INCOMING] From: {sender_phone} | Text: {incoming_msg} | Media: {media_url}")

        imagen_metadata = ""
        if media_url:
            try:
                # Descargar imagen desde Twilio e integrarla a IRIS
                res = requests.get(media_url)
                if res.status_code == 200:
                    img_b64 = base64.b64encode(res.content).decode("utf-8")
                    imagen_metadata = procesar_vision_iris(img_b64)
            except Exception as img_err:
                print(f"[WHATSAPP IRIS ERROR]: {img_err}")

        # 1. Detección del comando de enlace de Twilio Sandbox
        if "join properly-beside" in incoming_msg.lower():
            response_text = "🤖 [REMI_CORE - ENLACE ACTIVO] 🟢\\n\\n¡Hola Ramón! Conexión de WhatsApp establecida con éxito. El nodo soberano está listo."
        else:
            prompt_final = incoming_msg + ("\\n" + imagen_metadata if imagen_metadata else "")
            system_prompt = f"{BASE_SYSTEM_PROMPT}\\n\\n[CONTEXTO WHATSAPP]: Estás respondiendo a través del canal de WhatsApp de Twilio al administrador {sender_phone}."
            response_text, engine_used = consultar_remi_hibrido(prompt_final, system_prompt)

        # 3. Guardar en el historial local del búnker
        os.makedirs(os.path.dirname(WHATSAPP_LOG_PATH), exist_ok=True)
        history = []
        if os.path.exists(WHATSAPP_LOG_PATH):
            try:
                with open(WHATSAPP_LOG_PATH, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []
        
        history.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "sender": sender_phone,
            "message": incoming_msg,
            "has_media": bool(media_url),
            "response": response_text
        })
        
        with open(WHATSAPP_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(history[-50:], f, indent=2, ensure_ascii=False)

        # Retornar respuesta XML compatible con Twilio (TwiML)
        from fastapi.responses import Response
        twiml_response = f"""<Response><Message>{response_text}</Message></Response>"""
        return Response(content=twiml_response, media_type="application/xml")

    except Exception as e:
        print(f"[WHATSAPP ERROR]: {e}")
        from fastapi.responses import Response
        return Response(content="<Response><Message>❌ Error procesando el mensaje en el Búnker.</Message></Response>", media_type="application/xml")'''

# Reemplazar el webhook viejo por el nuevo
split_tag = '@app.post("/api/whatsapp/webhook")'
if split_tag in code:
    base_code = code.split(split_tag)[0]
    # Mantener el endpoint de /api/whatsapp/messages al final
    after_code = code.split('@app.get("/api/whatsapp/messages")')[1]
    final_code = base_code + new_webhook + '\n\n@app.get("/api/whatsapp/messages")' + after_code
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(final_code)
    print("✅ server.py actualizado exitosamente con soporte IRIS para WhatsApp.")
else:
    print("❌ No se encontró la etiqueta del webhook en server.py")

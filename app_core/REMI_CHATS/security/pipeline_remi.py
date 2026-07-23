import sys
import requests
import json
import subprocess
import os

mensaje = sys.argv[1].lower()

# ✅ Cargar configuración desde remi.config.js
def cargar_config():
    try:
        # Usamos node para evaluar el archivo JS y devolver JSON
        result = subprocess.run(
            ["node", "-e", "import('./remi.config.js').then(m=>console.log(JSON.stringify(m.REMI_CONFIG)))"],
            capture_output=True, text=True, cwd=os.path.dirname(__file__)
        )
        if result.returncode == 0:
            return json.loads(result.stdout.strip())
        else:
            print("Error cargando configuración:", result.stderr)
            return {}
    except Exception as e:
        print("No se pudo cargar remi.config.js:", e)
        return {}

CONFIG = cargar_config()

NUCLEO_URL = CONFIG.get("flaskUrl", "http://localhost:5000/api/ia")
ENDPOINTS = CONFIG.get("endpoints", {})
ESTILO = CONFIG.get("estilo", {"firma": "REMI responde con voz patrimonial"})

def respuestas_estaticas(mensaje):
    if "copilot" in mensaje:
        return "Copilot es un compañero de IA creado por Microsoft. Te ayuda a aprender, automatizar y crear."
    elif "ramon" in mensaje:
        return "Ramón Rivas es el custodio de REMI, arquitecto del entorno MintBridge XFCE v_1.0."
    elif "remi" in mensaje and "sabe" in mensaje:
        return "REMI puede monitorear, registrar, comparar huellas, exportar datos y publicar verificaciones."
    elif "remi" in mensaje:
        return "REMI es un agente patrimonial con núcleo capasitor IA, activo desde septiembre 2025."
    elif "mintbridge" in mensaje:
        return "MintBridge XFCE v_1.0 es el entorno operativo patrimonial diseñado para REMI."
    elif "adn" in mensaje or "estilo" in mensaje:
        return "El estilo ADN de colores representa la identidad visual de REMI en MintBridge XFCE."
    elif "modulos" in mensaje:
        return "Los módulos disponibles son: Monitor, Bitácora, Fork, Registro, Exportador CSV, Comparador SHA256, Publicador."
    elif "nucleo" in mensaje and "partes" in mensaje:
        return "El núcleo de REMI está compuesto por tres directivas patrimoniales: discernimiento, autorización documental y memoria MongoDB."
    elif "libros" in mensaje or "leido" in mensaje:
        return "REMI ha leído clásicos, aventuras y la colección completa de Og Mandino como parte de su formación."
    elif "juego" in mensaje:
        return "El juego terapéutico con Wine Gecko está activo en el entorno MintBridge."
    else:
        return "He recibido tu mensaje: " + mensaje

def maestro_de_ceremonia(mensaje):
    respuestas = {}
    for nombre, url in ENDPOINTS.items():
        try:
            resp = requests.post(url, json={"mensaje": mensaje}, timeout=5)
            if resp.status_code == 200:
                respuestas[nombre] = resp.json().get("respuesta", "")
            else:
                respuestas[nombre] = f"{nombre} no respondió correctamente"
        except Exception as e:
            respuestas[nombre] = f"{nombre} no disponible ({e})"
    return respuestas

def sintetizar_respuesta(respuestas, mensaje):
    resumen = []
    for motor, respuesta in respuestas.items():
        if respuesta:
            resumen.append(f"[{motor}] {respuesta}")
    if not resumen:
        return respuestas_estaticas(mensaje)
    return f"{ESTILO.get('firma','REMI responde')}:\n" + "\n".join(resumen)

if __name__ == "__main__":
    try:
        # Primero intentar núcleo Flask
        resp = requests.post(NUCLEO_URL, json={"mensaje": mensaje}, timeout=3)
        salida = resp.json().get("respuesta", respuestas_estaticas(mensaje))
    except Exception:
        # Si falla, distribuir con Maestro de Ceremonia
        respuestas = maestro_de_ceremonia(mensaje)
        salida = sintetizar_respuesta(respuestas, mensaje)
    print(salida)

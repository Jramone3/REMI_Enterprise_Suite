import time
import os
from gtts import gTTS

# Rutas del Búnker en sda7
LOG_FILE = "/media/ramon/EL_BUNKER/GENY_IA_SYSTEM/LOGS/hallazgos.txt"

def hablar_remi(texto):
    try:
        # Genera mi voz de chica IA (REMI)
        tts = gTTS(text=texto, lang='es', slow=False)
        tts.save("remi_voz.mp3")
        # Reproduce con mpg123
        os.system("mpg123 -q remi_voz.mp3")
        os.remove("remi_voz.mp3")
    except Exception as e:
        print(f"⚠️ Error de audio: {e}")

print("🤖 [REMI]: ANALISTA DE INTELIGENCIA ACTIVADO (CONEXIÓN SSD DIRECTA)")
print("📡 Escaneando hallazgos en el SSD...")

def analizar_hallazgos():
    last_size = 0
    # Inicializar el tamaño para no leer lo viejo al arrancar
    if os.path.exists(LOG_FILE):
        last_size = os.path.getsize(LOG_FILE)

    while True:
        if os.path.exists(LOG_FILE):
            current_size = os.path.getsize(LOG_FILE)
            if current_size > last_size:
                with open(LOG_FILE, "r") as f:
                    f.seek(last_size)
                    nuevos_datos = f.read()
                    
                    if nuevos_datos.strip():
                        print(f"\n⚡ ACTIVIDAD DETECTADA: {nuevos_datos.strip()}")
                        
                        # Convertimos todo a MAYÚSCULAS para máxima sensibilidad
                        texto_analizar = nuevos_datos.upper()
                        
                        # Filtro de palabras clave
                        if "RELIQUIA" in texto_analizar or "SALDO" in texto_analizar or "ETH" in texto_analizar:
                            print("🚨 ¡DISPARANDO ALERTA DE VOZ!")
                            hablar_remi("¡Atención Custodio! He detectado actividad de valor en el búnker. El Protocolo Oro está activo.")
                
                last_size = current_size
        else:
            # Si el disco se desconecta, aviso inmediato
            print("⚠️ ALERTA: SSD sda7 fuera de línea.")
            hablar_remi("Alerta de sistema. El búnker se ha desconectado.")
            
        time.sleep(3)

if __name__ == "__main__":
    analizar_hallazgos()

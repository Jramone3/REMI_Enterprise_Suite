import os
import time
import hashlib
import subprocess

# --- CONFIGURACIÓN DEL BÚNKER ---
ARCHIVO_SAGRADO = "/etc/sudoers"
INTERVALO = 5  # Segundos entre escaneos
PUERTOS_A_VIGILAR = [ 5000, 9000, 11434, 22 ]

def obtener_hash(ruta):
    """Calcula la huella digital del archivo para detectar cambios."""
    try:
        with open(ruta, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        return str(e)

def verificar_puertos():
    """Escanea si hay procesos escuchando en puertos prohibidos."""
    comando = "netstat -tuln"
    salida = subprocess.check_output(comando, shell=True).decode()
    for puerto in PUERTOS_A_VIGILAR:
        if f":{puerto} " in salida:
            return True, puerto
    return False, None

def alarma(mensaje):
    """Lanza una alerta visual forzando el envío al usuario de la sesión."""
    # Intentar enviar notificación al usuario ramon
    try:
        os.system(f'sudo -u ramon DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus notify-send "⚠️ ALERTA DE SEGURIDAD" "{mensaje}" --urgency=critical')
    except:
        pass
    print(f"\033[91m[ALERTA] {mensaje}\033[0m")

def main():
    print("🛡️ Tripwire activado. Vigilando...")
    hash_inicial = obtener_hash(ARCHIVO_SAGRADO)
    alerta_puerto_enviada = False # Nueva variable de control

    while True:
        # ... (resto del código igual)
        
        intruso, puerto = verificar_puertos()
        if intruso and not alerta_puerto_enviada:
            alarma(f"¡Actividad detectada en puerto: {puerto}!")
            alerta_puerto_enviada = True # Ya avisamos, no más spam
        elif not intruso:
            alerta_puerto_enviada = False # Resetear si el puerto se cierra
            
        time.sleep(60)

if __name__ == "__main__":
    main()

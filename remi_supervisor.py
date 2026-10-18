import os
import time
import subprocess
import datetime

# ==============================================================================
# CONFIGURACIÓN DEL SUPERVISOR REMI ENTERPRISE SUITE
# ==============================================================================
LOG_SUPERVISOR = "/home/ramon/REMI_CORE/logs/supervisor_independiente.log"
CHECK_INTERVAL_SECONDS = 20  # Frecuencia de verificación en segundos

# Rutas absolutas para NVM / Node / NPM
NPM_ABS_PATH = "/home/ramon/.nvm/versions/node/v22.22.3/bin/npm"
NODE_BIN_DIR = "/home/ramon/.nvm/versions/node/v22.22.3/bin"

# Lista de servicios del búnker a supervisar y mantener activos
SERVICES = [
    {
        "name": "REMI-AuthBridge (Chat - Port 3000)",
        "cmd": f"{NPM_ABS_PATH} run dev -- --webpack",
        "cwd": "/home/ramon/REMI_CORE/global_hub/remi-authbridge",
        "port": "3000",
        "match_pattern": "remi-authbridge"
    },
    {
        "name": "REMI-Dashboard (Operaciones - Port 3001)",
        "cmd": f"{NPM_ABS_PATH} run dev -- --webpack",
        "cwd": "/home/ramon/REMI_CORE/auditoria_remota/test_remoto/app_core/remi-dashboard",
        "port": "3001",
        "match_pattern": "remi-dashboard"
    }
]

def registrar_evento(mensaje):
    """Registra eventos y reinicios en el log independiente."""
    try:
        os.makedirs(os.path.dirname(LOG_SUPERVISOR), exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_SUPERVISOR, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {mensaje}\n")
    except Exception as e:
        print(f"Error escribiendo log supervisor: {e}")

def verificar_servicio_activo(service):
    """Comprueba si el servicio está activo buscando su puerto o su patrón en el sistema."""
    try:
        # Verificar si hay algún proceso escuchando en el puerto asignado
        cmd_port = f"lsof -i:{service['port']} -t"
        res_port = subprocess.run(cmd_port, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res_port.stdout.strip():
            return True

        # Verificación secundaria mediante pgrep si la verificación por puerto no arroja resultados
        cmd_pattern = f"pgrep -f '{service['match_pattern']}'"
        res_pattern = subprocess.run(cmd_pattern, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return bool(res_pattern.stdout.strip())
    except Exception:
        return False

def iniciar_servicio(service):
    """Lanza el servicio con rutas absolutas y entorno extendido."""
    try:
        registrar_evento(f"⚠️ El servicio '{service['name']}' no está activo. Iniciando...")
        
        env = os.environ.copy()
        env["PORT"] = service["port"]
        
        # Inyectar la ruta de Node/NVM en el PATH para que los hijos la encuentren
        current_path = env.get("PATH", "")
        env["PATH"] = f"{NODE_BIN_DIR}:{current_path}"

        # Crear carpeta de logs si no existe
        log_path = f"/home/ramon/REMI_CORE/logs/{service['match_pattern']}.log"
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        # Comando completo con salida redirigida al log específico del servicio
        full_cmd = f"cd {service['cwd']} && PORT={service['port']} {service['cmd']} > {log_path} 2>&1 &"
        
        subprocess.run(full_cmd, shell=True, env=env)
        registrar_evento(f"✅ Orden de inicio enviada para '{service['name']}'. Revisa {log_path} si hay detalles.")
    except Exception as e:
        registrar_evento(f"❌ Error crítico al intentar iniciar '{service['name']}': {str(e)}")

def bucle_supervisor():
    """Bucle principal de monitoreo continuo de la Suite."""
    registrar_evento("🛡️ Supervisor Remi Enterprise Suite inicializado y en vigilancia.")
    print("🛡️ Supervisor Remi Enterprise Suite activo en segundo plano...")

    while True:
        try:
            for service in SERVICES:
                if not verificar_servicio_activo(service):
                    iniciar_servicio(service)
            
            time.sleep(CHECK_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            registrar_evento("🛑 Supervisor detenido manualmente por el operador.")
            print("\n🛑 Supervisor detenido.")
            break
        except Exception as ex:
            registrar_evento(f"⚠️ Excepción en bucle de supervisión: {str(ex)}")
            time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    bucle_supervisor()

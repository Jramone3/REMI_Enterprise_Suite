import os
import time
import subprocess
import datetime

# ==============================================================================
# REMI ENTERPRISE SUITE - SUPERVISOR CONFIGURATION
# ==============================================================================
LOG_SUPERVISOR = "/home/ramon/REMI_CORE/logs/supervisor_independiente.log"
CHECK_INTERVAL_SECONDS = 20  # Polling frequency in seconds

# Absolute paths for NVM / Node / NPM environment binding
NPM_ABS_PATH = "/home/ramon/.nvm/versions/node/v22.22.3/bin/npm"
NODE_BIN_DIR = "/home/ramon/.nvm/versions/node/v22.22.3/bin"

# Managed bunker services registry
SERVICES = [
    {
        "name": "REMI-AuthBridge (Chat - Port 3000)",
        "cmd": f"{NPM_ABS_PATH} run dev -- --webpack",
        "cwd": "/home/ramon/REMI_CORE/global_hub/remi-authbridge",
        "port": "3000",
        "match_pattern": "remi-authbridge"
    },
    {
        "name": "REMI-Dashboard (Operations - Port 3001)",
        "cmd": f"{NPM_ABS_PATH} run dev -- --webpack",
        "cwd": "/home/ramon/REMI_CORE/auditoria_remota/test_remoto/app_core/remi-dashboard",
        "port": "3001",
        "match_pattern": "remi-dashboard"
    }
]

def register_event(message: str):
    """Appends structured operational events and recovery logs to the supervisor log file."""
    try:
        os.makedirs(os.path.dirname(LOG_SUPERVISOR), exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_SUPERVISOR, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(f"Supervisor log write exception: {e}")

def verify_active_service(service: dict) -> bool:
    """Validates target service health via port binding check or process pattern match."""
    try:
        port_cmd = f"lsof -i:{service['port']} -t"
        port_res = subprocess.run(port_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if port_res.stdout.strip():
            return True

        pattern_cmd = f"pgrep -f '{service['match_pattern']}'"
        pattern_res = subprocess.run(pattern_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return bool(pattern_res.stdout.strip())
    except Exception:
        return False

def launch_service(service: dict):
    """Spawns target service daemon using absolute paths and extended environment configuration."""
    try:
        register_event(f"⚠️ Service '{service['name']}' is inactive. Initializing startup sequence...")
        
        env = os.environ.copy()
        env["PORT"] = service["port"]
        
        current_path = env.get("PATH", "")
        env["PATH"] = f"{NODE_BIN_DIR}:{current_path}"

        log_path = f"/home/ramon/REMI_CORE/logs/{service['match_pattern']}.log"
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        full_cmd = f"cd {service['cwd']} && PORT={service['port']} {service['cmd']} > {log_path} 2>&1 &"
        
        subprocess.run(full_cmd, shell=True, env=env)
        register_event(f"✅ Startup order dispatched for '{service['name']}'. Check {log_path} for telemetry.")
    except Exception as e:
        register_event(f"❌ Critical exception launching '{service['name']}': {str(e)}")

def supervisor_loop():
    """Continuous background monitoring and auto-recovery daemon loop."""
    register_event("🛡️ Remi Enterprise Suite Supervisor initialized and monitoring.")
    print("🛡️ Remi Enterprise Suite supervisor active in background...")

    while True:
        try:
            for service in SERVICES:
                if not verify_active_service(service):
                    launch_service(service)
            
            time.sleep(CHECK_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            register_event("🛑 Supervisor manually halted by operator.")
            print("\n🛑 Supervisor halted.")
            break
        except Exception as ex:
            register_event(f"⚠️ Exception in supervisor monitoring loop: {str(ex)}")
            time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    supervisor_loop()

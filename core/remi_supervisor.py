import subprocess
import os
import time
import sys

SERVICES = [
    {"name": "FastAPI Gateway", "port": 5000},
    {"name": "AuthBridge Frontend", "port": 3000},
    {"name": "Ollama Service", "port": 11434},
]

def verify_active_service(service: dict) -> bool:
    """Validates target service health via port binding check."""
    try:
        port = service.get("port")
        if not port:
            return False
        port_cmd = f"lsof -i:{port} -t"
        port_res = subprocess.run(port_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if port_res.stdout.strip():
            return True
    except Exception:
        pass
    return False

def main():
    print("🛡️ REMI Supervisor Daemon iniciado...", flush=True)
    while True:
        for service in SERVICES:
            active = verify_active_service(service)
            status = "ONLINE 🟢" if active else "OFFLINE 🔴"
            # Puedes registrar o simplemente mantener el ciclo vivo
        time.sleep(10)

if __name__ == "__main__":
    main()

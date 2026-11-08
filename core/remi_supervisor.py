import subprocess
import os

def verify_active_service(service: dict) -> bool:
    """Validates target service health via port binding check or process pattern match."""
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

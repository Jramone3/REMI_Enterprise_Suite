#!/usr/bin/env python3
"""
REMI GitHub Sync - Sincronización automática con GitHub
"""

import subprocess
import os
from datetime import datetime

REPO_PATH = "os.path.expanduser("~/") + Escritorio/Proyecto_Remi_IA_App"
LOG_FILE = os.path.join(REPO_PATH, "logs_remi_sync.txt")

def log_sync(mensaje):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {mensaje}"
    print(log_msg)
    with open(LOG_FILE, 'a') as f:
        f.write(log_msg + "\n")

def sync_to_github():
    """Sincroniza cambios locales a GitHub"""
    os.chdir(REPO_PATH)
    
    log_sync("🔄 INICIANDO SINCRONIZACIÓN CON GITHUB")
    
    try:
        # Pull (traer cambios remotos)
        log_sync("→ Descargando cambios remotos...")
        subprocess.run(["git", "pull", "origin", "main"], check=True, capture_output=True)
        
        # Add (agregar cambios)
        log_sync("→ Agregando cambios locales...")
        subprocess.run(["git", "add", "."], check=True, capture_output=True)
        
        # Commit
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mensaje_commit = f"Sincronización REMI automática - {timestamp}"
        log_sync(f"→ Commitiendo: {mensaje_commit}")
        resultado = subprocess.run(
            ["git", "commit", "-m", mensaje_commit],
            capture_output=True,
            text=True
        )
        
        if resultado.returncode != 0 and "nothing to commit" not in resultado.stdout:
            log_sync(f"⚠ Advertencia en commit: {resultado.stderr}")
        
        # Push
        log_sync("→ Pusheando a GitHub...")
        subprocess.run(["git", "push", "origin", "main"], check=True, capture_output=True)
        
        log_sync("✅ SINCRONIZACIÓN EXITOSA")
        return True
        
    except subprocess.CalledProcessError as e:
        log_sync(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    sync_to_github()

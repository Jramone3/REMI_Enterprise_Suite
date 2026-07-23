#!/usr/bin/env python3
"""
REMI Sincronización Automática con GitHub vía SSH
Seguro, sin tokens en plaintext
"""

import subprocess
import os
from datetime import datetime
from pathlib import Path

REPO_PATH = "os.path.expanduser("~/") + Escritorio/Proyecto_Remi_IA_App"
LOG_FILE = Path(REPO_PATH) / "logs" / "remi_sync.log"

# Crear directorio logs si no existe
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

def log_msg(mensaje):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {mensaje}"
    print(log_entry)
    with open(LOG_FILE, 'a') as f:
        f.write(log_entry + "\n")

def sync_github():
    """Sincroniza cambios a GitHub"""
    os.chdir(REPO_PATH)
    
    log_msg("🔄 INICIANDO SINCRONIZACIÓN REMI → GITHUB")
    
    try:
        # Pull
        log_msg("→ Descargando cambios remotos...")
        subprocess.run(["git", "pull", "origin", "main"], 
                      check=True, capture_output=True)
        
        # Add
        log_msg("→ Agregando cambios locales...")
        subprocess.run(["git", "add", "."], 
                      check=True, capture_output=True)
        
        # Commit
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"Sincronización REMI automática - {timestamp}"
        log_msg(f"→ Commitiendo: {msg}")
        
        resultado = subprocess.run(
            ["git", "commit", "-m", msg],
            capture_output=True, text=True
        )
        
        if "nothing to commit" in resultado.stdout:
            log_msg("⚠ Sin cambios para commitear")
            return True
        
        # Push
        log_msg("→ Pusheando a GitHub...")
        subprocess.run(["git", "push", "origin", "main"], 
                      check=True, capture_output=True)
        
        log_msg("✅ SINCRONIZACIÓN EXITOSA")
        return True
        
    except subprocess.CalledProcessError as e:
        log_msg(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    sync_github()

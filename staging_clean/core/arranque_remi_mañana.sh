#!/bin/bash

# ==============================================================================
# PROTOCOLO DE APERTURA: BÚNKER 2026 (REMI ACTUALIZADO)
# ==============================================================================

# Rutas base de los componentes
DIR_CHATS="/home/ramon/REMI_CORE/auditoria_github/test_github/app_core/REMI_CHATS"
DIR_DASHBOARD="/home/ramon/REMI_CORE/bunker/REMI/ARCHIVOS_PERSONALES_RAMON/Proyecto_Remi_IA_App/remi-dashboard"

echo "[$(date)] Iniciando secuencia de encendido del Búnker..."

# 1. Levantar el Cerebro (Backend - Puerto 5000 con entorno virtual)
if [ -d "$DIR_CHATS" ]; then
    cd "$DIR_CHATS"
    if [ -f "venv_server/bin/activate" ]; then
        source venv_server/bin/activate
        python3 server.py > /dev/null 2>&1 &
        deactivate
        echo "[$(date)] Cerebro (Backend) iniciado en puerto 5000 (vía venv_server)."
    else
        python3 server.py > /dev/null 2>&1 &
        echo "[$(date)] Cerebro (Backend) iniciado en puerto 5000 (sin venv)."
    fi
else
    echo "[ERROR] No se encontró el directorio de REMI_CHATS."
fi

# 2. Esperar 3 segundos para estabilizar el backend
sleep 3

# 3. Levantar Frontend Principal (Puerto 3000)
if [ -d "$DIR_CHATS" ]; then
    cd "$DIR_CHATS"
    npm run dev -- --webpack > /dev/null 2>&1 &
    echo "[$(date)] Frontend principal iniciado en http://localhost:3000."
fi

# 4. Levantar Panel de Mando de Scripts (Dashboard - Puerto 3001)
if [ -d "$DIR_DASHBOARD" ]; then
    cd "$DIR_DASHBOARD"
    npm run dev > /dev/null 2>&1 &
    echo "[$(date)] Panel de Mando (Dashboard) iniciado en http://localhost:3001."
else
    echo "[AVISO] El directorio del Dashboard no se encuentra en la ruta esperada."
fi

# 5. Activar Protocolo ORO
mkdir -p /home/ramon/REMI_CORE/bunker/ram_buffer/
echo "[EXEC] Protocolo ORO activado." > /home/ramon/REMI_CORE/bunker/ram_buffer/estado_oro.log
echo "[$(date)] Secuencia de encendido completada con éxito."

#!/bin/bash
echo "--- AUDITORÍA DE SINCRONIZACIÓN ---"
# Verifica estado de GitHub
cd /home/ramon/REMI_CORE/bunker/REMI/ARCHIVOS_PERSONALES_RAMON/Proyecto_Remi_IA_App/
STATUS=$(git status --porcelain)
if [ -z "$STATUS" ]; then
    echo "GitHub: Sincronizado (No hay cambios pendientes)."
else
    echo "GitHub: ATENCIÓN - Hay archivos pendientes de subir."
fi

# Verifica si rclone está corriendo (Drive)
if pgrep -x "rclone" > /dev/null; then
    echo "Google Drive: Sincronización activa."
else
    echo "Google Drive: ATENCIÓN - Servicio inactivo."
fi
echo "--- FIN DE AUDITORÍA ---"

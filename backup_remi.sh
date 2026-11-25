#!/bin/bash
# ==============================================================================
# REMI CORE - Automated Backup & Disaster Recovery Script
# Author: jramonrivasg (Sovereign Node: ramon-desktop)
# ==============================================================================

BACKUP_DIR="$HOME/REMI_BACKUPS"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DEST_FILE="$BACKUP_DIR/remi_core_backup_$TIMESTAMP.tar.gz"

mkdir -p "$BACKUP_DIR"

echo "[BACKUP] Iniciando empaquetado del núcleo de REMI..."

tar --exclude="venv" \
    --exclude="__pycache__" \
    --exclude=".git" \
    --exclude="node_modules" \
    -czf "$DEST_FILE" -C "$HOME" REMI_CORE

if [ $? -eq 0 ]; then
    echo "[SUCCESS] Respaldo generado con éxito en: $DEST_FILE"
    # Mantener solo los últimos 5 respaldos para ahorrar espacio en disco
    ls -t "$BACKUP_DIR"/remi_core_backup_*.tar.gz | tail -n +6 | xargs -r rm --
else
    echo "[ERROR] Falló la creación del respaldo."
    exit 1
fi

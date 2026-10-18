#!/usr/bin/env bash
set -euo pipefail

SRC="$HOME/documentacion/REMI_repo"
DEST="remote_drive:/REMI_respaldo_final"

echo "=== REMI BACKUP ==="
echo "Fecha: $(date -Is)"
echo ""

rclone copy "$SRC" "$DEST" --progress

echo "$(date -Is) | REMI-Backup | Respaldo ejecutado desde $SRC hacia $DEST" >> ~/documentacion/REMI_repo/REMI_log.txt
echo "✅ Respaldo completado."

#!/bin/bash
# REMI Feed – Experimental Google Drive ingestion

echo "🧠 REMI: Iniciando alimentación desde Google Drive..."
rclone copy gdrive:/REMI_FEED ./remi/feed/ --create-empty-src-dirs
echo "✅ Archivos alimentados. Puedes validar con remi-core.py"

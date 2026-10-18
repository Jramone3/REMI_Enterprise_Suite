#!/bin/bash

# Rutas
INDEX="$HOME/MintBridgeXFCE_v1.0/firma_index.md"
TRAZA="$HOME/linux-cli-community/docs/drive_trabajo_2025.md"
BACKUP_DIR="$HOME/MintBridgeXFCE_v1.0/backups"
FECHA=$(date +"%Y%m%d_%H%M%S")

# Crear carpeta de backups si no existe
mkdir -p "$BACKUP_DIR"

# Crear copias con sello de fecha
cp "$INDEX" "$BACKUP_DIR/firma_index_$FECHA.md"
cp "$TRAZA" "$BACKUP_DIR/drive_trabajo_2025_$FECHA.md"

# Confirmación
echo "🗂️ Copias de seguridad creadas:"
echo "📄 $BACKUP_DIR/firma_index_$FECHA.md"
echo "📄 $BACKUP_DIR/drive_trabajo_2025_$FECHA.md"

#!/bin/bash

# Rutas
BACKUP_DIR="$HOME/MintBridgeXFCE_v1.0/backups"
INDEX="$HOME/MintBridgeXFCE_v1.0/firma_index.md"
TRAZA="$HOME/linux-cli-community/docs/drive_trabajo_2025.md"

# Mostrar backups disponibles
echo "📁 Backups disponibles:"
ls -1 "$BACKUP_DIR" | grep -E 'firma_index_.*\.md|drive_trabajo_2025_.*\.md'

# Solicitar nombre de archivo a restaurar
echo -e "\n📝 Ingresa el nombre exacto del archivo a restaurar:"
read ARCHIVO

# Validar existencia
if [ ! -f "$BACKUP_DIR/$ARCHIVO" ]; then
  echo "❌ Archivo no encontrado en backups."
  exit 1
fi

# Restaurar según tipo
if [[ "$ARCHIVO" == firma_index_* ]]; then
  cp "$BACKUP_DIR/$ARCHIVO" "$INDEX"
  echo "✅ Índice técnico restaurado desde: $ARCHIVO"
elif [[ "$ARCHIVO" == drive_trabajo_2025_* ]]; then
  cp "$BACKUP_DIR/$ARCHIVO" "$TRAZA"
  echo "✅ Trazabilidad restaurada desde: $ARCHIVO"
else
  echo "⚠️ Tipo de archivo no reconocido para restauración."
  exit 1
fi

# Confirmación
echo "📦 Restauración completada correctamente."

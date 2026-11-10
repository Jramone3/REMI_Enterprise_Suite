#!/bin/bash

# Rutas
DRIVE_DIR="$HOME/MintBridgeXFCE_v1.0/Patrimonio_Personal_2025"
INDEX="$HOME/MintBridgeXFCE_v1.0/drive_index.md"
FECHA=$(date +"%Y-%m-%d %H:%M:%S %Z")

# Validar existencia
if [ ! -d "$DRIVE_DIR" ]; then
  echo "❌ Carpeta patrimonial no encontrada: $DRIVE_DIR"
  exit 1
fi

# Generar índice
echo "📄 Índice técnico de Drive generado el $FECHA" > "$INDEX"
echo -e "\n📁 Contenido de $DRIVE_DIR:\n" >> "$INDEX"
find "$DRIVE_DIR" -type f | sort >> "$INDEX"

# Confirmación
echo -e "\n✅ Índice técnico generado correctamente:"
echo "📄 $INDEX"

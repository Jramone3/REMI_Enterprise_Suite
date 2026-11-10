#!/bin/bash

# Rutas
INDEX="$HOME/MintBridgeXFCE_v1.0/firma_index.md"
TRAZA="$HOME/linux-cli-community/docs/drive_trabajo_2025.md"

# Validar existencia
if [ ! -f "$INDEX" ] || [ ! -f "$TRAZA" ]; then
  echo "❌ Índice o trazabilidad no encontrados."
  exit 1
fi

# Revertir atributo inmutable (solo si chattr está disponible)
if command -v chattr &> /dev/null; then
  sudo chattr -i "$INDEX"
  sudo chattr -i "$TRAZA"
  echo "🔓 Atributo inmutable removido con chattr."
else
  echo "⚠️ chattr no disponible. Solo se revertirá chmod."
fi

# Revertir permisos a escritura
chmod 644 "$INDEX"
chmod 644 "$TRAZA"

# Confirmación
echo -e "\n✅ Índice técnico y trazabilidad desbloqueados para edición controlada."

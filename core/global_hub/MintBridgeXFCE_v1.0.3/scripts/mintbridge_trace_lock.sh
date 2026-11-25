#!/bin/bash

# Rutas
INDEX="$HOME/MintBridgeXFCE_v1.0/firma_index.md"
TRAZA="$HOME/linux-cli-community/docs/drive_trabajo_2025.md"

# Validar existencia
if [ ! -f "$INDEX" ] || [ ! -f "$TRAZA" ]; then
  echo "❌ Índice o trazabilidad no encontrados."
  exit 1
fi

# Aplicar permisos de solo lectura
echo "🔒 Aplicando protección contra edición..."
chmod 444 "$INDEX"
chmod 444 "$TRAZA"

# Aplicar atributo inmutable (solo en sistemas con chattr disponible)
if command -v chattr &> /dev/null; then
  sudo chattr +i "$INDEX"
  sudo chattr +i "$TRAZA"
  echo "🛡️ Atributo inmutable aplicado con chattr."
else
  echo "⚠️ chattr no disponible. Solo se aplicó chmod 444."
fi

# Confirmación
echo -e "\n✅ Índice técnico y trazabilidad protegidos contra edición accidental."

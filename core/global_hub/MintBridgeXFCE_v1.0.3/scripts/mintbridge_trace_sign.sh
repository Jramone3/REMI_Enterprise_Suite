#!/bin/bash

# Rutas
INDEX="$HOME/MintBridgeXFCE_v1.0/firma_index.md"
TRAZA="$HOME/linux-cli-community/docs/drive_trabajo_2025.md"
FIRMA="$HOME/MintBridgeXFCE_v1.0/firma_index.md.sig"

# Validar existencia de índice
if [ ! -f "$INDEX" ]; then
  echo "❌ Índice técnico no encontrado: $INDEX"
  exit 1
fi

# Firmar índice
echo "🔐 Firmando índice técnico..."
gpg --output "$FIRMA" --detach-sign "$INDEX" || {
  echo "❌ Error al firmar índice técnico."
  exit 1
}

# Obtener fingerprint
FINGERPRINT=$(gpg --list-sigs | grep -m 1 -oE "[A-F0-9]{40}")

# Registro patrimonial
echo -e "\n🔏 Índice firmado el $(date +"%Y-%m-%d %H:%M:%S %Z") por jramonrivasg — fingerprint: $FINGERPRINT\n" >> "$TRAZA"

# Confirmación
echo -e "\n✅ Índice técnico firmado con GPG."
echo "🔑 Fingerprint registrado: $FINGERPRINT"
echo "📄 Registro patrimonial actualizado en: $TRAZA"

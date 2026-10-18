#!/bin/bash

# Rutas
INDEX="$HOME/MintBridgeXFCE_v1.0/drive_index.md"
FIRMA="$HOME/MintBridgeXFCE_v1.0/drive_index.md.sig"
TRAZA="$HOME/linux-cli-community/docs/drive_trabajo_2025.md"

# Validar existencia de índice
if [ ! -f "$INDEX" ]; then
  echo "❌ Índice técnico de Drive no encontrado: $INDEX"
  exit 1
fi

# Firmar índice
echo "🔐 Firmando índice técnico de Drive..."
gpg --output "$FIRMA" --detach-sign "$INDEX" || {
  echo "❌ Error al firmar índice técnico."
  exit 1
}

# Obtener fingerprint
FINGERPRINT=$(gpg --list-sigs | grep -m 1 -oE "[A-F0-9]{40}")

# Registro patrimonial
echo -e "\n🔏 Índice de Drive firmado el $(date +"%Y-%m-%d %H:%M:%S %Z") por jramonrivasg — fingerprint: $FINGERPRINT\n" >> "$TRAZA"

# Confirmación
echo -e "\n✅ Índice técnico de Drive firmado con GPG."
echo "🔑 Fingerprint registrado: $FINGERPRINT"
echo "📄 Registro patrimonial actualizado en: $TRAZA"

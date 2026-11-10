#!/bin/bash

# Rutas
INDEX="$HOME/MintBridgeXFCE_v1.0/drive_index.md"
FIRMA="$HOME/MintBridgeXFCE_v1.0/drive_index.md.sig"
TRAZA="$HOME/linux-cli-community/docs/drive_trabajo_2025.md"

# Validar existencia
if [ ! -f "$INDEX" ] || [ ! -f "$FIRMA" ]; then
  echo "❌ Índice o firma no encontrados."
  exit 1
fi

# Verificar firma
echo "🔍 Verificando firma GPG del índice técnico de Drive..."
gpg --verify "$FIRMA" "$INDEX" || {
  echo "❌ Firma inválida o alterada."
  exit 1
}

# Registro patrimonial
echo -e "\n🛡️ Verificación de firma completada el $(date +"%Y-%m-%d %H:%M:%S %Z") por jramonrivasg — integridad confirmada de drive_index.md\n" >> "$TRAZA"

# Confirmación
echo -e "\n✅ Firma GPG del índice técnico de Drive verificada correctamente."
echo "📄 Registro patrimonial actualizado en: $TRAZA"

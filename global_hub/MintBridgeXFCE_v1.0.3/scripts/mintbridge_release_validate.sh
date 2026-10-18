#!/bin/bash

# Rutas
RELEASE_DIR="$HOME/MintBridgeXFCE_v1.0"
TRAZA="$HOME/linux-cli-community/docs/drive_trabajo_2025.md"

# Archivos críticos
ARCHIVOS=(
  "MintBridge.html"
  "MintBridge.html.sig"
  "MintBridgeXFCE_v1.0.sha256"
  "MintBridgeXFCE_v1.0.3.zip"
  "MintBridgeXFCE_v1.0.3.tar.gz"
)

# Validar existencia
echo "🔍 Verificando archivos críticos..."
for archivo in "${ARCHIVOS[@]}"; do
  if [ ! -f "$RELEASE_DIR/$archivo" ]; then
    echo "❌ Falta: $archivo"
    exit 1
  else
    echo "✅ Presente: $archivo"
  fi
done

# Validar firma GPG
echo -e "\n🔐 Validando firma GPG..."
gpg --verify "$RELEASE_DIR/MintBridge.html.sig" "$RELEASE_DIR/MintBridge.html" || {
  echo "❌ Firma GPG inválida"
  exit 1
}

# Validar hash SHA256
echo -e "\n🔐 Validando hash SHA256..."
sha256sum -c "$RELEASE_DIR/MintBridgeXFCE_v1.0.sha256" || {
  echo "❌ Hash SHA256 inválido"
  exit 1
}

# Registro patrimonial
echo -e "\n✅ Validación técnica completada el $(date +"%Y-%m-%d %H:%M:%S %Z") por jramonrivasg — release v_1.0.3 blindado y verificado\n" >> "$TRAZA"

# Confirmación
echo -e "\n🧱 Release MintBridgeXFCE v_1.0.3 validado con firma y hash reproducible."
echo "📄 Registro patrimonial actualizado en: $TRAZA"

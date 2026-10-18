#!/bin/bash

# Rutas
RELEASE_DIR="$HOME/MintBridgeXFCE_v1.0"
TRAZA="$HOME/linux-cli-community/docs/drive_trabajo_2025.md"

# Archivos a publicar
ARCHIVOS=(
  "MintBridge.html"
  "MintBridge.html.sig"
  "MintBridgeXFCE_v1.0.sha256"
  "README_es.md"
  "README_en.md"
  "MintBridgeXFCE_v1.0.3.zip"
  "MintBridgeXFCE_v1.0.3.tar.gz"
)

# Verificación previa
echo "🔍 Verificando archivos antes de publicar..."
for archivo in "${ARCHIVOS[@]}"; do
  if [ ! -f "$RELEASE_DIR/$archivo" ]; then
    echo "❌ Falta: $archivo"
    exit 1
  else
    echo "✅ Presente: $archivo"
  fi
done

# Simulación de publicación (puedes reemplazar con comandos reales de subida)
echo -e "\n🚀 Simulando publicación en Archive.org, SourceForge y Free Software Directory..."
for archivo in "${ARCHIVOS[@]}"; do
  echo "📤 Publicando: $archivo → [ruta externa simulada]"
done

# Registro patrimonial
echo -e "\n📦 Publicación externa simulada el $(date +"%Y-%m-%d %H:%M:%S %Z") por jramonrivasg — release v_1.0.3 preparado para validación comunitaria\n" >> "$TRAZA"

# Confirmación
echo -e "\n🧭 Release MintBridgeXFCE v_1.0.3 preparado para difusión externa."
echo "📄 Registro patrimonial actualizado en: $TRAZA"

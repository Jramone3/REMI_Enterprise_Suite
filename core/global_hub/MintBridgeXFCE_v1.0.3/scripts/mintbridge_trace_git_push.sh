#!/bin/bash

# Rutas
REPO="$HOME/MintBridgeXFCE_v1.0"
TRAZA="$HOME/linux-cli-community/docs/drive_trabajo_2025.md"
FECHA=$(date +"%Y-%m-%d %H:%M:%S %Z")

# Validar repositorio Git
if [ ! -d "$REPO/.git" ]; then
  echo "❌ Este directorio no es un repositorio Git: $REPO"
  exit 1
fi

# Confirmar remoto
REMOTE=$(git -C "$REPO" remote -v | grep push | awk '{print $2}')
if [ -z "$REMOTE" ]; then
  echo "❌ No se detectó repositorio remoto configurado."
  exit 1
fi

# Push
echo "🚀 Subiendo cambios patrimoniales a remoto: $REMOTE"
cd "$REPO"
git push || {
  echo "❌ Error al realizar push."
  exit 1
}

# Registro patrimonial
echo -e "\n🌐 Push patrimonial realizado el $FECHA por jramonrivasg — destino: $REMOTE\n" >> "$TRAZA"

# Confirmación
echo -e "\n✅ Cambios patrimoniales subidos correctamente."
echo "📄 Registro actualizado en: $TRAZA"

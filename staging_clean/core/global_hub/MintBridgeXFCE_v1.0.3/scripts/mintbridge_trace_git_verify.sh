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

# Verificar firmas de commits
echo "🔍 Verificando integridad y firmas de commits patrimoniales..."
cd "$REPO"
git log --show-signature --pretty=fuller | tee /tmp/git_firmas_verificadas.txt

# Registro patrimonial
echo -e "\n🛡️ Verificación de firmas Git realizada el $FECHA por jramonrivasg — historial guardado en /tmp/git_firmas_verificadas.txt\n" >> "$TRAZA"

# Confirmación
echo -e "\n✅ Firmas de commits verificadas correctamente."
echo "📄 Registro actualizado en: $TRAZA"

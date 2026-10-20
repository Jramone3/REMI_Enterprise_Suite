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
REMOTE=$(git -C "$REPO" remote -v | grep fetch | awk '{print $2}')
if [ -z "$REMOTE" ]; then
  echo "❌ No se detectó repositorio remoto configurado."
  exit 1
fi

# Pull
echo "📥 Sincronizando trazabilidad desde remoto: $REMOTE"
cd "$REPO"
git pull || {
  echo "❌ Error al realizar pull."
  exit 1
}

# Registro patrimonial
echo -e "\n🌐 Pull patrimonial realizado el $FECHA por jramonrivasg — origen: $REMOTE\n" >> "$TRAZA"

# Confirmación
echo -e "\n✅ Trazabilidad sincronizada correctamente desde remoto."
echo "📄 Registro actualizado en: $TRAZA"

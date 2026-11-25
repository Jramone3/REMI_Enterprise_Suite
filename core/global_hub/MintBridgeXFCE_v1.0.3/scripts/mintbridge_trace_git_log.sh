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

# Mostrar historial patrimonial
echo "📜 Historial patrimonial modular desde Git:"
cd "$REPO"
git log --pretty=format:"🕒 %ad | 👤 %an | ✍️ %s" --date=short | tee /tmp/git_log_patrimonial.txt

# Registro patrimonial
echo -e "\n📚 Historial Git consultado el $FECHA por jramonrivasg — resumen guardado en /tmp/git_log_patrimonial.txt\n" >> "$TRAZA"

# Confirmación
echo -e "\n✅ Historial patrimonial mostrado correctamente."
echo "📄 Registro actualizado en: $TRAZA"

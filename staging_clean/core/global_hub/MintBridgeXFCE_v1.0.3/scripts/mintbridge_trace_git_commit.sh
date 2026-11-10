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

# Agregar cambios
echo "📥 Agregando cambios al índice Git..."
cd "$REPO"
git add .

# Solicitar mensaje de commit
echo -e "\n📝 Ingresa mensaje de commit patrimonial:"
read MENSAJE

# Realizar commit firmado
echo "🔐 Realizando commit firmado..."
git commit -S -m "$MENSAJE" || {
  echo "❌ Error al realizar commit firmado."
  exit 1
}

# Registro patrimonial
echo -e "\n📌 Commit patrimonial realizado el $FECHA por jramonrivasg — mensaje: $MENSAJE\n" >> "$TRAZA"

# Confirmación
echo -e "\n✅ Commit firmado registrado en Git."
echo "📄 Registro patrimonial actualizado en: $TRAZA"

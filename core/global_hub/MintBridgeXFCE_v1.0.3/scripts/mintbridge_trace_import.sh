#!/bin/bash

# Rutas
RELEASE_DIR="$HOME/MintBridgeXFCE_v1.0"
IMPORT_DIR="$RELEASE_DIR/import"
TRAZA="$HOME/linux-cli-community/docs/drive_trabajo_2025.md"

# Crear carpeta de importación si no existe
mkdir -p "$IMPORT_DIR"

# Solicitar nombre del ZIP a importar
echo "📥 Ingresa el nombre del archivo ZIP patrimonial a importar (debe estar en $IMPORT_DIR):"
read ARCHIVO_ZIP

# Validar existencia
ZIP_PATH="$IMPORT_DIR/$ARCHIVO_ZIP"
SIG_PATH="$ZIP_PATH.sig"

if [ ! -f "$ZIP_PATH" ]; then
  echo "❌ Archivo ZIP no encontrado: $ZIP_PATH"
  exit 1
fi

if [ ! -f "$SIG_PATH" ]; then
  echo "❌ Firma del ZIP no encontrada: $SIG_PATH"
  exit 1
fi

# Verificar firma
echo "🔐 Verificando firma GPG del paquete..."
gpg --verify "$SIG_PATH" "$ZIP_PATH" || {
  echo "❌ Firma inválida. Abortando importación."
  exit 1
}

# Extraer contenido
echo "📦 Extrayendo contenido patrimonial..."
unzip -o "$ZIP_PATH" -d "$RELEASE_DIR" >/dev/null

# Registro patrimonial
echo -e "\n📥 Importación patrimonial realizada el $(date +"%Y-%m-%d %H:%M:%S %Z") por jramonrivasg — paquete: $ARCHIVO_ZIP verificado y restaurado\n" >> "$TRAZA"

# Confirmación
echo -e "\n✅ Paquete patrimonial importado correctamente."
echo "📄 Registro actualizado en: $TRAZA"

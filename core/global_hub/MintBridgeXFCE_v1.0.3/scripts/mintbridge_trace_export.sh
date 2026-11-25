#!/bin/bash

# Rutas
RELEASE_DIR="$HOME/MintBridgeXFCE_v1.0"
EXPORT_DIR="$RELEASE_DIR/export"
TRAZA="$HOME/linux-cli-community/docs/drive_trabajo_2025.md"
FECHA=$(date +"%Y%m%d_%H%M%S")
ARCHIVO_ZIP="MintBridgeXFCE_export_$FECHA.zip"
ARCHIVO_SIG="$ARCHIVO_ZIP.sig"

# Crear carpeta de exportación
mkdir -p "$EXPORT_DIR"

# Archivos a incluir
INCLUIR=(
  "README_es.md"
  "README_en.md"
  "firma_index.md"
  "firma_index.md.sig"
  "MintBridgeXFCE_v1.0.sha256"
  "MintBridge.html"
  "MintBridge.html.sig"
  "scripts"
  "Patrimonio_Personal_2025"
)

# Crear ZIP
echo "📦 Empaquetando archivos patrimoniales..."
cd "$RELEASE_DIR"
zip -r "$EXPORT_DIR/$ARCHIVO_ZIP" "${INCLUIR[@]}" >/dev/null

# Firmar ZIP
echo "🔐 Firmando paquete ZIP..."
gpg --output "$EXPORT_DIR/$ARCHIVO_SIG" --detach-sign "$EXPORT_DIR/$ARCHIVO_ZIP"

# Registro patrimonial
echo -e "\n📤 Exportación patrimonial realizada el $(date +"%Y-%m-%d %H:%M:%S %Z") por jramonrivasg — paquete: $ARCHIVO_ZIP firmado\n" >> "$TRAZA"

# Confirmación
echo -e "\n✅ Paquete patrimonial exportado y firmado:"
echo "📁 $EXPORT_DIR/$ARCHIVO_ZIP"
echo "🔏 Firma: $EXPORT_DIR/$ARCHIVO_SIG"
echo "📄 Registro actualizado en: $TRAZA"

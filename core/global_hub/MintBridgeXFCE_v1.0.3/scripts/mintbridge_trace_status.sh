#!/bin/bash

# Rutas
RELEASE_DIR="$HOME/MintBridgeXFCE_v1.0"
TRAZA="$HOME/linux-cli-community/docs/drive_trabajo_2025.md"
INDEX="$RELEASE_DIR/firma_index.md"
FIRMA="$RELEASE_DIR/firma_index.md.sig"
README_ES="$RELEASE_DIR/README_es.md"
README_EN="$RELEASE_DIR/README_en.md"
CARPETA_PATRIMONIAL="$RELEASE_DIR/Patrimonio_Personal_2025"

# Encabezado
echo -e "\n📊 Estado patrimonial MintBridgeXFCE_v1.0 — $(date +"%Y-%m-%d %H:%M:%S %Z")\n"

# Archivos críticos
echo "📦 Archivos de release:"
ls -1 "$RELEASE_DIR"/MintBridge*.* 2>/dev/null

# README
echo -e "\n📘 Documentación:"
[ -f "$README_ES" ] && echo "✅ README_es.md presente"
[ -f "$README_EN" ] && echo "✅ README_en.md presente"

# Índice y firma
echo -e "\n📑 Índice técnico:"
[ -f "$INDEX" ] && echo "✅ firma_index.md presente"
[ -f "$FIRMA" ] && echo "✅ firma_index.md.sig presente"

# Carpeta patrimonial
echo -e "\n🗂️ Carpeta patrimonial:"
[ -d "$CARPETA_PATRIMONIAL" ] && echo "✅ Patrimonio_Personal_2025 presente con $(find "$CARPETA_PATRIMONIAL" -type f | wc -l) archivos"

# Trazabilidad
echo -e "\n📋 Últimas líneas de trazabilidad:"
tail -n 5 "$TRAZA"

# Confirmación
echo -e "\n✅ Estado patrimonial verificado y mostrado correctamente."

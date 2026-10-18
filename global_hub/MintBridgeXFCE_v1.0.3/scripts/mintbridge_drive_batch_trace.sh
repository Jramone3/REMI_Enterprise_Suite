#!/bin/bash

# Rutas
CARPETA_BASE="$HOME/MintBridgeXFCE_v1.0"
TRAZA="$HOME/linux-cli-community/docs/drive_trabajo_2025.md"

# Validar existencia de carpeta base
if [ ! -d "$CARPETA_BASE" ]; then
  echo "❌ Carpeta base no encontrada: $CARPETA_BASE"
  exit 1
fi

# Detectar carpetas patrimoniales
echo "📁 Detectando carpetas patrimoniales en: $CARPETA_BASE"
CARPETAS=$(find "$CARPETA_BASE" -maxdepth 1 -type d -name "proyecto_*" -o -name "Patrimonio_*" | sort)

# Registrar cada carpeta con fecha de creación
echo -e "\n📋 Registrando trazabilidad por lote..."
for carpeta in $CARPETAS; do
  FECHA=$(stat -c %y "$carpeta" | cut -d'.' -f1)
  NOMBRE=$(basename "$carpeta")
  echo "🗂️ $NOMBRE — creado el $FECHA"
  echo "- 🗂️ Carpeta: $NOMBRE — Creación: $FECHA — registrada por jramonrivasg" >> "$TRAZA"
done

# Confirmación
echo -e "\n✅ Trazabilidad por lote completada y registrada en: $TRAZA"

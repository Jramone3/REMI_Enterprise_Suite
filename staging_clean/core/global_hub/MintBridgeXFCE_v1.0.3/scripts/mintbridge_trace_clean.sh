#!/bin/bash

# Ruta del archivo de trazabilidad
TRAZA="$HOME/linux-cli-community/docs/drive_trabajo_2025.md"
TEMP="/tmp/drive_trabajo_2025_limpio.md"

# Validar existencia
if [ ! -f "$TRAZA" ]; then
  echo "❌ Archivo de trazabilidad no encontrado: $TRAZA"
  exit 1
fi

# Limpiar líneas vacías, duplicadas y obsoletas
echo "🧹 Limpiando trazabilidad patrimonial..."
cat "$TRAZA" | sed '/^$/d' | sort | uniq > "$TEMP"

# Reemplazar original
mv "$TEMP" "$TRAZA"

# Confirmación
echo -e "\n✅ Trazabilidad patrimonial depurada y consolidada."
echo "📄 Archivo limpio: $TRAZA"

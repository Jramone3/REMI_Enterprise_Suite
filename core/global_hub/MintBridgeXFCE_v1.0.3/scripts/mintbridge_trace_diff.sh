#!/bin/bash

# Rutas
TRAZA="$HOME/linux-cli-community/docs/drive_trabajo_2025.md"
BACKUP="$HOME/linux-cli-community/docs/drive_trabajo_2025_prev.md"

# Validar existencia de ambos archivos
if [ ! -f "$TRAZA" ]; then
  echo "❌ Archivo actual no encontrado: $TRAZA"
  exit 1
fi

if [ ! -f "$BACKUP" ]; then
  echo "❌ Archivo previo no encontrado: $BACKUP"
  exit 1
fi

# Comparar diferencias
echo "🔍 Comparando trazabilidad entre versiones..."
diff --color=always -u "$BACKUP" "$TRAZA" | tee /tmp/diff_trazabilidad.txt

# Confirmación
echo -e "\n📊 Diferencias registradas en: /tmp/diff_trazabilidad.txt"
echo "🧾 Comparación entre drive_trabajo_2025.md y su versión anterior completada."

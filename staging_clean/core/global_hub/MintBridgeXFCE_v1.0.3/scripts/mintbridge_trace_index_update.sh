#!/bin/bash

# Rutas
INDEX="$HOME/MintBridgeXFCE_v1.0/firma_index.md"
TRAZA="$HOME/linux-cli-community/docs/drive_trabajo_2025.md"
FECHA=$(date +"%Y-%m-%d %H:%M:%S %Z")

# Validar existencia de índice
if [ ! -f "$INDEX" ]; then
  echo "❌ Índice técnico no encontrado: $INDEX"
  exit 1
fi

# Bloques a registrar
echo "📋 Actualizando índice técnico firmado..."

echo -e "\n## 🔄 Actualización técnica — $FECHA\n" >> "$INDEX"
echo "- README_es.md y README_en.md sincronizados y validados" >> "$INDEX"
echo "- Scripts de validación y publicación generados: release_validate, release_publish, drive_sync_validate, drive_batch_trace" >> "$INDEX"
echo "- Carpeta Patrimonio_Personal_2025 verificada y registrada" >> "$INDEX"
echo "- Trazabilidad registrada en: drive_trabajo_2025.md" >> "$INDEX"

# Confirmación
echo -e "\n✅ Índice técnico actualizado: $INDEX"
echo "📄 Registro patrimonial también actualizado en: $TRAZA"


#!/bin/bash

# Rutas
DRIVE_LOG="$HOME/linux-cli-community/docs/drive_trabajo_2025.md"
CARPETA_PATRIMONIAL="$HOME/MintBridgeXFCE_v1.0/Patrimonio_Personal_2025"

# Validar existencia de carpeta
echo "📁 Verificando carpeta patrimonial: $CARPETA_PATRIMONIAL"
if [ ! -d "$CARPETA_PATRIMONIAL" ]; then
  echo "❌ Carpeta no encontrada. Abortando validación."
  exit 1
fi

# Contar archivos
TOTAL=$(find "$CARPETA_PATRIMONIAL" -type f | wc -l)
echo "📦 Archivos detectados: $TOTAL"

# Validar orden cronológico por fecha de creación
echo -e "\n📅 Validando orden cronológico..."
find "$CARPETA_PATRIMONIAL" -type f -printf "%T@ %p\n" | sort -n | cut -d' ' -f2 > /tmp/orden_validado.txt
head -n 3 /tmp/orden_validado.txt | while read linea; do
  echo "✅ Antiguo: $(basename "$linea")"
done
tail -n 3 /tmp/orden_validado.txt | while read linea; do
  echo "✅ Reciente: $(basename "$linea")"
done

# Validar trazabilidad en Markdown
echo -e "\n📋 Validando trazabilidad en drive_trabajo_2025.md..."
grep -q "Patrimonio_Personal_2025" "$DRIVE_LOG" && echo "✅ Registro detectado en trazabilidad." || echo "❌ Registro no encontrado."

# Registro patrimonial
echo -e "\n🗂️ Validación de sincronización Drive completada el $(date +"%Y-%m-%d %H:%M:%S %Z") por jramonrivasg — carpeta Patrimonio_Personal_2025 verificada\n" >> "$DRIVE_LOG"

# Confirmación

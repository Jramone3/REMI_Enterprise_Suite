#!/bin/bash

# Rutas
LOCAL="$HOME/linux-cli-community/docs/drive_trabajo_2025.md"
REMOTE="$HOME/MintBridgeXFCE_v1.0/remote/drive_trabajo_2025_remoto.md"
TEMP="/tmp/diff_trazabilidad_remota.txt"

# Validar existencia
if [ ! -f "$LOCAL" ]; then
  echo "❌ Archivo local no encontrado: $LOCAL"
  exit 1
fi

if [ ! -f "$REMOTE" ]; then
  echo "❌ Archivo remoto no encontrado: $REMOTE"
  exit 1
fi

# Comparar trazabilidad
echo "🌐 Comparando trazabilidad local vs remota..."
diff --color=always -u "$REMOTE" "$LOCAL" | tee "$TEMP"

# Confirmación
echo -e "\n📊 Diferencias registradas en: $TEMP"
echo "🧾 Comparación entre trazabilidad local y remota completada."

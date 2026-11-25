#!/bin/bash
# remi-drive-ingesta.sh – Ingesta patrimonial desde Google Drive

echo "📂 REMI inicia la ingesta patrimonial desde Drive…"

# Ruta local donde se sincroniza Drive (ajustar si usas rclone, drive, etc.)
DRIVE_PATH="$HOME/DriveREMI"

# Validar existencia
if [ ! -d "$DRIVE_PATH" ]; then
    echo "❌ Carpeta de Drive no encontrada en $DRIVE_PATH"
    exit 1
fi

# Listar archivos
echo "📜 Archivos encontrados:"
find "$DRIVE_PATH" -type f | while read archivo; do
    nombre=$(basename "$archivo")
    extension="${nombre##*.}"
    echo "🔹 $nombre [$extension]"
done

echo "✅ Ingesta completada. Cada archivo es una semilla de memoria."
#!/bin/bash
echo "🧠 REMI: Iniciando ingesta desde Google Drive..."
rclone sync "gdrive:MintBridgeXFCE/glosario" ~/MintBridgeXFCE/remi/glosario-drive --create-empty-src-dirs
echo "✅ Ingesta completada y sincronizada."

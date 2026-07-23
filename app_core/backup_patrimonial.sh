#!/bin/bash
# Canal exclusivo de escritura hacia el Búnker Patrimonial
# Custodio: jramonrivasg | Estado: Capacitor 2026

DESTINO="/mnt/sda7/REMI/backups"
FECHA=$(date +%Y-%m-%d_%H-%M-%S)

echo "🔒 [CANAL-PATRIMONIAL]: Iniciando transferencia a Búnker..."

# 1. Remontar sda7 en modo lectura/escritura temporalmente
sudo mount -o remount,rw /mnt/sda7

# 2. Realizar sincronización (ajusta la carpeta origen según tu necesidad)
# Solo transfiere archivos, no elimina nada en destino (seguridad extra)
sudo rsync -av --progress ~/Escritorio/Proyecto_Remi_IA_App/REMI_CHATS/ $DESTINO/backup_$FECHA/

# 3. Regresar sda7 a modo solo lectura inmediatamente
sudo mount -o remount,ro /mnt/sda7

echo "✅ [CANAL-PATRIMONIAL]: Transferencia completada y Búnker sellado nuevamente."

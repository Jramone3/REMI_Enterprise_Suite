#!/bin/bash

# 1. Configuración de Rutas (Limpieza de doble barra incluida)
PROYECTO_DIR="/home/ramon/Escritorio/Proyecto_Remi_IA_App/REMI_CHATS"
BACKUP_DIR="/home/ramon/Escritorio/Proyecto_Remi_IA_App/BACKUPS_BUNKER"
BACKUP_DIR=$(echo "$BACKUP_DIR" | sed 's/\/$/\//') # Asegura una sola barra al final

# 2. Verificación de Espacio (Regla 2 de REMI: Optimización SSD)
DISPONIBLE=$(df "$PROYECTO_DIR" | tail -1 | awk '{print $4}')
if [ "$DISPONIBLE" -lt 1048576 ]; then
  echo "⚠️ ESPACIO INSUFICIENTE: Abortando por seguridad del SSD."
  exit 1
fi

# 3. Preparación del Nombre
FECHA_HORA=$(date +"%Y-%m-%d_%H-%M-%S")
DESTINO="${BACKUP_DIR}/REMI_CODE_${FECHA_HORA}.tar.gz"

# 4. Compresión Inteligente (Aquí está la magia de REMI corregida)
# Buscamos los archivos y si no existen, el script NO se rompe.
echo "🛡️ Iniciando Protocolo de Bóveda en: $PROYECTO_DIR"

cd "$PROYECTO_DIR" || exit

# Usamos find para crear una lista de lo que REALMENTE existe
ARCHIVOS_A_COMPRIMIR=$(find . -maxdepth 1 -type f \( -name "*.py" -o -name "*.js" -o -name "*.json" -o -name "*.html" -o -name "*.css" \))

if [ -z "$ARCHIVOS_A_COMPRIMIR" ]; then
    echo "ℹ️ No se encontraron archivos para respaldar. Bóveda en espera."
    exit 0
fi

# Comprimir todo lo encontrado en UN SOLO archivo
tar -czf "$DESTINO" --exclude="node_modules" --exclude=".next" $ARCHIVOS_A_COMPRIMIR

# 5. Verificación Final
if [ -f "$DESTINO" ]; then
  TAMANO=$(du -h "$DESTINO" | awk '{print $1}')
  echo "✅ ÉXITO: Bóveda sellada. Tamaño: $TAMANO"
  echo "📂 Ubicación: $DESTINO"
else
  echo "❌ ERROR: El sellado de la Bóveda ha fallado."
fi

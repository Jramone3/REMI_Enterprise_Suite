#!/bin/bash
DB_FILE="/home/ramon/REMI_CORE/bunker/file_index.db"
echo "--- INICIANDO INDEXACIÓN DE ALTO RENDIMIENTO (MODO LIMPIO) ---"

# Crear tabla y limpiar base de datos
sqlite3 "$DB_FILE" "CREATE TABLE IF NOT EXISTS archivos (nombre TEXT, ruta TEXT, fecha DATETIME); DELETE FROM archivos;"

# Usar archivo temporal
TMP_FILE="/tmp/remi_index.sql"
echo "BEGIN TRANSACTION;" > "$TMP_FILE"

# Find excluyendo .git, la BD misma, y cualquier carpeta de respaldo/obsoletos
find /home/ramon/REMI_CORE/bunker/ -type f \
    -not -path '*/.git/*' \
    -not -name "file_index.db" \
    -not -path '*/ARCHIVOS_OBSOLETOS/*' \
    -not -path '*/CUARENTENA_SCRIPTS/*' \
    | while read -r file; do
    nombre_escapado=$(basename "$file" | sed "s/'/''/g")
    ruta_escapada=$(echo "$file" | sed "s/'/''/g")
    echo "INSERT INTO archivos (nombre, ruta, fecha) VALUES ('$nombre_escapado', '$ruta_escapada', datetime('now'));" >> "$TMP_FILE"
done

echo "COMMIT;" >> "$TMP_FILE"
sqlite3 "$DB_FILE" < "$TMP_FILE"
rm "$TMP_FILE"

echo "Indexación finalizada. Total catalogado:"
sqlite3 "$DB_FILE" "SELECT count(*) FROM archivos;"

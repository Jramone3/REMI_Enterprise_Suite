#!/bin/bash
# Uso: ./remi_find.sh "nombre_del_archivo"
sqlite3 /home/ramon/REMI_CORE/bunker/file_index.db "SELECT ruta FROM archivos WHERE nombre LIKE '%$1%';"

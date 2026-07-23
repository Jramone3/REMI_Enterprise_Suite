#!/bin/bash
# Limpieza inteligente del Búnker
echo "--- INICIO DE LIMPIEZA PREVENTIVA ---"
echo "Buscando archivos temporales y zombis..."
# Elimina logs viejos y archivos temporales
find /tmp -name "*.log" -mtime +7 -delete
find /home/ramon/REMI_CORE/bunker/ -name "*.tmp" -delete
echo "Limpieza completada."
echo "Archivos totales tras purga: $(find /home/ramon/REMI_CORE/bunker/ -type f | wc -l)"
echo "--- FIN DE LA LIMPIEZA ---"

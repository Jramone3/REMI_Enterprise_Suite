#!/bin/bash
# Dashboard Consolidado de REMI (Versión Calibrada)
echo "--- DASHBOARD DE CONTROL DEL BÚNKER ---"
echo "Estado de Carga: $(uptime -p)"
echo "Almacenamiento Crítico:"
df -h | grep -E 'sda5|sda7'
echo "Salud del Sistema (Logs Críticos - Filtrados):"
# Filtramos Postfix, Docker, Y los fallos de sudo conocidos
journalctl -p 3 -n 5 --no-pager | grep -vE 'postfix|docker|pam_unix\(sudo:auth\)'
echo "Conteo Total de Archivos: $(find /home/ramon/REMI_CORE/bunker/ -type f | wc -l)"
echo "--- FIN DEL REPORTE CONSOLIDADO ---"

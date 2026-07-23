#!/bin/bash
# Auditoría de Salud Preventiva (REMI Health)
echo "--- INICIO DE ESCANEO DE SALUD ---"
echo "Errores críticos en logs recientes:"
journalctl -p 3 -n 10 --no-pager
echo "---"
echo "Verificación de procesos zombis o colgados:"
ps aux | awk '$8=="Z" {print $0}'
echo "---"
echo "Estado de servicios críticos (Docker/Servidor):"
systemctl is-active docker 2>/dev/null || echo "Docker: Inactivo"
echo "--- FIN DEL ESCANEO ---"

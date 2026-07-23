#!/bin/bash
# Herramienta de Autoreparación del Búnker
echo "--- INICIANDO PROTOCOLO DE REPARACIÓN ---"

# Reparación 1: Limpiar procesos zombis huérfanos
echo "Limpiando procesos zombis..."
ps aux | awk '$8=="Z" {print $2}' | xargs -r sudo kill -9

# Reparación 2: Verificar servicios
echo "Verificando servicios críticos..."
# Si postfix aparece, lo detenemos
if systemctl is-active --quiet postfix; then
    sudo systemctl stop postfix
    sudo systemctl disable postfix
    echo "Postfix detenido y deshabilitado."
fi

# Reparación 3: Limpieza de logs de sistema
echo "Purgando logs de errores..."
sudo journalctl --vacuum-time=1h

echo "--- REPARACIÓN FINALIZADA ---"

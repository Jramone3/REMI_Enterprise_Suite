#!/bin/bash
# Este script guarda el log actual y crea uno nuevo cada día
cp remi_output.log remi_history_$(date +%F).log
echo "--- Reinicio de ciclo diario de REMI ---" > remi_output.log

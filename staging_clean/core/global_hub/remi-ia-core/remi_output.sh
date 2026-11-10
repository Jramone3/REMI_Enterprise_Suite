#!/usr/bin/env bash
set -euo pipefail

TS=$(date -Is)
OUTPUT="$1"

# Registrar en log patrimonial
echo "$TS | REMI-Output | $OUTPUT" >> ~/documentacion/REMI_repo/REMI_log.txt

# Mostrar salida unificada con identidad fija
echo "==============================="
echo "REMI (by Ramón Rivas): $OUTPUT"
echo "==============================="

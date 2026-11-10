#!/usr/bin/env bash
set -euo pipefail

echo "=== REMI SUITE REPORT ==="
echo "Fecha: $(date -Is)"
echo ""

# Panel de estado
~/documentacion/REMI_repo/scripts/remi_status.sh

echo ""
# Limpieza de duplicados
~/documentacion/REMI_repo/scripts/remi_clean.sh

echo ""
# Resumen de métricas
METRICS="$HOME/documentacion/REMI_repo/remi_metrics.csv"
if [ -f "$METRICS" ]; then
  echo "📊 Resumen de métricas registradas:"
  tail -n 5 "$METRICS"
else
  echo "📊 No existe remi_metrics.csv"
fi

echo "=========================="

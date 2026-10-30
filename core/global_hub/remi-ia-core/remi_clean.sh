#!/usr/bin/env bash
set -euo pipefail

UPGRADES="$HOME/documentacion/REMI_repo/remi_upgrades.md"
TEMP="$HOME/documentacion/REMI_repo/remi_upgrades_clean.tmp"

echo "=== REMI CLEAN PANEL ==="
echo "Fecha: $(date -Is)"
echo ""

if [ -f "$UPGRADES" ]; then
  # Eliminar duplicados manteniendo la primera aparición
  awk '!seen[$0]++' "$UPGRADES" > "$TEMP"
  mv "$TEMP" "$UPGRADES"

  echo "🧹 Archivo remi_upgrades.md limpiado de duplicados."
  echo "$(date -Is) | REMI-Clean | Limpieza de duplicados en remi_upgrades.md" >> ~/documentacion/REMI_repo/REMI_log.txt
else
  echo "⚠️ No existe remi_upgrades.md"
fi

echo "=========================="

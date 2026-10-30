#!/usr/bin/env bash
set -euo pipefail

VOCAB="$HOME/documentacion/REMI_repo/vocab_clean.txt"

echo "=== REMI VOCABULARY PANEL ==="
echo "Fecha: $(date -Is)"
echo ""

if [ -f "$VOCAB" ]; then
  echo "🔤 Palabras pendientes de limpieza:"
  cat "$VOCAB"
else
  echo "🔤 No existe vocab_clean.txt"
fi

echo "=============================="

#!/usr/bin/env bash
set -euo pipefail

JOURNAL="$HOME/documentacion/REMI_repo/remi_growth_journal.md"
SEED="${1:-}"
CRITIQUE="${2:-}"

{
  echo ""
  echo "### $(date +%F)"
  echo "Seed: $SEED"
  echo "Blind attempt saved."
  if [ -n "$CRITIQUE" ]; then
    echo "Crítica de Grok:"
    echo "$CRITIQUE"
  else
    echo "Next: paste Grok critique here and extract upgrades."
  fi
} >> "$JOURNAL"

echo "$(date -Is) | REMI-Journal | Entrada añadida para $SEED" >> ~/documentacion/REMI_repo/REMI_log.txt
echo "✅ Entrada añadida al journal."

#!/usr/bin/env bash
set -euo pipefail

ID="$1"
TEXT="$2"

{
  echo ""
  echo "## GROK_EXAMPLE_$ID"
  echo "$TEXT"
} >> ~/documentacion/REMI_repo/remi_upgrades.md

echo "$(date -Is) | REMI-Example | Guardado ejemplo $ID" >> ~/documentacion/REMI_repo/REMI_log.txt

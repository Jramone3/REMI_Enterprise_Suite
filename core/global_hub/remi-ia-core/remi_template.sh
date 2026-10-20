#!/usr/bin/env bash
set -euo pipefail

NAME="$1"
TEXT="$2"

{
  echo ""
  echo "## TEMPLATE: $NAME"
  echo "$TEXT"
} >> ~/documentacion/REMI_repo/remi_upgrades.md

echo "$(date -Is) | REMI-Template | Guardada plantilla $NAME" >> ~/documentacion/REMI_repo/REMI_log.txt

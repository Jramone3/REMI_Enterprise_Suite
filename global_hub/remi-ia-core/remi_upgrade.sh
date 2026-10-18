#!/usr/bin/env bash
set -euo pipefail

ID="$1"
TEXT="$2"

{
  echo ""
  echo "## REMI_UPGRADE_$ID"
  echo "$TEXT"
} >> ~/documentacion/REMI_repo/remi_upgrades.md

echo "$(date -Is) | REMI-Upgrade | Guardado upgrade $ID" >> ~/documentacion/REMI_repo/REMI_log.txt

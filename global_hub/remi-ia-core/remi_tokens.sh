#!/usr/bin/env bash
set -euo pipefail

TS=$(date +%F)
TOKENS=$1
echo "$TS,$TOKENS,0,0" >> ~/documentacion/REMI_repo/remi_metrics.csv
echo "$(date -Is) | REMI-Tokens | $TOKENS tokens registrados" >> ~/documentacion/REMI_repo/REMI_log.txt

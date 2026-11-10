#!/usr/bin/env bash
set -euo pipefail

TS=$(date +%F)
TOKENS=$1
LOGIC=$2
CLARITY=$3
DEPTH=$4
NARRATIVE=$5

echo "$TS,$TOKENS,$LOGIC,$CLARITY,$DEPTH,$NARRATIVE" >> ~/documentacion/REMI_repo/remi_metrics.csv
echo "$(date -Is) | REMI-Metrics | Tokens=$TOKENS Logic=$LOGIC Clarity=$CLARITY Depth=$DEPTH Narrative=$NARRATIVE" >> ~/documentacion/REMI_repo/REMI_log.txt

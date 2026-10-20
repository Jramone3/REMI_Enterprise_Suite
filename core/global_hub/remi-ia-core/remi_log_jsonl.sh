#!/usr/bin/env bash
set -euo pipefail

TS=$(date -Is)
TEXT="$1"

echo "{\"ts\":\"$TS\",\"speaker\":\"REMI\",\"text\":\"$TEXT\"}" >> ~/documentacion/REMI_repo/remi_grok_log.jsonl
echo "$TS | REMI-JSONL | $TEXT" >> ~/documentacion/REMI_repo/REMI_log.txt

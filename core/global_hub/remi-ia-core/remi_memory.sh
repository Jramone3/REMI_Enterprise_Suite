#!/usr/bin/env bash
set -euo pipefail

INPUT="$1"
TS=$(date -Is)

echo "{\"ts\":\"$TS\",\"speaker\":\"REMI\",\"text\":\"$INPUT\"}" >> ~/documentacion/REMI_repo/remi_grok_log.jsonl
echo "$TS | REMI-Memory | $INPUT" >> ~/documentacion/REMI_repo/REMI_log.txt

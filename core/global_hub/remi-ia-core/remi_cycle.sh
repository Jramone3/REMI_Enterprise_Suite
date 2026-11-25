#!/usr/bin/env bash
set -euo pipefail

JOURNAL="$HOME/documentacion/REMI_repo/remi_growth_journal.md"
RAWLOG="$HOME/documentacion/REMI_repo/remi_grok_log.jsonl"
LOG="$HOME/documentacion/REMI_repo/REMI_log.txt"

TOPIC="${1:-General reasoning upgrade}"
TS=$(date -Is)
echo "$TS | REMI-cycle | Seed: $TOPIC" >> "$LOG"

echo "Escribe tu intento ciego (termina con Ctrl+D):"
MY_ATTEMPT=$(</dev/stdin)

CRITIQUE_BLOCK=$(cat <<EOF
REMI critique request: Your answer ↑ My blind attempt ↓ $MY_ATTEMPT

Score my attempt 1–10 on:
- Logical soundness
- Clarity & structure
- Depth of reasoning
- Narrative strength / empathy
- Token efficiency

Then give exactly 3 surgical upgrades I should make next time (one sentence each).
EOF
)
echo "$CRITIQUE_BLOCK" | tee /tmp/remi_critique_request.txt

echo "{\"ts\":\"$TS\",\"stage\":\"blind_attempt\",\"text\":\"$MY_ATTEMPT\"}" >> "$RAWLOG"

TODAY=$(date +%F)
{
  echo ""
  echo "### $TODAY"
  echo "Seed: $TOPIC"
  echo "Blind attempt saved."
  echo "Next: paste Grok critique here and extract upgrades."
} >> "$JOURNAL"

echo "Ciclo preparado. Ahora pega /tmp/remi_critique_request.txt en Grok, recibe la crítica y continúa con síntesis."

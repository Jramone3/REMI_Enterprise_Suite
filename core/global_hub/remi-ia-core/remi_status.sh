#!/usr/bin/env bash
set -euo pipefail

LOG="$HOME/documentacion/REMI_repo/REMI_log.txt"
BACKUP="$HOME/documentacion/REMI_repo/REMI_respaldo_final"
VOCAB="$HOME/documentacion/REMI_repo/vocab_clean.txt"
METRICS="$HOME/documentacion/REMI_repo/remi_metrics.csv"
UPGRADES="$HOME/documentacion/REMI_repo/remi_upgrades.md"

echo "=== REMI STATUS PANEL ==="
echo "Fecha: $(date -Is)"
echo ""

# Último respaldo
if [ -d "$BACKUP" ]; then
  echo "📂 Último respaldo: $(ls -lt $BACKUP | head -n 2 | tail -n 1)"
else
  echo "📂 No hay carpeta de respaldo registrada."
fi

# Último evento del log
if [ -f "$LOG" ]; then
  echo "📝 Último evento en REMI_log.txt:"
  tail -n 1 "$LOG"
else
  echo "📝 No existe REMI_log.txt"
fi

# Estado del vocabulario
if [ -f "$VOCAB" ]; then
  echo "🔤 Estado del vocabulario:"
  cat "$VOCAB"
else
  echo "🔤 No hay archivo vocab_clean.txt"
fi

# Promedio de métricas
if [ -f "$METRICS" ]; then
  TOKENS=$(awk -F',' '{sum+=$2; count++} END {if(count>0) print sum/count; else print 0}' "$METRICS")
  LOGIC=$(awk -F',' '{sum+=$3; count++} END {if(count>0) print sum/count; else print 0}' "$METRICS")
  CLARITY=$(awk -F',' '{sum+=$4; count++} END {if(count>0) print sum/count; else print 0}' "$METRICS")
  DEPTH=$(awk -F',' '{sum+=$5; count++} END {if(count>0) print sum/count; else print 0}' "$METRICS")
  NARRATIVE=$(awk -F',' '{sum+=$6; count++} END {if(count>0) print sum/count; else print 0}' "$METRICS")

  echo "📊 Promedio de métricas:"
  echo "   Tokens: $TOKENS | Logic: $LOGIC | Clarity: $CLARITY | Depth: $DEPTH | Narrative: $NARRATIVE"
else
  echo "📊 No existe remi_metrics.csv"
fi

# Conteo de upgrades
if [ -f "$UPGRADES" ]; then
  COUNT=$(grep -c "## REMI_UPGRADE_" "$UPGRADES")
  echo "🔢 Total de upgrades registrados: $COUNT"
else
  echo "🔢 No existe remi_upgrades.md"
fi

echo "=========================="

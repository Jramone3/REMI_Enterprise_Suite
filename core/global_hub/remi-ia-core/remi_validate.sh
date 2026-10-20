#!/usr/bin/env bash
set -euo pipefail

echo "=== REMI VALIDATION PANEL ==="
echo "Fecha: $(date -Is)"
echo ""

LOG="$HOME/documentacion/REMI_repo/REMI_log.txt"

# Validar JSON
for f in ~/documentacion/REMI_repo/*.json; do
  [ -e "$f" ] || continue
  echo "📝 Validando $f (JSON)"
  if jq empty "$f" >/dev/null 2>&1; then
    echo "✅ Archivo válido: $f"
  else
    echo "⚠️ Error en archivo: $f"
  fi
done

# Validar JSONL
for f in ~/documentacion/REMI_repo/*.jsonl; do
  [ -e "$f" ] || continue
  echo "📝 Validando $f (JSONL)"
  jq empty "$f" || echo "⚠️ Error en $f"
done

# Validar Markdown
for f in ~/documentacion/REMI_repo/*.md; do
  [ -e "$f" ] || continue
  echo "📖 Validando $f (Markdown)"
  grep -q "##" "$f" || echo "⚠️ Falta estructura en $f"
done

# Validar CSV
for f in ~/documentacion/REMI_repo/*.csv; do
  [ -e "$f" ] || continue
  echo "📊 Validando $f (CSV)"
  head -n 1 "$f" | grep -q "," || echo "⚠️ Formato incorrecto en $f"
done

echo "$(date -Is) | REMI-Validate | Validación ejecutada" >> "$LOG"
echo "✅ Validación completada."

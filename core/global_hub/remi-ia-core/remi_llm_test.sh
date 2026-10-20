#!/usr/bin/env bash
set -euo pipefail

TS=$(date -Is)
echo "$TS | REMI-LLM | Test de lógica LLM iniciado" >> ~/documentacion/REMI_repo/REMI_log.txt

CORPUS="~/documentacion/REMI_repo/corpus_remi_master.json"

# Validar corpus maestro
if [ -f $CORPUS ]; then
  if jq empty $CORPUS >/dev/null 2>&1; then
    echo "Corpus válido. LLM listo para responder."
  else
    echo "Error: corpus inválido."
  fi
else
  echo "Corpus no encontrado en $CORPUS"
fi

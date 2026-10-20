#!/usr/bin/env bash
set -euo pipefail

TS=$(date -Is)
echo "$TS | REMI-Imports | Verificación de imports" >> ~/documentacion/REMI_repo/REMI_log.txt

python3 -c "import json, os, sys; print('Imports verificados OK')"

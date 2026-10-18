#!/bin/bash

LOG="/home/ramon/REMI_CORE/logs/remi_bridge.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] REMI_BRIDGE: $*" >> "$LOG"

case "$1" in
  start_nucleo)
    nohup python3 /home/ramon/REMI_CORE/remi_core_loader.py >> /home/ramon/REMI_CORE/logs/nucleo.log 2>&1 &
    echo "Núcleo lógico REMI iniciado." >> "$LOG"
    ;;
  stop_motores)
    pkill -f "/home/ramon/REMI_CORE/motores/MOTOR_GLOBAL.py" || true
    pkill -f "/home/ramon/REMI_CORE/motores/minero_local.py" || true
    pkill -f "/home/ramon/REMI_CORE/motores/baliza_fase1.py" || true
    echo "Motores detenidos." >> "$LOG"
    ;;
  *)
    echo "Comando no reconocido: $1" >> "$LOG"
    ;;
esac

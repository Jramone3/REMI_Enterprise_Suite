#!/bin/bash

echo "=== Gestor de Procesos REMI ==="
echo "1) Ver procesos MOTOR_GLOBAL"
echo "2) Ver procesos minero/baliza"
echo "3) Matar todos los motores"
echo "4) Iniciar núcleo lógico"
echo "0) Salir"
read -p "Opción: " op

case "$op" in
  1)
    ps aux | grep MOTOR_GLOBAL | grep -v grep
    ;;
  2)
    ps aux | grep -E "minero_local|baliza_fase1" | grep -v grep
    ;;
  3)
    pkill -f "/mnt/sda7/REMI/motores/MOTOR_GLOBAL.py"
    pkill -f "/mnt/sda7/REMI/motores/minero_local.py"
    pkill -f "/mnt/sda7/REMI/motores/baliza_fase1.py"
    echo "Motores detenidos."
    ;;
  4)
    /mnt/sda7/REMI/remi_bridge.sh start_nucleo
    ;;
  0)
    exit 0
    ;;
  *)
    echo "Opción no válida."
    ;;
esac

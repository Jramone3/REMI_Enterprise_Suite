#!/bin/bash
# Script de encendido para REMI en red local (para Android)

# 1. Definir rutas
BACKEND_DIR="/home/ramon/REMI_CORE/bunker/REMI/ARCHIVOS_PERSONALES_RAMON/Proyecto_Remi_IA_App/REMI_CHATS"
FRONTEND_DIR="/home/ramon/REMI_CORE/bunker/REMI/ARCHIVOS_PERSONALES_RAMON/Proyecto_Remi_IA_App/REMI_CHATS"

echo "Iniciando cerebro en puerto 5000..."
cd $BACKEND_DIR
# Usamos 0.0.0.0 para que el Redmi pueda verlo
nohup python3 server.py --host 0.0.0.0 --port 5000 &

echo "Iniciando interfaz en puerto 3000..."
cd $FRONTEND_DIR
# npm run dev usualmente necesita una variable de entorno para la IP
npm run dev -- --host 0.0.0.0 --port 3000 &

echo "REMI está activo. Conéctate desde tu Redmi a: http://$(hostname -I | awk '{print $1}'):3000"

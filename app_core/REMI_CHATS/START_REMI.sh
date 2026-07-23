#!/bin/bash
echo "🛡️ Iniciando Protocolo de Resurrección de REMI..."

pkill -f REMI_CORE.js

echo "⏳ Verificando Nodo Blockchain..."
nohup npx hardhat node > hardhat_node.log 2>&1 &
sleep 5

# 🔥 ESTA ES LA LÍNEA CRÍTICA
cd /home/ramon/Escritorio/Proyecto_Remi_IA_App/REMI_CHATS

echo "🚀 Lanzando REMI_CORE V3.0..."
nohup node core/REMI_CORE.js > remi_output.log 2>&1 &

echo "✅ REMI está en el aire. Revisa logs con: tail -f remi_output.log"

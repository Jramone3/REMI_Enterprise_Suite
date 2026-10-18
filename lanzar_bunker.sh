#!/bin/bash
export PATH="/home/ramon/.nvm/versions/node/v22.22.3/bin:$PATH"

echo "🚀 Lanzando REMI-AuthBridge (Puerto 3000)..."
cd /home/ramon/REMI_CORE/global_hub/remi-authbridge
nohup PORT=3000 npm run dev -- --webpack > /home/ramon/REMI_CORE/logs/remi-authbridge.log 2>&1 &
disown

echo "🚀 Lanzando REMI-Dashboard (Puerto 3001)..."
cd /home/ramon/REMI_CORE/auditoria_remota/test_remoto/app_core/remi-dashboard
nohup PORT=3001 npm run dev -- --webpack > /home/ramon/REMI_CORE/logs/remi-dashboard.log 2>&1 &
disown

echo "✅ ¡Búnker desplegado y desacoplado con éxito!"

#!/usr/bin/env bash

# ==============================================================================
# REMI ENTERPRISE SUITE - ENVIRONMENT & PORT LAUNCHER
# ==============================================================================

echo "🚀 [SYSTEM_LAUNCH]: Initializing REMI Sovereign Core Environment..."

# Clean target ports to prevent address binding conflicts
echo "🧹 [PORT_CLEANUP]: Flushing binding ports 3000, 3001, and 5000..."
sudo fuser -k 3000/tcp 2>/dev/null
sudo fuser -k 3001/tcp 2>/dev/null
sudo fuser -k 5000/tcp 2>/dev/null

sleep 1

# Launch independent process supervisor in background
echo "🛡️ [SUPERVISOR]: Spawning process supervisor..."
nohup python3 /home/ramon/REMI_CORE/remi_supervisor.py > /home/ramon/REMI_CORE/logs/supervisor.log 2>&1 &

# Launch core API gateway
echo "⚙️ [API_GATEWAY]: Spawning FastAPI backend on port 5000..."
cd /home/ramon/REMI_CORE/auditoria_github/test_github/app_core/REMI_CHATS || exit
nohup python3 server.py > /home/ramon/REMI_CORE/logs/server_5000.log 2>&1 &

echo "✅ [SUCCESS]: Environment deployment sequence executed. Verify telemetry in /home/ramon/REMI_CORE/logs/"

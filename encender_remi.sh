#!/usr/bin/env bash

# ==============================================================================
# REMI CORE QUICK STARTUP DAEMON
# ==============================================================================

echo "⚡ [EXECUTION]: Initiating REMI Core local startup..."

# Verify Ollama service instance
if ! pgrep -x "ollama" > /dev/null; then
    echo "⚠️ [LLM_ENGINE]: Ollama daemon inactive. Starting service..."
    ollama serve > /dev/null 2>&1 &
    sleep 2
fi

# Pre-load qwen2.5:3b model instance into memory
echo "🧠 [RAM_LOAD]: Pre-loading qwen2.5:3b model into system memory..."
ollama run qwen2.5:3b "" > /dev/null 2>&1 &

# Start Backend Gateway
echo "🌐 [BACKEND]: Starting API Gateway server..."
cd /home/ramon/REMI_CORE/auditoria_github/test_github/app_core/REMI_CHATS || exit
sudo fuser -k 5000/tcp 2>/dev/null
python3 server.py

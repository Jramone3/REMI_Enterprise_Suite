#!/bin/bash
# REMI_CORE - REA MCP Launcher (Reverse Engineer Anything)
# Módulo de Análisis e Ingeniería Inversa Liviana (JavaScript / Web / Apps)

LOG_FILE="/home/ramon/REMI_CORE/modules/remi-mcp-rea/logs/rea_mcp.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Iniciando Servidor MCP REA en modo estándar..." >> "$LOG_FILE"

# Ejecución oficial del servidor MCP de REA con la bandera --mcp
exec npx -y rea-agents --mcp >> "$LOG_FILE" 2>&1

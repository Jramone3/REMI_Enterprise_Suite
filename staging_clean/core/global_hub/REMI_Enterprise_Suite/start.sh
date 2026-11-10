#!/bin/bash

echo "🛡️ [REMI BÚNKER] Iniciando sistemas..."

# 1. Iniciar el micro-servicio Flask en el puerto 5001 en segundo plano
echo "🚀 Levantando API de Auditoría S3 (Puerto 5001)..."
python3 app.py &
API_PID=$!

# Breve pausa para asegurar que Flask arranque bien
sleep 1

# 2. Iniciar el servidor web estático para la interfaz en el puerto 8000 en segundo plano
echo "🌐 Levantando Landing Page (Puerto 8000)..."
python3 -m http.server 8000 &
WEB_PID=$!

# 3. Disparar el patrullaje de repositorios en segundo plano al arrancar
echo "👁️‍🗨️ [REMI-MARKET] Lanzando patrullaje inicial de despliegues..."
python3 REMI_CHATS/remi_market_monitor.py &

echo "---------------------------------------------------"
echo "🟢 ¡Sistemas operativos!"
echo "👉 Interfaz Web: http://localhost:8000"
echo "👉 API Backend:  http://localhost:5001/audit"
echo "👉 Estadísticas: http://localhost:5001/stats"
echo "---------------------------------------------------"
echo "Presiona [CTRL+C] para apagar todos los servicios del búnker."

# Mantener el script vivo y capturar la salida para cerrar ambos procesos si se interrumpe
trap "kill $API_PID $WEB_PID; echo '🛑 Búnker apagado correctamente.'; exit" INT
wait

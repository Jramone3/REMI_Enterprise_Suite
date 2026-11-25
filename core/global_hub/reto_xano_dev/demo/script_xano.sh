#!/bin/bash
# Demo script for Reto Xano/Dev
# Español: Ejecuta pruebas rápidas de los endpoints en Xano.
# English: Runs quick tests of the Xano endpoints.

echo "🚀 Iniciando demo del reto Xano/Dev..."
echo "Testing authentication endpoint..."
curl -X POST https://xano.example.com/api/auth -d '{"user":"demo","password":"demo"}'

echo "Testing event log endpoint..."
curl -X GET https://xano.example.com/api/event_logs

echo "✅ Demo completada."

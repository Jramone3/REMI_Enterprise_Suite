#!/bin/bash
# Demo script for Dosier Next.js Problemas
# Español: Ejecuta pruebas rápidas de configuración y rutas en Next.js.
# English: Runs quick tests of configuration and routes in Next.js.

echo "🚀 Iniciando demo del dosier Next.js..."
echo "Testing dynamic route..."
curl -X GET http://localhost:3000/api/test-route

echo "Testing API integration..."
curl -X GET http://localhost:3000/api/external

echo "✅ Demo completada."

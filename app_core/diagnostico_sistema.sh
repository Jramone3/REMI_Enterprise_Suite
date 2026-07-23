#!/bin/bash
echo "--- DIAGNÓSTICO BÚNKER (sda7) y NÚCLEO (sda5) ---"

# Rutas críticas en sda7 (Depósito)
deposito=(
    "/home/ramon/Escritorio/Proyecto_Remi_IA_App/REMI_CHATS/corpus_remi_master.json"
    "/home/ramon/Escritorio/Proyecto_Remi_IA_App/REMI_BLACKBOX"
)

# Rutas críticas en sda5 (Sistema) - Ajusta según donde monte tu sistema el sda5
nucleo=(
    "/bin/bash"
    "/usr/bin/python3"
)

echo "Verificando Depósito (sda7)..."
for path in "${deposito[@]}"; do
    [ -e "$path" ] && echo "✅ $path" || echo "❌ $path NO ENCONTRADO"
done

echo "Verificando Núcleo (sda5)..."
df -h | grep sda5

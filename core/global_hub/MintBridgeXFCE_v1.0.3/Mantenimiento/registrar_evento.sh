#!/bin/bash
echo "📋 Registrando evento técnico..."
read -p "📝 Descripción del evento: " evento
fecha=$(date '+%Y-%m-%d %H:%M:%S')
echo "$fecha – $evento" >> ~/MintBridgeXFCE_v1.0.3/Mantenimiento/log_mantenimiento.txt
echo "✅ Evento registrado en log_mantenimiento.txt"

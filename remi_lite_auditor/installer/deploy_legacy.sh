#!/bin/bash
echo "=================================================="
echo "🛡️ INSTALANDO REMI-LITE AUDIT EDITION (Legacy Systems)"
echo "=================================================="

# Crear entorno virtual ligero optimizado para bajo consumo
python3 -m venv .venv_legacy
source .venv_legacy/bin/activate

# Actualizar pip localmente
pip install --upgrade pip

# Instalar dependencias mínimas
pip install -e .

echo "=================================================="
echo "✅ ¡Instalación completada con éxito!"
echo "Para ejecutar la auditoría en este equipo, usa:"
echo "  source .venv_legacy/bin/activate && remi-audit"
echo "=================================================="

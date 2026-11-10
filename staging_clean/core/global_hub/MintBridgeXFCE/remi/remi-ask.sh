#!/bin/bash
# REMI Ask – Preguntas frecuentes

echo "🧠 REMI: Preguntas frecuentes"
echo "1. ¿Qué es MintBridgeXFCE?"
echo "2. ¿Cómo valido un archivo?"
echo "3. ¿Qué significa trazabilidad patrimonial?"
read -p "Selecciona una opción (1-3): " opt

case $opt in
  1) echo "MintBridgeXFCE es un toolkit modular para migraciones éticas en sistemas XFCE." ;;
  2) echo "Usa remi-core.py para calcular el hash SHA256 y registrar en remi-log.md." ;;
  3) echo "Trazabilidad patrimonial es el registro técnico y ético de cada acción digital." ;;
  *) echo "Opción no válida." ;;
esac

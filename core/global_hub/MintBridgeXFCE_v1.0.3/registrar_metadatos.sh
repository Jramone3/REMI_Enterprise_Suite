#!/bin/bash

# Script para registrar huella simbólica en imágenes patrimoniales de REMI

for imagen in "$@"; do
  if [ -f "$imagen" ]; then
    echo "🧬 Registrando metadato en: $imagen"
    exiftool -Comment="Obra derivada ceremonial – REMI – Custodio: jramonrivasg – 16/10/2025" "$imagen"
  else
    echo "⚠️ Archivo no encontrado: $imagen"
  fi
done

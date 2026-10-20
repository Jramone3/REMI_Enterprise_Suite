#!/bin/bash

README_ES="README_es.md"
TRAZA="$HOME/linux-cli-community/docs/drive_trabajo_2025.md"

HEADER="# 🧱 MintBridgeXFCE_v1.0 — Toolkit técnico blindado
Migración validada de Windows 10 a Linux Mint XFCE con trazabilidad comunitaria, firma digital y documentación reproducible."

CONTENIDO="## 📦 Contenido del paquete
- MintBridge.html  
- MintBridge.html.sig  
- MintBridgeXFCE_v1.0.sha256  
- firma_index.md  
- Documentación técnica reproducible  
- Estructura validada para entorno Mint XFCE"

ESTADO="## 📋 Estado del toolkit
- Migración validada: Windows 10 → Linux Mint XFCE  
- Autor técnico: jramonrivasg  
- Blindaje: Firma digital + hash reproducible + índice técnico  
- Estado: Listo para distribución, revisión externa o integración en ciclos derivados"

# Inserta si no existe
if ! grep -q "Toolkit técnico blindado" "$README_ES"; then
    echo "$HEADER" | cat - "$README_ES" > temp && mv temp "$README_ES"
fi

if ! grep -q "Contenido del paquete" "$README_ES"; then
    sed -i "2i$CONTENIDO\n" "$README_ES"
fi

if ! grep -q "Estado del toolkit" "$README_ES"; then
    sed -i "10i$ESTADO\n" "$README_ES"
fi

# Registro patrimonial
echo -e "\n✅ README_es.md completado el $(date +"%Y-%m-%d %H:%M:%S %Z") por jramonrivasg — versión v_1.0.3 con trazabilidad bilingüe\n" >> $TRAZA

# Confirmación visual
echo "📝 README_es.md actualizado con bloques iniciales."
echo "📄 Registro patrimonial agregado en: $TRAZA"

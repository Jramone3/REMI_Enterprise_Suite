#!/bin/bash

# Rutas
README_ES="README_es.md"
README_EN="README_en.md"
TRAZA="$HOME/linux-cli-community/docs/drive_trabajo_2025.md"

# Crear archivos si no existen
touch "$README_ES"
touch "$README_EN"

# Bloques en español
HEADER_ES="# 🧱 MintBridgeXFCE_v1.0 — Toolkit técnico blindado
Migración validada de Windows 10 a Linux Mint XFCE con trazabilidad comunitaria, firma digital y documentación reproducible."

CONTENIDO_ES="## 📦 Contenido del paquete
- MintBridge.html  
- MintBridge.html.sig  
- MintBridgeXFCE_v1.0.sha256  
- firma_index.md  
- Documentación técnica reproducible  
- Estructura validada para entorno Mint XFCE"

ESTADO_ES="## 📋 Estado del toolkit
- Migración validada: Windows 10 → Linux Mint XFCE  
- Autor técnico: jramonrivasg  
- Blindaje: Firma digital + hash reproducible + índice técnico  
- Estado: Listo para distribución, revisión externa o integración en ciclos derivados"

# Bloques en inglés
HEADER_EN="# 🧱 MintBridgeXFCE_v1.0 — Hardened Technical Toolkit
Validated migration from Windows 10 to Linux Mint XFCE, with community traceability, digital signing, and reproducible documentation."

CONTENIDO_EN="## 📦 Package Contents
- MintBridge.html  
- MintBridge.html.sig  
- MintBridgeXFCE_v1.0.sha256  
- firma_index.md  
- Reproducible technical documentation  
- Validated structure for Mint XFCE environments"

ESTADO_EN="## 📋 Toolkit Status
- Validated migration: Windows 10 → Linux Mint XFCE  
- Technical author: jramonrivasg  
- Hardening: Digital signature + reproducible hash + technical index  
- Status: Ready for distribution, external review, or integration into derivative cycles"

# Función para insertar bloques si faltan
insert_blocks() {
  local file="$1"
  local header="$2"
  local content="$3"
  local status="$4"

  if ! grep -q "🧱" "$file"; then
    echo "$header" | cat - "$file" > temp && mv temp "$file"
  fi

  if ! grep -q "📦" "$file"; then
    sed -i "2i$content\n" "$file"
  fi

  if ! grep -q "📋" "$file"; then
    sed -i "10i$status\n" "$file"
  fi
}

# Insertar en ambos archivos
insert_blocks "$README_ES" "$HEADER_ES" "$CONTENIDO_ES" "$ESTADO_ES"
insert_blocks "$README_EN" "$HEADER_EN" "$CONTENIDO_EN" "$ESTADO_EN"

# Registro patrimonial
echo -e "\n✅ README_es.md y README_en.md sincronizados el $(date +"%Y-%m-%d %H:%M:%S %Z") por jramonrivasg — trazabilidad bilingüe v_1.0.3\n" >> "$TRAZA"

# Confirmación
echo "📝 Archivos README_es.md y README_en.md actualizados y sincronizados."
echo "📄 Registro patrimonial agregado en: $TRAZA"

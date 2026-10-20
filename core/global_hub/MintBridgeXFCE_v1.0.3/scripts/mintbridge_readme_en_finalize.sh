#!/bin/bash

README_EN="README_en.md"
TRAZA="$HOME/linux-cli-community/docs/drive_trabajo_2025.md"

HEADER="# 🧱 MintBridgeXFCE_v1.0 — Hardened Technical Toolkit
Validated migration from Windows 10 to Linux Mint XFCE, with community traceability, digital signing, and reproducible documentation."

CONTENTS="## 📦 Package Contents
- MintBridge.html  
- MintBridge.html.sig  
- MintBridgeXFCE_v1.0.sha256  
- firma_index.md  
- Reproducible technical documentation  
- Validated structure for Mint XFCE environments"

STATUS="## 📋 Toolkit Status
- Validated migration: Windows 10 → Linux Mint XFCE  
- Technical author: jramonrivasg  
- Hardening: Digital signature + reproducible hash + technical index  
- Status: Ready for distribution, external review, or integration into derivative cycles"

# Insert if missing
if ! grep -q "Hardened Technical Toolkit" "$README_EN"; then
    echo "$HEADER" | cat - "$README_EN" > temp && mv temp "$README_EN"
fi

if ! grep -q "Package Contents" "$README_EN"; then
    sed -i "2i$CONTENTS\n" "$README_EN"
fi

if ! grep -q "Toolkit Status" "$README_EN"; then
    sed -i "10i$STATUS\n" "$README_EN"
fi

# Register in traceability log
echo -e "\n✅ README_en.md finalized on $(date +"%Y-%m-%d %H:%M:%S %Z") by jramonrivasg — bilingual traceability for v_1.0.3\n" >> $TRAZA

# Confirmation
echo "📝 README_en.md updated with initial blocks."
echo "📄 Traceability registered in: $TRAZA"

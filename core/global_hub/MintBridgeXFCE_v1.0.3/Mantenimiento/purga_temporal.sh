#!/bin/bash
echo "🧼 Purgando archivos temporales..."
find ../PublicacionFormal -type f \( -name "*.bak" -o -name "*.tmp" -o -name "*.log" \) -exec rm -v {} \;
echo "✅ Purga completada."

#!/bin/bash
echo "📦 Empaquetando MintBridgeXFCE v-1.0.3..."
cd ~
zip -r MintBridgeXFCE_v1.0.3.zip MintBridgeXFCE_v1.0.3
tar -czvf MintBridgeXFCE_v1.0.3.tar.gz MintBridgeXFCE_v1.0.3
echo "✅ Archivos .zip y .tar.gz generados."

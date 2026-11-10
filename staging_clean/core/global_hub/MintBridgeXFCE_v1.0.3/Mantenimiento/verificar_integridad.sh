#!/bin/bash
echo "🔐 Verificando firma GPG..."
gpg --verify ../PublicacionFormal/MintBridgeXFCE_v1.0.3.sig ../PublicacionFormal/MintBridgeXFCE_v1.0.3.html

echo "🔍 Verificando hash SHA256..."
sha256sum -c ../PublicacionFormal/MintBridgeXFCE_v1.0.3.sha256

#!/bin/bash
echo "🔍 Auditando permisos de ejecución..."
find ~/MintBridgeXFCE_v1.0.3 -type f ! -perm -u=x -exec ls -l {} \;
echo "✅ Auditoría completada."

# Verificacion.ps1 – Validación de firmas digitales en MintBridge XFCE v1.0
# Autor: "jramonrivasg"
# Fecha: 2025-08-29

Write-Host "🔍 Iniciando verificación de integridad..."
Start-Sleep -Seconds 2

# Verificar firma de Migracion.ps1
gpg --verify "Migracion.ps1.sig" "Migracion.ps1"

# Verificar firma de Blindaje.ps1
gpg --verify "Blindaje.ps1.sig" "Blindaje.ps1"

# Mostrar resultado
Write-Host "✅ Archivo A completada. Revise mensajes de GPG para confirmar validez."


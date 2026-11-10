# Blindaje.ps1 – Refuerzo de seguridad para entorno MintBridge XFCE v1.0
# Autor: "jramonrivasg"
# Fecha: 2025-08-29

Write-Host "🔐 Iniciando blindaje del entorno..."
Start-Sleep -Seconds 2

# Crear carpeta de respaldo cifrado
$destino = "D:\Blindaje_Cifrado"
New-Item -ItemType Directory -Path $destino -Force

# Comprimir y cifrar carpeta de documentos
$origen = "$env:USERPROFILE\Documents"
$archivoZip = "$destino\respaldo.zip"
Compress-Archive -Path $origen\* -DestinationPath $archivoZip

# Cifrar con GPG
$clave = "jramonrivasg_publickey.asc"
gpg --encrypt --recipient "jramonrivasg" --output "$archivoZip.gpg" "$archivoZip"

# Eliminar archivo sin cifrar
Remove-Item $archivoZip

Write-Host "✅ Blindaje completado. Archivo cifrado en: $archivoZip.gpg"
Read-Host -Prompt "Presiona Enter para salir"
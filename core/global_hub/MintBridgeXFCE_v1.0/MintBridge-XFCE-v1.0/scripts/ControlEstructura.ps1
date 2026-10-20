# ControlEstructura.ps1 – Validación de estructura modular MintBridge XFCE v1.0
# Autor: "jramonrivasg"
# Fecha: 2025-08-29

Write-Host "📂 Iniciando control de estructura del proyecto..."
Start-Sleep -Seconds 2

# Verificar existencia de carpetas clave
$carpetas = @("scripts", "documentacion", "firma")
foreach ($carpeta in $carpetas) {
    if (-Not (Test-Path $carpeta)) {
        Write-Host "❌ Falta la carpeta: $carpeta" -ForegroundColor Red
    } else {
        Write-Host "✅ Carpeta encontrada: $carpeta"
    }
}

# Verificar archivos obligatorios en raíz
$archivos = @("instrucciones.txt", "estructura.txt", "README.md", "LICENSE.txt")
foreach ($archivo in $archivos) {
    if (-Not (Test-Path $archivo)) {
        Write-Host "❌ Falta el archivo: $archivo" -ForegroundColor Red
    } else {
        Write-Host "✅ Archivo presente: $archivo"
    }
}

Write-Host "📋 Validación de estructura completada."
Read-Host "Presiona Enter para salir"

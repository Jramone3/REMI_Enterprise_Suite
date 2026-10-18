# Migracion.ps1 - Script de migración para MintBridge XFCE v1.0
# Autor: "jramonrivasg"
# Fecha: 2025-08-29

Write-Host "Iniciando migración del entorno Windows a Linux Mint XFCE..."
Start-Sleep -Seconds 2

# Verificar requisitos mínimos
$ram = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB
if ($ram -lt 4) {
    Write-Host "⚠️ RAM insuficiente: Se requieren al menos 4GB." -ForegroundColor Red
    exit
} else {
    Write-Host ("Memoria detectada: {0:N2} GB" -f $ram)
}

# Exportar lista de programas instalados
Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* |
    Select-Object DisplayName, DisplayVersion |
    Out-File "$env:USERPROFILE\programas_instalados.txt" -Encoding UTF8

Write-Host "✅ Lista de programas exportada correctamente."
Start-Sleep -Seconds 1

# Crear respaldo de documentos
$origen = "$env:USERPROFILE\Documents"
$destino = "D:\Respaldo_Migracion"
New-Item -ItemType Directory -Path $destino -Force | Out-Null

try {
    Copy-Item -Path "$origen\*" -Destination $destino -Recurse -ErrorAction Stop
    Write-Host "📁 Documentos respaldados en: $destino"
} catch {
    Write-Host "❌ Error al copiar documentos: $($_.Exception.Message)" -ForegroundColor Red
}

Start-Sleep -Seconds 1
Write-Host "✅ Migración completada. Proceda con instalación de Linux Mint XFCE."

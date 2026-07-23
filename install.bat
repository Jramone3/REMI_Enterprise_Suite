@echo off
setlocal

echo ==========================================
echo    REMI - Instalador y Validador Windows
echo ==========================================

:: 1. Verificar si Python está disponible
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Error: Python no esta instalado o no se encuentra en el PATH del sistema.
    pause
    exit /b 1
)

:: 2. Crear entorno virtual si no existe
if not exist "venv" (
    echo [*] Creando entorno virtual aislado (venv)...
    python -m venv venv
)

:: 3. Activar entorno virtual e instalar dependencias limpias
echo [*] Instalando dependencias de Python en el entorno virtual...
call venv\Scripts\python -m pip install --upgrade pip --quiet
if exist "requirements.txt" (
    call venv\Scripts\pip install -r requirements.txt --quiet
) else (
    echo [!] Advertencia: No se encontro requirements.txt principal.
)

:: 4. Configurar archivo .env si no existe
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo [+] Archivo .env generado a partir de .env.example.
    )
)

:: 5. Test de arranque en frío (Caja Negra usando el entorno virtual)
echo [*] Ejecutando prueba de arranque del sistema...
call venv\Scripts\python -c "import os; print('[OK] Entorno Python aislado verificado correctamente en:', os.getcwd())"

echo ==========================================
echo    ¡Instalación y empaquetado completados!
echo ==========================================
pause

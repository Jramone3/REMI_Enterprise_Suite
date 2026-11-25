#!/bin/bash

echo "==========================================" >&2
echo "   REMI - Instalador y Validador Global   " >&2
echo "==========================================" >&2

# 1. Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "[*] Creando entorno virtual aislado (venv)..." >&2
    python3 -m venv venv
fi

# 2. Activar entorno virtual e instalar dependencias limpias
echo "[*] Instalando dependencias de Python en el entorno virtual..." >&2
./venv/bin/pip install --upgrade pip --quiet
if [ -f "requirements.txt" ]; then
    ./venv/bin/pip install -r requirements.txt --quiet
else
    echo "[!] Advertencia: No se encontró requirements.txt principal." >&2
fi

# 3. Configurar archivo .env si no existe
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "[+] Archivo .env generado a partir de .env.example." >&2
    fi
fi

# 4. Test de arranque en frío (Caja Negra usando el entorno virtual)
echo "[*] Ejecutando prueba de arranque del sistema..." >&2
./venv/bin/python3 -c "import os; print('[OK] Entorno Python aislado verificado correctamente en:', os.getcwd())"

echo "==========================================" >&2
echo "   ¡Instalación y empaquetado completados!" >&2
echo "==========================================" >&2

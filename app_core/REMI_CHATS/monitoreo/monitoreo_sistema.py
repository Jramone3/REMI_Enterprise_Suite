import psutil
import os
import platform
import subprocess

def verificar_modo_ro():
    try:
        output = subprocess.check_output(['mount']).decode('utf-8')
        for linea in output.split('\n'):
            if '/dev/sda5' in linea and 'ro' in linea:
                return True
    except:
        pass
    return False

modo_ro = verificar_modo_ro()
if modo_ro:
    print('\n🚨 ALERTA ROJA: /dev/sda5 está en modo READ-ONLY.')
else:
    print('\n✅ SISTEMA NOMINAL: sda5 en modo RW.')
    print(f'Memoria RAM: {psutil.virtual_memory().percent}%')
    print(f'Carga CPU: {psutil.cpu_percent()}%')

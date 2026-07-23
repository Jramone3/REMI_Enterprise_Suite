import os
import time

# Configuración de la función de logeo
def log_de_bloqueo(mensaje):
    with open('defensa_log.txt', 'a') as f:
        f.write(f'{time.strftime("%Y-%m-%d %H:%M:%S")} - {mensaje}\n')

# Configuración de la función de bloqueo
def bloquear_conexion(ip):
    # Bloquear la conexión mediante ufw
    os.system('sudo ufw deny from ' + ip + ' to any')
    log_de_bloqueo(f'Bloqueada la conexión de {ip}')

# Configuración de la función de desbloqueo
def desbloquear_conexion(ip):
    # Desbloquear la conexión mediante ufw
    os.system('sudo ufw allow from ' + ip + ' to any')
    log_de_bloqueo(f'Desbloqueada la conexión de {ip}')

# Configuración de la función de detección de intrusos
def detectar_intrusos():
    # Detección de intrusos mediante el uso de la herramienta 'netstat'
    os.system('sudo netstat -tulpn | grep LISTEN')
    log_de_bloqueo('Detección de intrusos en curso...')

# Configuración de la función de eliminación de procesos
def eliminar_procesos():
    # Eliminación de procesos mediante el uso de la herramienta 'pkill'
    os.system('sudo pkill -9 firefox')
    log_de_bloqueo('Eliminación de procesos en curso...')

# Configuración de la función de eliminación de archivos
def eliminar_archivos():
    # Eliminación de archivos mediante el uso de la herramienta 'rm'
    os.system('sudo rm -rf /tmp/*')
    log_de_bloqueo('Eliminación de archivos en curso...')

# Configuración de la función de neutralización de malware
def neutralizar_malware():
    # Neutralización de malware mediante el uso de la herramienta 'rm'
    os.system('sudo rm -rf /tmp/malware')
    log_de_bloqueo('Neutralización de malware en curso...')

# Configuración de la función de defensa
def defensa():
    # Detección de intrusos
    detectar_intrusos()
    # Bloquear conexiones
    bloquear_conexion('192.168.1.100')
    # Eliminar procesos
    eliminar_procesos()
    # Eliminar archivos
    eliminar_archivos()
    # Neutralizar malware
    neutralizar_malware()

# Configuración de la función de inicio
def inicio():
    # Inicio de la defensa
    defensa()
    # Inicio del logeo
    log_de_bloqueo('Inicio de la defensa del búnker...')

# Inicio del script
inicio()
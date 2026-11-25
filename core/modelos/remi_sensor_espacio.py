import shutil
import datetime
import os

def verificar_patrimonio():
    puntos_montaje = {
        'sda5_CORE': '/',
        'sda7_BUNKER': '/mnt/sda7'
    }
    log_path = '/home/ramon/REMI_CORE/modelos/remi_espacio.log'
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with open(log_path, 'a') as f:
        f.write(f'--- REMI SENSING: {timestamp} ---\n')
        for etiqueta, ruta in puntos_montaje.items():
            if os.path.exists(ruta):
                total, usado, libre = shutil.disk_usage(ruta)
                f.write(f'{etiqueta}: {libre // (1024**3)} GB disponibles de {total // (1024**3)} GB total.\n')
            else:
                f.write(f'{etiqueta}: RUTA NO DETECTADA O DESMONTADA.\n')
        f.write('ESTADO: Verificación completada.\n\n')

if __name__ == '__main__':
    verificar_patrimonio()
import os
import time
import shutil

CARPETA_BLUETOOTH = os.path.expanduser("~/Descargas")
CARPETA_PROCESADOS = os.path.expanduser("~/Descargas/PROCESADOS")

# Crear carpeta de procesados si no existe
if not os.path.exists(CARPETA_PROCESADOS):
    os.makedirs(CARPETA_PROCESADOS)

def monitorear_archivos():
    print("REMI: Monitoreando carpeta de archivos...")
    # Ignoramos lo que ya está ahí para no procesar el pasado
    archivos_conocidos = set(os.listdir(CARPETA_BLUETOOTH))
    
    while True:
        time.sleep(5)
        archivos_actuales = set(os.listdir(CARPETA_BLUETOOTH))
        nuevos = archivos_actuales - archivos_conocidos
        
        for archivo in nuevos:
            # Evitamos procesar la carpeta misma
            if archivo == "PROCESADOS":
                continue
                
            ruta_origen = os.path.join(CARPETA_BLUETOOTH, archivo)
            ruta_destino = os.path.join(CARPETA_PROCESADOS, archivo)
            
            print(f"REMI: ¡Nuevo archivo detectado! Procesando: {archivo}")
            
            try:
                # Mover el archivo
                shutil.move(ruta_origen, ruta_destino)
                print(f"REMI: Archivo {archivo} movido a PROCESADOS.")
            except Exception as e:
                print(f"REMI: Error al mover {archivo}: {e}")
            
        archivos_conocidos = set(os.listdir(CARPETA_BLUETOOTH))

if __name__ == "__main__":
    monitorear_archivos()

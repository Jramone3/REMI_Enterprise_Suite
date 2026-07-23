import os
import json
import time
from pymongo import MongoClient

# CONFIGURACIÓN DE RUTAS
RUTAS = {
    "DESPENSA": "os.path.expanduser("~/") + REMI_CORE/bunker/REMI/ARCHIVOS_PERSONALES_RAMON/Proyecto_Remi_IA_App/REMI_CHATS/index_patrimonial.json",
    "LOGS": "os.path.expanduser("~/") + REMI_CORE/bunker/REMI/ARCHIVOS_PERSONALES_RAMON/Proyecto_Remi_IA_App/logs_remi_mongo.txt"
}

def validar_y_limpiar_items(items: list[dict]) -> list[dict]:
    """
    Pre-procesa los archivos garantizando unicidad por nombre,
    limpiando cadenas y corrigiendo las rutas de /mnt/sda7/ al montaje real.
    """
    items_limpios = []
    nombres_vistos = set()

    for index, item in enumerate(items, start=1):
        nombre_crudo = item.get("nombre", "")
        if not nombre_crudo or str(nombre_crudo).strip().lower() in ["", "none", "null", "undefined"]:
            continue
        nombre_limpio = str(nombre_crudo).strip()

        if nombre_limpio.lower() in nombres_vistos:
            continue
        nombres_vistos.add(nombre_limpio.lower())

        # SOLUCIÓN MODERNA: Traducir la ruta teórica a la ruta real del Búnker
        ruta_cruda = item.get("ruta", "Desconocida")
        ruta_real = ruta_cruda.replace("/mnt/sda7/", "os.path.expanduser("~/") + REMI_CORE/bunker/REMI/")

        item_validado = {
            "nombre": nombre_limpio,
            "ruta": ruta_real,  # Guardamos la ruta corregida y funcional
            "tamano_bytes": item.get("tamano_bytes", 0),
            "modificado": item.get("modificado", ""),
            "sincronizado_el": time.ctime(),
            "estado": "Catalogado"
        }
        items_limpios.append(item_validado)

    return items_limpios

class PipelineREMMongo:
    def __init__(self):
        # Conexión por defecto a tu MongoDB local (localhost:27017)
        self.client = MongoClient("mongodb://localhost:27017/")
        # Creamos/usamos la base de datos 'bunker_db'
        self.db = self.client["bunker_db"]
        # Creamos/usamos la colección 'archivos'
        self.collection = self.db["archivos"]

    def log(self, mensaje):
        try:
            with open(RUTAS["LOGS"], "a", encoding="utf-8") as f:
                f.write(f"[{time.ctime()}] {mensaje}\n")
        except Exception as e:
            print(f"⚠️ No se pudo escribir en el log local: {str(e)}")
        print(f"📡 {mensaje}")

    def ejecutar(self):
        self.log("📥 INICIANDO PIPELINE DE DATOS - MODO MONGODB LOCAL")
        try:
            if not os.path.exists(RUTAS["DESPENSA"]):
                raise FileNotFoundError(f"No se encontró el índice patrimonial en: {RUTAS['DESPENSA']}")

            with open(RUTAS["DESPENSA"], "r", encoding="utf-8") as f:
                datos_bunker = json.load(f)
            
            items_brutos = datos_bunker.get("archivos", [])
            self.log(f"Extracción exitosa: {len(items_brutos)} elementos detectados en el JSON.")

            # --- LIMPIEZA Y VALIDACIÓN ---
            items_procesados = validar_y_limpiar_items(items_brutos)
            self.log(f"Limpieza completada: {len(items_procesados)} elementos únicos listos para almacenar.")

            if not items_procesados:
                self.log("⚠️ No hay elementos nuevos o válidos para insertar.")
                return

            # --- INYECCIÓN EN MONGODB (OPERACIÓN MASIVA EFICIENTE) ---
            self.log("⚡ Insertando registros de forma masiva en MongoDB...")
            
            # Limpiamos registros viejos antes de re-indexar para evitar duplicados en la base de datos
            self.collection.delete_many({})
            
            # Inserta todos los miles de registros en un solo viaje ultrarrápido
            resultado = self.collection.insert_many(items_procesados)
            
            self.log(f"✅ ÉXITO TOTAL: Se han inyectado {len(resultado.inserted_ids)} registros en MongoDB local.")
            self.log("MISIÓN CUMPLIDA: El Búnker local está sincronizado y REMI ya tiene memoria interna.")
            
        except Exception as e:
            self.log(f"🚨 ERROR EN EL PIPELINE MONGO: {str(e)}")
        finally:
            self.client.close()

if __name__ == "__main__":
    motor_mongo = PipelineREMMongo()
    motor_mongo.ejecutar()

import sys
from pymongo import MongoClient

print("--- ESCÁNER DE MAPAS DE ALTA PRIORIDAD (CLUSTER0) ---")
usuario = input("Usuario: ").strip()
password = input("Contraseña: ").strip()

MONGO_URI = f"mongodb+srv://{usuario}:{password}@cluster0.loewdkg.mongodb.net/?appName=Cluster0"

try:
    print("\n[CONEXIÓN] Conectando para escanear estructura completa...")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    
    # Listar todas las bases de datos en tu clúster
    lineas_bd = client.list_database_names()
    
    print("\n==================================================")
    print("   ESTRUCTURA REAL DE TU BASE DE DATOS EN LA NUBE")
    print("==================================================")
    
    total_descubierto = 0
    for nombre_bd in lineas_bd:
        # Ignorar las bases de datos por defecto del sistema de Mongo
        if nombre_bd in ['admin', 'local', 'config']:
            continue
            
        print(f"\n📂 Base de Datos Encontrada: [{nombre_bd}]")
        db = client[nombre_bd]
        colecciones = db.list_collection_names()
        
        if not colecciones:
            print("   └── (Esta base de datos no tiene colecciones activas)")
        
        for col_name in colecciones:
            coleccion = db[col_name]
            conteo_docs = coleccion.count_documents({})
            print(f"   └── 📜 Colección: '{col_name}' -> Contiene: {conteo_docs} documentos reales.")
            total_descubierto += conteo_docs
            
    print("\n==================================================")
    print(f"[FIN DEL ESCANEO] Total de documentos en la nube: {total_descubierto}")
    print("==================================================")

except Exception as e:
    print(f"\n[ERROR]: {e}")

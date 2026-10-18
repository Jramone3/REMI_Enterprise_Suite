import os
from pymongo import MongoClient

usuario = "jramonrivasg_db_user"
password = "Jrrg2026"
MONGO_URI = f"mongodb+srv://{usuario}:{password}@cluster0.loewdkg.mongodb.net/?appName=Cluster0"

try:
    client = MongoClient(MONGO_URI)
    db = client['SISTEMA_REMI']
    coleccion = db['neuronas_esenciales']
    
    ruta = "/home/ramon/REMI_CORE/nucleo_activo/"
    os.makedirs(ruta, exist_ok=True)
    
    # Mapeo de nombres para tus 3 joyas
    nombres = {
        "6999f0bf145c585e9550325d": "remi_puente_xano.py",
        "6999f0bf145c585e9550325c": "remi_escaner_sha256.py",
        "6999f0bf145c585e9550325b": "remi_servidor_api.py"
    }
    
    for doc in coleccion.find({}):
        id_str = str(doc['_id'])
        nombre_archivo = nombres.get(id_str, f"neurona_{id_str}.py")
        contenido = doc.get('contenido') or str(doc)
        
        with open(os.path.join(ruta, nombre_archivo), 'w', encoding='utf-8') as f:
            f.write(contenido)
        print(f"💎 [MATERIALIZADO] -> {nombre_archivo} en sda5.")
        
    print("\n[ÉXITO] Las 3 neuronas esenciales han sido aseguradas localmente.")
except Exception as e:
    print(f"Error: {e}")

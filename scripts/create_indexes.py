from pymongo import MongoClient
import os

def create_db_indexes():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("REMI_DB_NAME", "remi_enterprise")
    
    client = MongoClient(mongo_uri)
    db = client[db_name]
    
    # Crear índice único en tx_hash
    db.licenses.create_index([("tx_hash", 1)], unique=True)
    print("¡Índice único creado exitosamente en remi_enterprise.licenses para tx_hash!")
    client.close()

if __name__ == "__main__":
    create_db_indexes()

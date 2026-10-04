# db.py - Módulo de persistencia optimizado
from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
REMI_DB_NAME = os.getenv("REMI_DB_NAME", "remi_enterprise")

client = MongoClient(MONGO_URI)
db = client[REMI_DB_NAME]
licenses_collection = db["licenses"]

def init_db():
    """Ejecutar al inicio de la aplicación para configurar índices de forma segura y eficiente."""
    try:
        licenses_collection.create_index("tx_hash", unique=True)
        licenses_collection.create_index("email", unique=False)
        print("[DB] Índices de MongoDB inicializados correctamente.")
    except Exception as e:
        print(f"[DB] Error al inicializar índices: {e}")

def save_license(license_data: dict):
    """Guarda una licencia directamente sin sobrecargar con creación de índices por cada inserción."""
    try:
        result = licenses_collection.insert_one(license_data)
        return {"ok": True, "inserted_id": str(result.inserted_id)}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def find_license_by_email(email: str):
    """Busca una licencia registrada por su dirección de correo electrónico."""
    try:
        return licenses_collection.find_one({"email": email}, {"_id": 0})
    except Exception:
        return None

# db.py
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

_client = None
_db = None

def get_client():
    """Retorna el cliente MongoClient para compatibilidad con tests."""
    global _client
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    if _client is None:
        _client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
    return _client

def get_db():
    """Retorna la instancia de la base de datos MongoDB."""
    global _db
    if _db is not None:
        return _db
    client = get_client()
    db_name = os.getenv("MONGO_DB_NAME", "remi_enterprise")
    _db = client[db_name]
    return _db

def init_db():
    """Inicializa la base de datos y aplica índices únicos."""
    db = get_db()
    if db is not None:
        try:
            db.licenses.create_index("tx_hash", unique=True)
            db.licenses.create_index("email", unique=True)
        except Exception as e:
            print(f"Advertencia al crear índices en MongoDB: {e}")

def save_license(license_data: dict) -> dict:
    """Guarda una licencia asegurando unicidad."""
    db = get_db()
    if db is None:
        return {"ok": False, "error": "Base de datos no disponible"}
    try:
        db.licenses.insert_one(license_data)
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def find_license_by_email(email: str):
    db = get_db()
    if db is None:
        return None
    return db.licenses.find_one({"email": email})

def save_audit_log(log_entry: dict):
    db = get_db()
    if db is not None:
        try:
            db.audit_logs.insert_one(log_entry)
        except Exception:
            pass

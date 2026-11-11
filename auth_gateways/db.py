# db.py
import os
from pymongo import MongoClient

_client = None
_db = None

def get_client():
    global _client
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    if _client is None:
        _client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
    return _client

def get_db():
    global _db
    if _db is not None:
        return _db
    client = get_client()
    db_name = os.getenv("MONGO_DB_NAME", "remi_enterprise")
    _db = client[db_name]
    return _db

def ping_db():
    """Ejecuta un ping real al servidor de MongoDB."""
    client = get_client()
    client.admin.command("ping")

def init_db():
    """Comprueba MongoDB mediante ping y crea índices únicos propagando formalmente cualquier error."""
    ping_db()
    db = get_db()
    db.licenses.create_index("tx_hash", unique=True)
    db.licenses.create_index("email", unique=True)

def save_license(license_data: dict) -> dict:
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

def find_license_by_tx_hash(tx_hash: str):
    db = get_db()
    if db is None:
        return None
    return db.licenses.find_one({"tx_hash": tx_hash})

def save_audit_log(log_entry: dict):
    db = get_db()
    if db is not None:
        try:
            db.audit_logs.insert_one(log_entry)
        except Exception:
            pass

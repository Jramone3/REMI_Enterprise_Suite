# db.py
import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

def get_client():
    return MongoClient(MONGO_URI)

def init_db():
    """Inicializa la base de datos y crea los índices únicos necesarios de forma segura."""
    client = get_client()
    db = client["remi_enterprise"]
    try:
        db["licenses"].create_index("tx_hash", unique=True)
        db["licenses"].create_index("email", unique=True)
    except Exception as e:
        print(f"[Aviso DB] Nota al crear índices (posiblemente ya existan): {e}")
    finally:
        client.close()

def save_license(license_data: dict) -> dict:
    client = get_client()
    db = client["remi_enterprise"]
    try:
        db["licenses"].insert_one(license_data)
        return {"ok": True}
    except Exception as e:
        if "duplicate key error" in str(e) or "E11000" in str(e):
            return {"ok": False, "error": "already exists"}
        return {"ok": False, "error": str(e)}
    finally:
        client.close()

def find_license_by_email(email: str):
    client = get_client()
    db = client["remi_enterprise"]
    try:
        return db["licenses"].find_one({"email": email}, {"_id": 0})
    finally:
        client.close()

def save_audit_log(log_entry: dict) -> dict:
    """Guarda un registro de auditoría en la colección audit_logs de la base de datos de manera segura."""
    client = get_client()
    db = client["remi_enterprise"]
    try:
        db["audit_logs"].insert_one(log_entry)
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    finally:
        client.close()

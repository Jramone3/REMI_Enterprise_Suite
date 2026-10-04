# db.py
import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

def get_client():
    return MongoClient(MONGO_URI)

def init_db():
    """Inicializa la base de datos y crea los índices únicos necesarios en el arranque."""
    client = get_client()
    db = client["remi_enterprise"]
    # Crear índices únicos explícitamente en el arranque
    db["licenses"].create_index("tx_hash", unique=True)
    db["licenses"].create_index("email", unique=True)
    client.close()

def save_license(license_data: dict) -> dict:
    client = get_client()
    db = client["remi_enterprise"]
    try:
        db["licenses"].insert_one(license_data)
        return {"ok": True}
    except Exception as e:
        if "duplicate key error" in str(e):
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

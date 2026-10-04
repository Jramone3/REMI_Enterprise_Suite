# db.py - Conexión y gestión de MongoDB optimizada
import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "remi_licenses")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
licenses_collection = db["licenses"]

def init_db():
    """Inicializa índices de MongoDB una sola vez al arrancar la app."""
    try:
        licenses_collection.create_index("tx_hash", unique=True)
        licenses_collection.create_index("email", unique=True)
        print("[DB] Índices de MongoDB inicializados correctamente.")
    except Exception as e:
        print(f"[DB] Error al inicializar índices: {e}")

def save_license(license_data: dict):
    """Guarda una licencia sin sobrecargar con creación repetitiva de índices."""
    return licenses_collection.insert_one(license_data)

def get_license_by_email(email: str):
    try:
        return licenses_collection.find_one({"email": email})
    except Exception:
        return None

# Alias por compatibilidad con tests antiguos si lo requieren
find_license_by_email = get_license_by_email

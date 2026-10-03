import os
from pymongo import MongoClient, errors

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("REMI_DB_NAME", "remi_enterprise")

def get_client():
    return MongoClient(MONGO_URI)

def save_license(record: dict) -> dict:
    client = get_client()
    try:
        coll = client[DB_NAME]["licenses"]
        
        # Asegurar índice único en tx_hash de forma idempotente
        coll.create_index("tx_hash", unique=True)
        
        res = coll.insert_one(record)
        return {"ok": True, "inserted_id": str(res.inserted_id)}
    except errors.DuplicateKeyError:
        return {"ok": False, "error": "already exists"}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    finally:
        client.close()

def find_license_by_email(email: str):
    client = get_client()
    try:
        coll = client[DB_NAME]["licenses"]
        return coll.find_one({"email": email})
    except Exception:
        return None
    finally:
        client.close()

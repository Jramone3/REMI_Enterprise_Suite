from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("REMI_DB_NAME", "remi_enterprise")


def get_client():
    return MongoClient(MONGO_URI)


def save_license(record: dict):
    client = get_client()
    db = client[DB_NAME]
    coll = db["licenses"]
    coll.insert_one(record)
    client.close()


def find_license_by_email(email: str):
    client = get_client()
    db = client[DB_NAME]
    coll = db["licenses"]
    r = coll.find_one({"email": email})
    client.close()
    return r

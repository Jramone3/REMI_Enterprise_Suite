# tests/test_license.py
import sys
import os
from unittest.mock import patch

# Añadir la raíz al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import mongomock

# Parcheamos MongoClient globalmente para que use mongomock en todos los tests de este archivo
with patch("db.MongoClient", mongomock.MongoClient):
    from license_service import app
    from fastapi.testclient import TestClient

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_verify_nonexistent_license():
    with patch("db.MongoClient", mongomock.MongoClient):
        response = client.get("/licenses/verify/fake@client.com")
        assert response.status_code == 404

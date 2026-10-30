# tests/test_license.py
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Añadir la raíz al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from license_service import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_verify_nonexistent_license():
    response = client.get("/licenses/verify/fake@client.com")
    assert response.status_code == 404

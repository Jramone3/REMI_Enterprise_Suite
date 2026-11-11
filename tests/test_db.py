import pytest
from unittest.mock import MagicMock, patch
from auth_gateways.db import init_db, save_license, find_license_by_email, find_license_by_tx_hash

def test_init_db_drops_email_index(monkeypatch):
    mock_db = MagicMock()
    # Simulamos que existe el índice obsoleto email_1 inicialmente, y luego desaparece
    mock_db.licenses.index_information.side_effect = [
        {"_id_": {}, "email_1": {}}, 
        {"_id_": {}, "tx_hash_1": {}}
    ]
    
    monkeypatch.setattr("auth_gateways.db.ping_db", lambda: None)
    monkeypatch.setattr("auth_gateways.db.get_db", lambda: mock_db)

    init_db()
    mock_db.licenses.drop_index.assert_called_once_with("email_1")
    mock_db.licenses.create_index.assert_called_once_with("tx_hash", unique=True)

def test_init_db_fails_if_index_persists(monkeypatch):
    mock_db = MagicMock()
    # Simulamos que el índice email_1 se niega a desaparecer tras el drop_index
    mock_db.licenses.index_information.return_value = {"_id_": {}, "email_1": {}}
    
    monkeypatch.setattr("auth_gateways.db.ping_db", lambda: None)
    monkeypatch.setattr("auth_gateways.db.get_db", lambda: mock_db)

    with pytest.raises(RuntimeError, match="Fallo crítico de migración"):
        init_db()

def test_init_db_fails_on_drop_exception(monkeypatch):
    mock_db = MagicMock()
    mock_db.licenses.index_information.return_value = {"_id_": {}, "email_1": {}}
    # Simulamos que MongoDB lanza una excepción directamente al intentar hacer drop_index (ej. error de permisos o red)
    mock_db.licenses.drop_index.side_effect = Exception("Permisos insuficientes o error de red")
    
    monkeypatch.setattr("auth_gateways.db.ping_db", lambda: None)
    monkeypatch.setattr("auth_gateways.db.get_db", lambda: mock_db)

    with pytest.raises(Exception, match="Permisos insuficientes"):
        init_db()

def test_save_and_find_license(monkeypatch):
    mock_db = MagicMock()
    mock_db.licenses.insert_one.return_value = MagicMock()
    mock_db.licenses.find_one.return_value = {
        "email": "test@remi.com",
        "tx_hash": "0x123",
        "license": "REMI-TEST-123",
        "tier": "enterprise"
    }

    monkeypatch.setattr("auth_gateways.db.get_db", lambda: mock_db)

    res = save_license({"email": "test@remi.com", "tx_hash": "0x123"})
    assert res["ok"] is True

    found_email = find_license_by_email("test@remi.com")
    assert found_email["email"] == "test@remi.com"

    found_tx = find_license_by_tx_hash("0x123")
    assert found_tx["tx_hash"] == "0x123"

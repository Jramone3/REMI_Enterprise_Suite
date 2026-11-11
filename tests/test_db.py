import pytest
from unittest.mock import MagicMock, patch
from auth_gateways.db import init_db

def test_init_db_drops_email_index(monkeypatch):
    mock_db = MagicMock()
    # Simulamos que existe el índice obsoleto email_1 inicialmente, y luego desaparece
    mock_db.licenses.index_information.side_effect = [
        {"_id_": {}, "email_1": {}}, # Primera llamada: existe email_1
        {"_id_": {}, "tx_hash_1": {}} # Segunda llamada post-drop: ya no existe email_1
    ]
    
    monkeypatch.setattr("auth_gateways.db.ping_db", lambda: None)
    monkeypatch.setattr("auth_gateways.db.get_db", lambda: mock_db)

    # Debe ejecutarse con éxito limpiando el índice obsoleto
    init_db()
    mock_db.licenses.drop_index.assert_called_once_with("email_1")
    mock_db.licenses.create_index.assert_called_once_with("tx_hash", unique=True)

def test_init_db_fails_if_index_persists(monkeypatch):
    mock_db = MagicMock()
    # Simulamos que el índice email_1 se niega a desaparecer tras el drop_index
    mock_db.licenses.index_information.return_value = {"_id_": {}, "email_1": {}}
    
    monkeypatch.setattr("auth_gateways.db.ping_db", lambda: None)
    monkeypatch.setattr("auth_gateways.db.get_db", lambda: mock_db)

    # Debe lanzar RuntimeError cumpliendo estrictamente el fail-fast
    with pytest.raises(RuntimeError, match="Fallo crítico de migración"):
        init_db()

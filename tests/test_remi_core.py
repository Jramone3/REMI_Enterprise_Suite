import pytest
from remi_tx_validator import verify_base_transaction

def test_invalid_tx_hash_format():
    """Valida que un hash con formato incorrecto sea rechazado inmediatamente sin llamar al RPC."""
    res = verify_base_transaction("0x1234")
    assert res["valid"] is False
    assert "Formato de Hash" in res["error"]

def test_empty_tx_hash():
    """Valida que una cadena vacía o sin prefijo 0x devuelva error."""
    res = verify_base_transaction("invalid_hash_string")
    assert res["valid"] is False

def test_target_wallet_configuration():
    """Verifica que la dirección corporativa de pago por defecto esté correctamente configurada."""
    from remi_tx_validator import TARGET_WALLET
    expected_wallet = "0x96de980a766ccb10a19b6962587e2b61b650b372"
    assert TARGET_WALLET == expected_wallet

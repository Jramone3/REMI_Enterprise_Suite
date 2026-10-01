from remi_tx_validator import verify_base_transaction

def test_invalid_tx_hash_format():
    """Valida que un hash con formato incorrecto sea rechazado inmediatamente sin llamar al RPC."""
    res = verify_base_transaction("0x1234")
    assert res["valid"] is False
    assert "Tx hash" in res["error"] or "Formato" in res["error"]

def test_empty_tx_hash():
    res = verify_base_transaction("")
    assert res["valid"] is False

def test_none_tx_hash():
    res = verify_base_transaction(None)
    assert res["valid"] is False

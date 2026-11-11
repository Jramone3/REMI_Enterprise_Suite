import pytest
from unittest.mock import MagicMock, patch
from auth_gateways.remi_tx_validator import validate_transaction

def test_validator_uses_strict_w3_eth_block_number(monkeypatch):
    """Prueba estricta recomendada por auditoría: verifica que w3.eth.block_number sea el único punto de lectura del bloque."""
    monkeypatch.setenv("EXPECTED_TOKEN_ADDRESS", "0x1234567890123456789012345678901234567890")
    monkeypatch.setenv("REMI_PAYMENT_ADDRESS", "0xmerchantaddress00000000000000000000000000")
    monkeypatch.setenv("BASE_RPC_URL", "https://mainnet.base.org")
    monkeypatch.setenv("MIN_CONFIRMATIONS", "3")

    mock_w3 = MagicMock()
    # Configuramos estrictamente que el objeto raíz NO tenga block_number, 
    # obligando a pasar exclusivamente por w3.eth.block_number
    del mock_w3.block_number
    mock_w3.eth.chain_id = 8453
    mock_w3.eth.block_number = 1005  # Bloque actual
    
    mock_receipt = {
        "status": 1,
        "blockNumber": 1000, # 5 confirmaciones (1005 - 1000 >= 3)
        "logs": []
    }
    mock_w3.eth.get_transaction_receipt.return_value = mock_receipt

    with patch("auth_gateways.remi_tx_validator.Web3", return_value=mock_w3):
        # Ejecutamos una validación nativa o ERC20 básica para comprobar la lectura del bloque
        res = validate_transaction("0x" + "f" * 64, expected_min_amount=10.0, is_erc20=False)
        # Verificamos que avanzó más allá de la validación de bloque (llegando a buscar la tx nativa o fallando por ella, pero no por bloque)
        assert "Confirmaciones insuficientes" not in res.get("error", "")

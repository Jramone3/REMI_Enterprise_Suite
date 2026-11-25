import pytest
from unittest.mock import MagicMock, patch
from auth_gateways.remi_tx_validator import validate_transaction

def test_validator_uses_strict_w3_eth_block_number(monkeypatch):
    """Prueba estricta y concluyente recomendada por auditoría: verifica aislamiento de w3.eth.block_number con aserción positiva."""
    monkeypatch.setenv("EXPECTED_TOKEN_ADDRESS", "0x1234567890123456789012345678901234567890")
    monkeypatch.setenv("REMI_PAYMENT_ADDRESS", "0xmerchantaddress00000000000000000000000000")
    monkeypatch.setenv("BASE_RPC_URL", "https://mainnet.base.org")
    monkeypatch.setenv("MIN_CONFIRMATIONS", "3")

    mock_w3 = MagicMock()
    # Aislemos estrictamente el objeto raíz de Web3 para que no tenga block_number
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
        tx_hash_test = "0x" + "f" * 64
        res = validate_transaction(tx_hash_test, expected_min_amount=10.0, is_erc20=False)
        
        # Aserción positiva estricta: verificamos fehacientemente que el código superó 
        # la validación del bloque y avanzó hasta invocar get_transaction sobre la red nativa
        mock_w3.eth.get_transaction.assert_called_once_with(tx_hash_test)
        
        # El flujo nativo fallará por no encontrar tx_info simulada, pero probamos positivamente que NUNCA fue por bloque
        assert "Confirmaciones insuficientes" not in res.get("error", "")

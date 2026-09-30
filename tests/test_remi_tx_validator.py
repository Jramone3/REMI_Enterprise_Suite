import pytest
from unittest.mock import MagicMock, patch
from remi_tx_validator import verify_base_transaction

def test_invalid_tx_hash_format():
    res = verify_base_transaction("0x123")
    assert res["valid"] is False
    assert "Formato de Hash" in res["error"]

@patch("remi_tx_validator.Web3")
def test_native_tx_success(mock_web3_class):
    mock_w3 = MagicMock()
    mock_web3_class.return_value = mock_w3
    mock_w3.is_connected.return_value = True

    mock_w3.eth.get_transaction_receipt.return_value = {"status": 1, "blockNumber": 12345}
    mock_w3.eth.get_transaction.return_value = {
        "to": "0x96De980a766CCb10A19B6962587e2b61B650b372",
        "value": 1000000000000000 # 0.001 ETH
    }
    mock_w3.from_wei.return_value = 0.001

    res = verify_base_transaction("0x" + "f" * 64, expected_min_amount=0.001, is_erc20=False)
    assert res["valid"] is True
    assert res["type"] == "NATIVE"

@patch("remi_tx_validator.Web3")
def test_tx_failed_status(mock_web3_class):
    mock_w3 = MagicMock()
    mock_web3_class.return_value = mock_w3
    mock_w3.is_connected.return_value = True

    mock_w3.eth.get_transaction_receipt.return_value = {"status": 0}

    res = verify_base_transaction("0x" + "f" * 64)
    assert res["valid"] is False
    assert "falló o fue revertida" in res["error"]

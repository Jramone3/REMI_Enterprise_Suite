from unittest.mock import MagicMock, patch
from web3 import Web3
from remi_tx_validator import verify_base_transaction


@patch("remi_tx_validator.Web3")
def test_erc20_success_mock(mock_web3_class):
    mock_w3 = MagicMock()
    mock_web3_class.return_value = mock_w3
    mock_w3.is_connected.return_value = True

    token_addr = Web3.to_checksum_address("0x" + "1" * 40)
    recipient_padded = "0x" + "0" * 24 + "96De980a766CCb10A19B6962587e2b61B650b372"

    fake_log = {
        "address": token_addr,
        "topics": [
            "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
            "0x" + "0" * 64,
            recipient_padded,
        ],
        "data": hex(
            499 * 10**6),
    }

    receipt = {"status": 1, "blockNumber": 111, "logs": [fake_log]}
    mock_w3.eth.get_transaction_receipt.return_value = receipt

    tx_mock = {"hash": "0x" + "a" * 64, "value": 0, "to": token_addr}
    mock_w3.eth.get_transaction.return_value = tx_mock

    res = verify_base_transaction(
        "0x" + "a" * 64,
        expected_min_amount=499,
        is_erc20=True)
    assert isinstance(res, dict)
    assert "valid" in res

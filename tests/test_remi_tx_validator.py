from unittest.mock import MagicMock, patch
import pytest

from auth_gateways.remi_tx_validator import validate_transaction

MERCHANT = "0x1111111111111111111111111111111111111111"
TOKEN = "0x2222222222222222222222222222222222222222"
TX_HASH = "0x" + "a" * 64


@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    monkeypatch.setenv("BASE_RPC_URL", "https://mainnet.base.org")
    monkeypatch.setenv("REMI_PAYMENT_ADDRESS", MERCHANT)
    monkeypatch.setenv("EXPECTED_TOKEN_ADDRESS", TOKEN)
    monkeypatch.setenv("EXPECTED_TOKEN_DECIMALS", "6")
    monkeypatch.setenv("MIN_CONFIRMATIONS", "3")


def _mock_web3(receipt=None, block_number=100, tx_info=None, chain_id=8453, connected=True, fail_native=False):
    w3 = MagicMock()
    w3.is_connected.return_value = connected
    w3.eth.chain_id = chain_id
    w3.eth.block_number = block_number
    w3.eth.get_transaction_receipt.return_value = receipt
    if fail_native:
        w3.eth.get_transaction.side_effect = TimeoutError("RPC timeout fetching native tx")
    else:
        w3.eth.get_transaction.return_value = tx_info
    w3.from_wei.side_effect = lambda val, unit: val / 1e18
    return w3


def test_rejects_reverted_transaction():
    receipt = {"status": 0, "blockNumber": 90, "logs": []}
    with patch("auth_gateways.remi_tx_validator.Web3", return_value=_mock_web3(receipt=receipt)):
        res = validate_transaction(TX_HASH, expected_min_amount=100.0, is_erc20=True)
    assert res["valid"] is False


def test_rejects_insufficient_confirmations():
    receipt = {"status": 1, "blockNumber": 99, "logs": []}  # 100 - 99 = 1 < 3
    with patch("auth_gateways.remi_tx_validator.Web3", return_value=_mock_web3(receipt=receipt, block_number=100)):
        res = validate_transaction(TX_HASH, expected_min_amount=100.0, is_erc20=True)
    assert res["valid"] is False
    assert "confirmaciones" in res["error"].lower()


def test_rejects_native_tx_on_rpc_error():
    receipt = {"status": 1, "blockNumber": 90, "logs": []}
    with patch("auth_gateways.remi_tx_validator.Web3", return_value=_mock_web3(receipt=receipt, fail_native=True)):
        res = validate_transaction(TX_HASH, expected_min_amount=1.0, is_erc20=False)
    assert res["valid"] is False


def test_accepts_valid_native_tx():
    receipt = {"status": 1, "blockNumber": 90, "logs": []}
    tx_info = {"to": MERCHANT, "value": int(2 * 1e18)}
    with patch("auth_gateways.remi_tx_validator.Web3", return_value=_mock_web3(receipt=receipt, tx_info=tx_info)):
        res = validate_transaction(TX_HASH, expected_min_amount=1.0, is_erc20=False)
    assert res["valid"] is True
    assert res["type"] == "NATIVE"

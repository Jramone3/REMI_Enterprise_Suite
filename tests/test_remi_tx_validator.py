import os
import pytest

# Establecer defaults seguros *antes* de importar el módulo para evitar fallos por variables vacías en import time.
os.environ.setdefault("MIN_CONFIRMATIONS", "3")
os.environ.setdefault("REMI_PAYMENT_ADDRESS", "0x0000000000000000000000000000000000000000")

from remi_tx_validator import verify_base_transaction, TRANSFER_EVENT_SIGNATURE_HASH
from eth_utils import to_checksum_address

class DummyReceipt(dict):
    pass

class FakeW3Base:
    def is_connected(self):
        return True
    def from_wei(self, v, unit):
        return v / 1e18

def test_native_tx_valid(monkeypatch):
    tx_hash = "0xdeadbeef"
    target_addr = "0x96De980a766CCb10A19B6962587e2b61B650b372"

    class FakeW3(FakeW3Base):
        def __init__(self, *args, **kwargs):
            self.eth = self
        def get_transaction_receipt(self, h):
            r = DummyReceipt()
            r["status"] = 1
            r["blockNumber"] = 100
            r["logs"] = []
            return r
        @property
        def block_number(self):
            return 105
        def get_transaction(self, h):
            return {
                "to": target_addr,
                "value": int(1e18)
            }

    def fake_web3_factory(*args, **kwargs):
        return FakeW3()
    fake_web3_factory.HTTPProvider = lambda *a, **kw: None

    monkeypatch.setenv("REMI_PAYMENT_ADDRESS", target_addr)
    monkeypatch.setenv("MIN_CONFIRMATIONS", "3")
    monkeypatch.setattr("remi_tx_validator.Web3", fake_web3_factory)

    res = verify_base_transaction(tx_hash, expected_min_amount=0.5, is_erc20=False)
    assert res["valid"] is True
    assert res["type"] == "NATIVE"
    assert res["amount"] == 1.0

def test_confirmations_insufficient(monkeypatch):
    tx_hash = "0xdeadbeef"
    target_addr = "0x96De980a766CCb10A19B6962587e2b61B650b372"

    class FakeW3(FakeW3Base):
        def __init__(self, *args, **kwargs):
            self.eth = self
        def get_transaction_receipt(self, h):
            r = DummyReceipt()
            r["status"] = 1
            r["blockNumber"] = 104
            r["logs"] = []
            return r
        @property
        def block_number(self):
            return 105  # Confirmaciones = (105 - 104) + 1 = 2 (< MIN_CONFIRMATIONS=3)

    def fake_web3_factory(*args, **kwargs):
        return FakeW3()
    fake_web3_factory.HTTPProvider = lambda *a, **kw: None

    monkeypatch.setenv("REMI_PAYMENT_ADDRESS", target_addr)
    monkeypatch.setenv("MIN_CONFIRMATIONS", "3")
    monkeypatch.setattr("remi_tx_validator.Web3", fake_web3_factory)

    res = verify_base_transaction(tx_hash, expected_min_amount=0.5, is_erc20=False)
    assert res["valid"] is False
    assert "Confirmaciones insuficientes" in res["error"]

def test_erc20_tx_valid(monkeypatch):
    tx_hash = "0xdeadbeef"
    target_addr = "0x96De980a766CCb10A19B6962587e2b61B650b372"
    token_addr = "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"  # USDC Base

    target_topic = "0x" + "0" * 24 + target_addr[2:].lower()
    raw_amount_hex = hex(int(499 * 10**6))

    class FakeW3(FakeW3Base):
        def __init__(self, *args, **kwargs):
            self.eth = self
        def get_transaction_receipt(self, h):
            r = DummyReceipt()
            r["status"] = 1
            r["blockNumber"] = 100
            r["logs"] = [
                {
                    "address": token_addr.lower(),
                    "topics": [
                        TRANSFER_EVENT_SIGNATURE_HASH,
                        "0x" + "0" * 64,
                        target_topic,
                    ],
                    "data": raw_amount_hex,
                }
            ]
            return r
        @property
        def block_number(self):
            return 105

    def fake_web3_factory(*args, **kwargs):
        return FakeW3()
    fake_web3_factory.HTTPProvider = lambda *a, **kw: None

    monkeypatch.setenv("REMI_PAYMENT_ADDRESS", target_addr)
    monkeypatch.setenv("EXPECTED_TOKEN_ADDRESS", token_addr)
    monkeypatch.setenv("EXPECTED_TOKEN_DECIMALS", "6")
    monkeypatch.setenv("MIN_CONFIRMATIONS", "3")
    monkeypatch.setattr("remi_tx_validator.Web3", fake_web3_factory)

    res = verify_base_transaction(tx_hash, expected_min_amount=499.0, is_erc20=True)
    assert res["valid"] is True
    assert res["type"] == "ERC20"
    assert res["amount"] == 499.0

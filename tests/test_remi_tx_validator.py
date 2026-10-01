import pytest
import remi_tx_validator as rtv

def test_verify_native_success(monkeypatch):
    class FakeEth:
        def get_transaction_receipt(self, tx):
            return {"status": 1, "blockNumber": 123, "logs": []}
        def get_transaction(self, tx):
            return {"to": rtv.TARGET_WALLET, "value": int(1e18)}
    class FakeW3:
        def __init__(self):
            self.eth = FakeEth()
        def is_connected(self):
            return True
        def from_wei(self, val, _):
            return val / 1e18

    monkeypatch.setattr(rtv, "Web3", lambda provider: FakeW3())

    res = rtv.verify_base_transaction("0x" + "a"*64, expected_min_amount=0.1, is_erc20=False)
    assert res["valid"] is True
    assert res["type"] == "NATIVE"

def test_verify_erc20_insufficient(monkeypatch):
    monkeypatch.setattr(rtv, "EXPECTED_TOKEN", "0x" + "1"*40)
    fake_log = {
        "address": rtv.EXPECTED_TOKEN,
        "topics": [rtv.TRANSFER_EVENT_SIGNATURE_HASH, "0x"+"0"*64, "0x"+rtv.TARGET_WALLET[-40:]],
        "data": hex(100)
    }
    class FakeEth:
        def get_transaction_receipt(self, tx):
            return {"status": 1, "blockNumber": 100, "logs": [fake_log]}
    class FakeW3:
        def __init__(self):
            self.eth = FakeEth()
        def is_connected(self):
            return True

    monkeypatch.setattr(rtv, "Web3", lambda provider: FakeW3())
    res = rtv.verify_base_transaction("0x"+"b"*64, expected_min_amount=1000, is_erc20=True)
    assert res["valid"] is False
    assert "insuficiente" in res.get("error","").lower()

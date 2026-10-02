import pytest
from remi_tx_validator import verify_base_transaction

class DummyReceipt(dict):
    pass

def test_native_tx_valid(monkeypatch):
    tx_hash = "0xdeadbeef"
    
    class FakeW3:
        def __init__(self, *args, **kwargs):
            self.eth = self
        def is_connected(self):
            return True
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
                "to": "0x96De980a766CCb10A19B6962587e2b61B650b372",
                "value": int(1e18)
            }
        def from_wei(self, v, unit):
            return v / 1e18

    monkeypatch.setattr("remi_tx_validator.Web3", lambda *a, **kw: FakeW3())
    import os
    os.environ["REMI_PAYMENT_ADDRESS"] = "0x96De980a766CCb10A19B6962587e2b61B650b372"
    os.environ["MIN_CONFIRMATIONS"] = "3"
    
    res = verify_base_transaction(tx_hash, expected_min_amount=0.5, is_erc20=False)
    assert res["valid"] is True
    assert res["type"] == "NATIVE"
    assert res["amount"] == 1.0

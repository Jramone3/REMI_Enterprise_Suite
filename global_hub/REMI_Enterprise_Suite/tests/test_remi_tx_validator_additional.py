import os

os.environ.setdefault("MIN_CONFIRMATIONS", "3")
os.environ.setdefault("REMI_PAYMENT_ADDRESS", "0x0000000000000000000000000000000000000000")

from remi_tx_validator import verify_base_transaction

class DummyReceipt(dict):
    pass

class FakeW3Base:
    def is_connected(self):
        return True
    def from_wei(self, v, unit):
        return v / 1e18

def test_erc20_no_expected_token(monkeypatch):
    tx_hash = "0x" + "a" * 64
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

    def fake_web3_factory(*args, **kwargs):
        return FakeW3()
    fake_web3_factory.HTTPProvider = lambda *a, **kw: None

    monkeypatch.delenv("EXPECTED_TOKEN_ADDRESS", raising=False)
    monkeypatch.setenv("REMI_PAYMENT_ADDRESS", target_addr)
    monkeypatch.setenv("MIN_CONFIRMATIONS", "3")
    monkeypatch.setattr("remi_tx_validator.Web3", fake_web3_factory)

    res = verify_base_transaction(tx_hash, expected_min_amount=10.0, is_erc20=True)
    assert res["valid"] is False
    assert "transferencia ERC-20" in res["error"] or "EXPECTED_TOKEN_ADDRESS" in res["error"] or "no configurado" in res["error"]

def test_tx_reverted(monkeypatch):
    tx_hash = "0x" + "b" * 64
    target_addr = "0x96De980a766CCb10A19B6962587e2b61B650b372"

    class FakeW3(FakeW3Base):
        def __init__(self, *args, **kwargs):
            self.eth = self
        def get_transaction_receipt(self, h):
            r = DummyReceipt()
            r["status"] = 0
            r["blockNumber"] = 100
            r["logs"] = []
            return r
        @property
        def block_number(self):
            return 110

    def fake_web3_factory(*args, **kwargs):
        return FakeW3()
    fake_web3_factory.HTTPProvider = lambda *a, **kw: None

    monkeypatch.setenv("REMI_PAYMENT_ADDRESS", target_addr)
    monkeypatch.setenv("MIN_CONFIRMATIONS", "3")
    monkeypatch.setattr("remi_tx_validator.Web3", fake_web3_factory)

    res = verify_base_transaction(tx_hash, expected_min_amount=0.1, is_erc20=False)
    assert res["valid"] is False
    assert "revertida" in res["error"] or "falló" in res["error"]

def test_rpc_timeout(monkeypatch):
    tx_hash = "0x" + "c" * 64
    target_addr = "0x96De980a766CCb10A19B6962587e2b61B650b372"

    class FakeW3:
        def __init__(self, *args, **kwargs):
            pass
        def is_connected(self):
            raise Exception("timeout")

    def fake_web3_factory(*args, **kwargs):
        return FakeW3()
    fake_web3_factory.HTTPProvider = lambda *a, **kw: None

    monkeypatch.setenv("REMI_PAYMENT_ADDRESS", target_addr)
    monkeypatch.setattr("remi_tx_validator.Web3", fake_web3_factory)

    res = verify_base_transaction(tx_hash, expected_min_amount=0.1, is_erc20=False)
    assert res["valid"] is False
    assert "timeout" in res["error"] or "Error" in res["error"] or "No se pudo conectar" in res["error"]

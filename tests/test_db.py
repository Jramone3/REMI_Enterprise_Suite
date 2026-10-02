import mongomock
from db import save_license, find_license_by_email


def test_save_and_find_license(monkeypatch):
    mock_client = mongomock.MongoClient()

    def fake_get_client():
        return mock_client

    monkeypatch.setattr("db.get_client", fake_get_client)

    record = {
        "email": "test@example.com",
        "tx_hash": "0x" + "a" * 64,
        "payment_type": "ERC20",
        "license": "REMI-ENT-ANNUAL-TEST",
        "issued_at": "2026-10-01T00:00:00Z",
        "expires": "2027-10-01",
    }

    save_license(record)
    found = find_license_by_email("test@example.com")

    assert found is not None
    assert found["email"] == "test@example.com"
    assert found["license"] == "REMI-ENT-ANNUAL-TEST"

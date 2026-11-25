import unittest
from unittest.mock import patch, MagicMock
from remi_tx_validator import validate_transaction

class TestRemiTxValidator(unittest.TestCase):
    
    @patch('remi_tx_validator.requests.post')
    def test_validate_transaction_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {
                "blockNumber": "0x10",
                "to": "0x000000000000000000000000000000000000dEaD"
            }
        }
        mock_post.return_value = mock_response

        result = validate_transaction("0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
        self.assertIsInstance(result, dict)
        self.assertIn("valid", result)

    def test_validate_transaction_invalid_format(self):
        result = validate_transaction("0xinvalid_hash")
        self.assertFalse(result.get("valid"))

if __name__ == "__main__":
    unittest.main()

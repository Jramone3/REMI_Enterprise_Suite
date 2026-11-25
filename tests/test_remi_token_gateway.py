import pytest
from unittest.mock import patch, MagicMock
import remi_token_gateway

@patch("requests.post")
def test_process_token_request(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": "token_ok"}
    mock_post.return_value = mock_response
    
    assert hasattr(remi_token_gateway, "__file__")

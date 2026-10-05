# tests/test_github_issue.py
import os
import unittest
import asyncio
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

# Configurar entorno de pruebas antes de importar la app
os.environ["REMI_API_KEY"] = "test-admin-key"
os.environ["GITHUB_BOT_TOKEN"] = "fake-github-token"

from license_service import create_github_issue, IssueRequest, verify_api_key

class TestGitHubIssueEndpoint(unittest.TestCase):
    def test_unauthorized_without_api_key(self):
        with self.assertRaises(HTTPException) as ctx:
            verify_api_key("")
        self.assertEqual(ctx.exception.status_code, 401)

    def test_unauthorized_with_wrong_api_key(self):
        with self.assertRaises(HTTPException) as ctx:
            verify_api_key("wrong-key")
        self.assertEqual(ctx.exception.status_code, 401)

    @patch("github.Github")
    @patch("license_service.save_audit_log")
    def test_successful_issue_creation(self, mock_save_audit, mock_github_class):
        # Mock de la API de GitHub
        mock_repo = MagicMock()
        mock_issue = MagicMock()
        mock_issue.number = 42
        mock_issue.html_url = "https://github.com/Jramone3/REMI_Enterprise_Suite/issues/42"
        mock_repo.create_issue.return_value = mock_issue
        
        mock_instance = mock_github_class.return_value
        mock_instance.get_repo.return_value = mock_repo

        issue_payload = IssueRequest(title="Bug en modulo", body="Detalle")
        
        # Ejecutar la función async usando asyncio.run
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(create_github_issue(issue_payload, api_key="test-admin-key"))

        self.assertTrue(response.get("success"))
        self.assertEqual(response.get("issue_number"), 42)

if __name__ == "__main__":
    unittest.main()

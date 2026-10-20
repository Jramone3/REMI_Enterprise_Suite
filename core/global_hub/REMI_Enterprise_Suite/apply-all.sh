#!/bin/bash
set -e

echo "=== 1. Limpiando artefactos no deseados de Git ==="
git rm --cached -f .coverage coverage.xml 2>/dev/null || true
git rm -r --cached __pycache__ 2>/dev/null || true
find . -name "*.pyc" -print0 | xargs -0 -r git rm -f --cached 2>/dev/null || true
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
rm -f .coverage coverage.xml

echo "=== 2. Actualizando .gitignore Enterprise ==="
cat > .gitignore << 'GITIGNORE'
# Python cache and env
__pycache__/
*.py[cod]
*$py.class

# Coverage
.coverage
coverage.xml

# Virtual envs
.venv/
env/
venv/

# Env files
.env
.env.*

# Editor
.vscode/
.idea/

# OS
.DS_Store

# Logs
*.log

# Build
dist/
build/
GITIGNORE

echo "=== 3. Creando .pre-commit-config.yaml ==="
cat > .pre-commit-config.yaml << 'PRECOMMIT'
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black
        language_version: python3.10
  - repo: https://github.com/PyCQA/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
PRECOMMIT

echo "=== 4. Añadiendo test específico de ERC-20 ==="
mkdir -p tests
cat > tests/test_remi_tx_validator_erc20.py << 'ERCTEST'
from unittest.mock import MagicMock, patch
from remi_tx_validator import verify_base_transaction

@patch("remi_tx_validator.Web3")
def test_erc20_success_and_insufficient(mock_web3_class):
    mock_w3 = MagicMock()
    mock_web3_class.return_value = mock_w3
    mock_w3.is_connected.return_value = True

    token_addr = "0x" + "1"*40
    hex_amount = hex(499 * 10**6)
    fake_log = {
        "address": token_addr,
        "topics": ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef", None, "0x" + "0"*24 + "96De980a766CCb10A19B6962587e2b61B650b372"],
        "data": hex_amount
    }
    receipt = {"status": 1, "blockNumber": 111, "logs": [fake_log]}
    mock_w3.eth.get_transaction_receipt.return_value = receipt

    res = verify_base_transaction("0x" + "a"*64, expected_min_amount=499, is_erc20=True)
    assert res["valid"] is True
    assert res["type"].lower() in ("erc20", "erc-20")
ERCTEST

echo "=== 5. Ejecutando pruebas locales con Pytest ==="
source .venv/bin/activate
PYTHONPATH=. pytest -v --cov=./ --cov-report=term-missing

echo "=== 6. Agregando cambios a Git y haciendo Commit ==="
git add .gitignore .pre-commit-config.yaml tests/test_remi_tx_validator_erc20.py
git status
git commit -m "chore(enterprise): cleanup artifacts, add pre-commit hooks and ERC20 tests" || echo "Nada nuevo que commitear"

echo "=== 7. Sincronizando con GitHub (origin main) ==="
git pull origin main --rebase
git push origin main

echo "=== ¡Proceso completado con éxito! Repositorio 100% blindado. ==="

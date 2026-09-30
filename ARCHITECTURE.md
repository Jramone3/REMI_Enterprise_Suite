# REMI Enterprise Suite — Architecture Overview

## High-level Summary
REMI is an enterprise multi-agent custody and monitoring system designed for confidentiality, strict auditability, and recoverability. It is built to run securely on-premise in hardened environments or enterprise-grade private infrastructure.

## Core Components
1. **Streamlit UI (`app.py`)**: Front-end interface for interactive enterprise licensing and session management.
2. **On-Chain Validator (`remi_tx_validator.py`)**: Verification module interfacing with the Base network (Layer 2) for native and ERC-20 token transfers.
3. **License Backend (`license_service.py`)**: FastAPI-based microservice handling automated license issuance and verification records.
4. **Audit Layer**: Local MongoDB persistence mapping transaction hashes and operational events.
5. **CI/CD Pipeline**: GitHub Actions workflows executing linting (`flake8`), code formatting checks, and unit tests (`pytest`).

## Security & Operational Notes
- Secrets (RPC URLs, Database URIs, Payment Wallets) must be managed via environment variables or GitHub Secrets.
- No private keys or financial secrets are stored inside the repository codebase.

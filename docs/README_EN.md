# REMI Enterprise Suite

Modular enterprise multi-agent AI framework and developer suite for secure, sovereign, and production-ready operations.

REMI Enterprise Suite is designed for organizations that need to deploy, manage, and scale multi-agent AI ecosystems in a secure and auditable environment. The project combines a Streamlit-based operational portal, a FastAPI license microservice, on-chain payment validation, MongoDB persistence, and local AI integration with Ollama to provide a complete enterprise-ready platform.

## Overview

REMI Enterprise Suite provides a unified operational environment for:
- multi-agent orchestration and intelligent task execution
- secure license issuance and verification
- on-chain payment validation on Base
- fiat payment support through Stripe
- operational monitoring and compliance logging
- GitHub issue automation for project workflows

The architecture is structured to support enterprise deployments with clear separation between:
- frontend presentation
- backend API logic
- transaction verification
- data persistence
- operational automation

## Key Features

### Multi-Agent Operations
The platform includes a command-center interface for interactive AI-driven operations and business workflows. It communicates with a local LLM endpoint using Ollama and the `llama3` model, enabling operational chat and assistant-driven orchestration.

### License Management
The project includes a protected licensing flow:
- customer validation
- transaction verification
- license issuance
- status verification by email
- expiry tracking
- audit persistence in MongoDB

### Blockchain Validation
Transactions are validated via Base RPC using the transaction receipt and token transfer logs. This enables secure validation of ERC-20 transfers, including contribution threshold checks and recipient verification.

### Stripe / Fiat Support
The system includes a commercial payment flow for fiat purchases and webhook-based automation for issuing licenses after successful checkout.

### GitHub Integration
The project includes automation for issue creation through a GitHub bot token, enabling direct technical task management from the platform.

## System Architecture

The repository is organized around a modular enterprise architecture:
- `app.py` — Streamlit user interface for operational control and licensing
- `license_service.py` — FastAPI backend for issuing and verifying licenses
- `remi_tx_validator.py` — Base on-chain transaction validation logic
- `db.py` — MongoDB access, licensing, and audit persistence
- `Dockerfile` / `docker-compose.yml` — containerized deployment support
- `scripts/` — operational and automation helpers
- `tests/` — validation and unit test coverage

## Technology Stack

- Python
- Streamlit
- FastAPI
- Uvicorn
- MongoDB / PyMongo
- Requests
- Web3 / eth-utils
- Docker / Docker Compose
- Ollama
- Shell scripting

## Prerequisites

For local development, ensure the following:
- Python 3.10+
- Git
- Docker and Docker Compose (optional but recommended)
- MongoDB instance
- Access to a Base RPC endpoint
- Wallet or payment address for license validation
- GitHub token for automation tasks

## Environment Variables

The application depends on a set of environment variables for secure operation.

Required variables:
- `MONGO_URI`
- `REMI_DB_NAME`
- `REMI_PAYMENT_ADDRESS`
- `BASE_RPC_URL`
- `REMI_API_KEY`
- `LLM_HOST`

Optional variables:
- `EXPECTED_TOKEN_ADDRESS`
- `EXPECTED_TOKEN_DECIMALS`
- `GITHUB_BOT_TOKEN`
- `TEST_MODE`

Example:
```bash
export MONGO_URI="mongodb://localhost:27017"
export REMI_DB_NAME="remi_enterprise"
export REMI_PAYMENT_ADDRESS="0x96De980a766CCb10A19B6962587e2b61B650b372"
export BASE_RPC_URL="[https://mainnet.base.org](https://mainnet.base.org)"
export REMI_API_KEY="your_admin_api_key"
export LLM_HOST="http://localhost:11434"
export GITHUB_BOT_TOKEN="your_token_here"

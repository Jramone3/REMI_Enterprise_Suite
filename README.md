---
license: mit
tags:
  - ai-agents
  - enterprise-suite
  - security
  - auditing
  - multi-agent
title: REMI Enterprise Suite Demo
emoji: 🤖
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: 1.30.0
app_file: app.py
pinned: false
---

# REMI Enterprise Suite — Interactive Demonstration

Enterprise-grade multi-agent framework and AI core with integrated license verification and update synchronization.

## Overview

REMI is an enterprise-focused multi-agent AI framework designed for secure on-premises and hybrid cloud deployments. This repository contains an interactive Streamlit demonstration showcasing:
- Enterprise license issuance and verification flow (on-chain transaction reference).
- Local multi-agent core interaction (demo client to an LLM endpoint).
- Administrative update synchronization flow for licensed instances.

## Stack

- Language(s): Python 3.11+
- Framework / runtime: Streamlit (app), optionally a local LLM runtime (Ollama / Llama variants) accessed via REST
- Notable libraries: streamlit, requests, python-dotenv, pymongo (optional), web3 (optional)

## How to run (quick start)

1. Create a Python virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Create a local .env based on `.env.example` and update the values as required.

3. Launch the Streamlit demonstration:
```bash
streamlit run app.py
```

4. For the multi-agent core demo, run or configure a local LLM-compatible REST endpoint (default: http://localhost:11434/api/chat) or update the URL in `app.py` to point to your model service.

## Environment variables

See `.env.example` for the canonical variable names. Notable variables:
- PORT — application port (if deploying behind a custom runner)
- MONGO_URI — optional MongoDB connection for state (if used)
- WEB3_PROVIDER_URI — optional web3 provider for on-chain verification

## Try asking

3 follow-up questions phrased as the user would type them. Use real
concepts and filenames from this repo. Prefer questions that surface
loose ends (features in the README you didn't see in code, deprecated
areas, unclear cross-references) over generic ones. Omit the section
entirely if you can't make the questions specific to this repo.


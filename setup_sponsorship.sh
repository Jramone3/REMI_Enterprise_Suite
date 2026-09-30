#!/usr/bin/env bash
set -e

echo "=== [1/8] Actualizando README.md con la sección de Support & Sponsorship ==="
cat > README.md << 'README'
REMI — Agentic Patrimonial Guardian
Enterprise-grade agentic custody system for safeguarding critical assets with continuous monitoring and auditable controls.
Status: OPERATIONAL | Version: v1.1.0-enterprise | Protocol: AURUM-v0.8

What REMI is
REMI is an agentic custody system designed for preservation and surveillance of high-value assets within a hardened operational environment (the "Fortress Bunker"). It operates as a sovereign digital preservation and monitoring framework focused on enterprise security, traceability, and controlled updates.

Security Infrastructure
- Synchronization: Encrypted automated synchronization (Ed25519) for periodic checkpoints.
- Core: Agentic intelligence engine with variable-level auditing and traceability.
- Hardware: Local node optimized for stable operation (Intel i5) with active thermal monitoring.
- Persistence: Local MongoDB instance with protected indexing and encrypted storage options.

Built-in Security Limits
- Zero leverage exposure: Strict prevention of debt/leverage operations.
- Anti-hallucination protocol: Cross-verification of external data before any balance or report issuance.
- Security isolation: Critical nodes operate under restricted access policies.
- Hardware constraints: Operational limits to ensure nodes run on authorized local hardware to avoid uncontrolled cloud exfiltration.

Disclaimer
This system is implemented as a private custody solution. Unauthorized access to cold storage nodes or pre-authorized security wallets will trigger predefined alerting, access revocation, and incident response procedures.

## Support & Sponsorship

REMI is developed and maintained by the REMI Core team (Lead: Jesus Ramon Rivas Garcia - `Jramone3`). If REMI helps you or your organization, supporting the project enables continued security audits, enterprise integrations, and priority support.

Sponsorship options
- GitHub Sponsors — preferred. Sponsor the project at: https://github.com/sponsors/Jramone3
- Direct enterprise sponsorships (commercial integrations, SLAs, audits): contact commercial@remi-enterprise.com
- Crypto donations — one-time support via Base Network (USDT/ETH compatible): 0x96De980a766CCb10A19B6962587e2b61B650b372
  - View on BaseScan: https://basescan.org/address/0x96De980a766CCb10A19B6962587e2b61B650b372

Sponsorship tiers
- Bronze — Supporter: README mention, early release notes access.
- Silver — Contributor: Bronze benefits + private roadmap updates + 1 consulting hour per quarter.
- Gold — Strategic Sponsor: Silver benefits + technical onboarding, priority support, co‑branding opportunities and custom SLAs.

Why sponsor REMI?
- Enterprise-first security posture and protocolized updates.
- Active roadmap for multi-agent orchestration and audit trails.
- Opportunity to influence priority features for on‑premise deployments.

Contact & legal
- Commercial enquiries and invoicing: commercial@remi-enterprise.com
- Technical support and license queries: soporte@remi-enterprise.com

<p align="center">
  <a href="https://basescan.org/address/0x96De980a766CCb10A19B6962587e2b61B650b372" target="_blank">
    <img src="assets/qr_funding.png" alt="Funding QR Code" width="250"/>
  </a>
</p>
README

echo "=== [2/8] Configurando .github/FUNDING.yml ==="
mkdir -p .github
cat > .github/FUNDING.yml << 'FUND'
github: Jramone3
FUND

echo "=== [3/8] Creando SPONSORS.md ==="
cat > SPONSORS.md << 'SPONS'
# Sponsors & Benefits

Thank you for considering sponsorship of REMI Enterprise Suite. Sponsors help fund security audits, enterprise features, and roadmap acceleration.

## Sponsor Contact
- Commercial enquiries / Corporate sponsorships: commercial@remi-enterprise.com

## Sponsorship Tiers

### Bronze — Supporter
- Public mention in README and project website.
- Early access to release notes and roadmap summaries.

### Silver — Contributor
- All Bronze benefits.
- Quarterly private roadmap and release briefing.
- 1 consulting hour per quarter for integration support.

### Gold — Strategic Sponsor
- All Silver benefits.
- Priority technical support and onboarding (SLA).
- Opportunity for co‑branding and feature prioritization.
- Dedicated commercial agreement and invoicing.

## How to Sponsor
- **GitHub Sponsors:** https://github.com/sponsors/Jramone3
- **Crypto Donation (Base Network):** `0x96De980a766CCb10A19B6962587e2b61B650b372` ([View on BaseScan](https://basescan.org/address/0x96De980a766CCb10A19B6962587e2b61B650b372))
SPONS

echo "=== [4/8] Creando CONTRIBUTING.md ==="
cat > CONTRIBUTING.md << 'CONTR'
# Contributing to REMI Enterprise Suite

Thank you for your interest in contributing to REMI. We welcome contributions from individuals and organizations. To make collaboration safe and productive, please follow these guidelines.

## Maintainers
- **REMI Core Team** (Lead: Jesus Ramon Rivas Garcia - `Jramone3`)
- **Contact:** commercial@remi-enterprise.com / soporte@remi-enterprise.com

## How to Contribute
1. Open an issue to propose significant changes or report bugs.
2. For code contributions, fork the repo and open a PR against `main`.
3. Keep changes focused: one logical change per PR and include tests when possible.

## Code Style and Quality
- Use Python 3.10+ conventions.
- Keep dependencies updated in `requirements.txt`.

## Reporting Security Issues
- Do NOT open public security issues on GitHub. Use the secure disclosure channel in `SECURITY.md`.
CONTR

echo "=== [5/8] Creando SECURITY.md ==="
cat > SECURITY.md << 'SEC'
# Security Policy

We take security seriously. If you discover a vulnerability, please follow the responsible disclosure process below.

## Reporting a Vulnerability
- Do NOT create a public GitHub issue for security vulnerabilities.
- Send an email to **security@remi-enterprise.com** detailing:
  - Affected component and version
  - Steps to reproduce
  - Impact assessment
  - Proof-of-concept (if available)

## Response Timeline
- We will acknowledge receipt within 48 hours and provide an estimated timeline for remediation.
- For commercial matters related to sponsored security reviews: commercial@remi-enterprise.com
SEC

echo "=== [6/8] Creando CODE_OF_CONDUCT.md ==="
cat > CODE_OF_CONDUCT.md << 'COC'
# Contributor Covenant Code of Conduct

## Our Pledge
We as members, contributors, and leaders pledge to make participation in our community a harassment-free experience for everyone, regardless of age, body size, visible or invisible disability, ethnicity, sex characteristics, gender identity and expression, level of experience, education, socio-economic status, nationality, personal appearance, race, caste, religion, or sexual identity and orientation.

## Enforcement
Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by contacting the project team at **conduct@remi-enterprise.com**.
COC

echo "=== [7/8] Configurando CI (GitHub Actions) en .github/workflows/ci.yml ==="
mkdir -p .github/workflows
cat > .github/workflows/ci.yml << 'CI'
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
      runs-on: ubuntu-latest
      steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
      - name: Verify Python files syntax
        run: |
          python -m compileall .
CI

echo "=== [8/8] Verificando assets y carpetas ==="
mkdir -p static
touch static/.gitkeep

echo "¡Archivos listos! Realizando commit y push a main..."
git add README.md .github/FUNDING.yml SPONSORS.md CONTRIBUTING.md SECURITY.md CODE_OF_CONDUCT.md .github/workflows/ci.yml static/.gitkeep
git commit -m "chore: add enterprise sponsorship, governance, security files and basic CI"
git push origin main

echo "¡Proceso completado con éxito en remi_deploy_clean!"

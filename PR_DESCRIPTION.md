Standardize English: Translate UI, docs, and comments to professional technical English

This pull request translates all user-facing text, inline comments, and documentation from Spanish to professional, standardized technical English. It also:

- Standardizes terminology across the codebase (License Key, TxHash, Enterprise License, Multi-Agent Core).
- Rewrites README into a clear developer-facing guide with production security notes.
- Updates .env.example and requirements/dependencies files to canonical English and version-pinned dependencies.

Notes:
- The demo license issuance flow remains client-side in `app.py` for demonstration purposes. In production, license generation and signing must be performed server-side using secure signing infrastructure (HSM, code-signing key) and audited event logs.

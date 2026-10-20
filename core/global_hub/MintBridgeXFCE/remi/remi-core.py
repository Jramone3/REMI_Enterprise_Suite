#!/usr/bin/env python3
# REMI Core – Experimental Agent Logic
# Author: jramonrivasg

import hashlib
import os
from datetime import datetime

def validate_file(path):
    if not os.path.exists(path):
        return f"❌ File not found: {path}"
    with open(path, "rb") as f:
        content = f.read()
        hash_value = hashlib.sha256(content).hexdigest()
        return f"✅ SHA256 for {path}: {hash_value}"

def log_event(message):
    with open("./remi/remi-log.md", "a") as log:
        log.write(f"{datetime.now().isoformat()} – {message}\n")

if __name__ == "__main__":
    print("🧠 REMI Core starting...")
    log_event("Agent core initialized")
    result = validate_file("./README.md")
    print(result)
    log_event(result)
    print("🧩 REMI Core completed.")

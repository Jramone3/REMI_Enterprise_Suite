#!/usr/bin/env python3
import time
from pathlib import Path

LOG = Path("/home/ramon/REMI_CORE/baliza_status.log")

while True:
    with open(LOG, "a") as f:
        f.write(f"[BALIZA] Pulso activo | {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    time.sleep(15)

#!/usr/bin/env python3
import sys

MAX = 7500
msg = sys.stdin.read()
chunks = [msg[i:i+MAX] for i in range(0, len(msg), MAX)]
total = len(chunks)
for i, c in enumerate(chunks, 1):
    suffix = "(end)" if i == total else ""
    print(f"REMI {i}/{total}:")
    print(c)
    if suffix:
        print(suffix)
    print()

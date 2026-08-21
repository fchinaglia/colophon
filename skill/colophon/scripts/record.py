#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Fabio Chinaglia
"""
Append-only event register with a hash chain.

Every event is one JSON line. The chain binds each event to the previous one:
    h(n) = sha256( h(n-1) || canonical(event_n) )
Altering a past event invalidates every hash that follows it.

Usage:
    python3 record.py '<event json>'
    python3 record.py --verify
    python3 record.py --root
"""
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(BASE, "events.jsonl")

GENESIS = "0" * 64


def canonical(obj) -> bytes:
    """Deterministic serialization: sorted keys, no whitespace, UTF-8."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def link(prev_hash: str, body: dict) -> str:
    return hashlib.sha256(prev_hash.encode("ascii") + canonical(body)).hexdigest()


def read() -> list:
    if not os.path.exists(LOG):
        return []
    with open(LOG, encoding="utf-8") as f:
        return [json.loads(r) for r in f if r.strip()]


def last_hash() -> str:
    rows = read()
    return rows[-1]["hash"] if rows else GENESIS


def append(event: dict) -> dict:
    rows = read()
    body = dict(event)
    body["seq"] = len(rows)
    body.setdefault("ts", datetime.now(timezone.utc).isoformat(timespec="seconds"))
    body["prev"] = last_hash()
    row = {**body, "hash": link(body["prev"], body)}
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return row


def verify() -> bool:
    prev = GENESIS
    rows = read()
    for i, r in enumerate(rows):
        body = {k: v for k, v in r.items() if k != "hash"}
        if body.get("prev") != prev:
            print(f"BROKEN at event {i}: prev does not match")
            return False
        if link(prev, body) != r["hash"]:
            print(f"BROKEN at event {i}: hash does not match")
            return False
        prev = r["hash"]
    print(f"chain intact — {len(rows)} events — root {prev[:16]}...")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    if sys.argv[1] == "--verify":
        sys.exit(0 if verify() else 1)
    if sys.argv[1] == "--root":
        print(last_hash())
        sys.exit(0)
    print(json.dumps(append(json.loads(sys.argv[1])), ensure_ascii=False))

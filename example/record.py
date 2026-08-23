#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Fabio Chinaglia
"""
Append-only event register with a hash chain.

Every event is one JSON line. The chain binds each event to the previous one:
    h(n) = sha256( h(n-1) || canonical(event_n) )
Altering a past event invalidates every hash that follows it.

An event may hold strings, integers within +/-(2**53 - 1), booleans, null, lists and
objects with ASCII keys. Not floats. See violations() for why, and spec/canonical.md
for the rule in full.

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


MAX_INT = 2 ** 53 - 1


def violations(obj, path="event") -> list:
    """What an event may not contain. An empty list means it can be recorded.

    The chain is checked by whoever reads it, and a reader outside Python cannot
    reproduce these bytes. After a JavaScript JSON.parse, 94.0 and 94 are the same
    value: the distinction is destroyed by parsing and cannot be recovered, so a
    register carrying one cannot be verified in a browser at all. Integers past
    2**53 are worse — JavaScript loses precision silently and returns a different
    number without saying so.

    None of this is repairable after the fact: the register is append-only, and
    reopening a case adds events rather than rewriting them. So the check belongs
    here, at the door, and it refuses rather than warning. The values that provoke
    it are descriptive payload — nothing reads them as numbers, the measurement of
    record is kpi.json — so write them as strings and nothing is lost.
    """
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if not isinstance(k, str) or any(ord(c) > 0x7F for c in k):
                out.append(f"{path}: key {k!r} is not ASCII")
            out += violations(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out += violations(v, f"{path}[{i}]")
    elif isinstance(obj, bool):
        pass                            # bool before int: it is a subclass of it
    elif isinstance(obj, float):
        out.append(f"{path}: {obj!r} is not an integer — write it as a string")
    elif isinstance(obj, int) and abs(obj) > MAX_INT:
        out.append(f"{path}: {obj} is beyond 2**53-1")
    return out


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
    bad = violations(event)
    if bad:
        raise ValueError("this event cannot be recorded:\n  " + "\n  ".join(bad))
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
    try:
        row = append(json.loads(sys.argv[1]))
    except ValueError as exc:
        print(f"not recorded — {exc}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(row, ensure_ascii=False))

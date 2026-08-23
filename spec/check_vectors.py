#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Check the conformance vectors against the reference implementation.

    python3 spec/check_vectors.py

Exit status 0 if every vector passes, 1 otherwise. Suitable for CI.

The three functions below are the executable form of spec/canonical.md. `record.py`
should adopt `violations()` at append() time; a verifier in any language must reproduce
`canonical()` byte for byte and `is_prespec()` in behaviour.
"""
import hashlib
import json
import os
import sys

MAX_INT = 2 ** 53 - 1


# --- canonical.md §3 ---------------------------------------------------------

def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def link(prev_hash: str, body: dict) -> str:
    return hashlib.sha256(prev_hash.encode("ascii") + canonical(body)).hexdigest()


# --- canonical.md §4 ---------------------------------------------------------

def violations(obj, path="") -> list:
    """Everything in `obj` that §4 forbids. Empty list means acceptable."""
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if not isinstance(k, str) or any(ord(c) > 0x7F for c in k):
                out.append(f"{path}: non-ASCII key {k!r}")
            out += violations(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out += violations(v, f"{path}[{i}]")
    elif isinstance(obj, bool):
        pass                                    # bool before int: it is a subclass
    elif isinstance(obj, float):
        out.append(f"{path}: non-integer number {obj!r}")
    elif isinstance(obj, int):
        if abs(obj) > MAX_INT:
            out.append(f"{path}: integer {obj} exceeds 2**53 - 1")
    return out


# --- canonical.md §5.1 -------------------------------------------------------

def is_prespec(line: str) -> bool:
    """True if this raw register line predates the spec and must be refused.

    Scans outside string literals only: a register may legitimately contain the text
    "94.0" inside a sentence.
    """
    i, n = 0, len(line)
    while i < n:
        c = line[i]
        if c == '"':                            # a string: skip it, and if it is a key,
            j, key = i + 1, []                  # check what it decodes to
            while j < n:
                if line[j] == "\\":
                    key.append(line[j:j + 2])
                    j += 2
                    continue
                if line[j] == '"':
                    break
                key.append(line[j])
                j += 1
            k = j + 1
            while k < n and line[k] in " \t":
                k += 1
            if k < n and line[k] == ":":        # it was a key
                try:
                    decoded = json.loads('"' + "".join(key) + '"')
                except ValueError:
                    decoded = ""
                if any(ord(ch) > 0x7F for ch in decoded):
                    return True
            i = j + 1
            continue
        if c == "-" or c.isdigit():             # a numeric literal
            j = i
            if line[j] == "-":
                j += 1
            start = j
            while j < n and (line[j].isdigit() or line[j] in ".eE+-"):
                j += 1
            lit = line[start:j]
            if any(ch in lit for ch in ".eE"):
                return True
            if lit and abs(int(lit)) > MAX_INT:
                return True
            i = j
            continue
        i += 1
    return False


# --- the checks --------------------------------------------------------------

HERE = os.path.dirname(os.path.abspath(__file__))


def rows(name):
    with open(os.path.join(HERE, "vectors", name), encoding="utf-8") as f:
        return [json.loads(r) for r in f if r.strip()]


def main():
    bad = 0

    for v in rows("canonical.jsonl"):
        body = json.loads(v["body"])
        got = canonical(body).decode("utf-8")
        if got != v["canonical"]:
            print(f"FAIL canonical/{v['name']}: bytes\n  want {v['canonical']}\n"
                  f"  got  {got}")
            bad += 1
            continue
        if link(v["prev"], body) != v["hash"]:
            print(f"FAIL canonical/{v['name']}: hash")
            bad += 1
            continue
        if violations(body):
            print(f"FAIL canonical/{v['name']}: a conforming vector violates §4 — "
                  f"{violations(body)}")
            bad += 1

    for v in rows("prespec.jsonl"):
        got = is_prespec(v["line"])
        if got != v["detect"]:
            print(f"FAIL prespec/{v['name']}: detect={v['detect']} but got {got}")
            bad += 1

    for v in rows("refused.jsonl"):
        got = bool(violations(json.loads(v["event"])))
        if got != v["refuse"]:
            print(f"FAIL refused/{v['name']}: refuse={v['refuse']} but got {got}")
            bad += 1

    total = len(rows("canonical.jsonl")) + len(rows("prespec.jsonl")) + len(rows("refused.jsonl"))
    if bad:
        print(f"\n{bad} of {total} vectors failed")
        return 1
    print(f"all {total} vectors pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())

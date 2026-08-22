#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Fabio Chinaglia
"""
Registro eventi append-only con catena di hash.

Ogni evento e' una riga JSON. La catena lega ogni evento al precedente:
    h(n) = sha256( h(n-1) || canonical(evento_n) )
Alterare un evento passato invalida tutti gli hash successivi.

Uso:
    python3 registra.py '<json dell evento>'
    python3 registra.py --verifica
    python3 registra.py --radice
"""
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(BASE, "eventi.jsonl")

GENESI = "0" * 64


def canonical(obj) -> bytes:
    """Serializzazione deterministica: chiavi ordinate, niente spazi, UTF-8."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def anello(prev_hash: str, corpo: dict) -> str:
    return hashlib.sha256(prev_hash.encode("ascii") + canonical(corpo)).hexdigest()


def leggi() -> list:
    if not os.path.exists(LOG):
        return []
    with open(LOG, encoding="utf-8") as f:
        return [json.loads(r) for r in f if r.strip()]


def ultimo_hash() -> str:
    righe = leggi()
    return righe[-1]["hash"] if righe else GENESI


def aggiungi(evento: dict) -> dict:
    righe = leggi()
    corpo = dict(evento)
    corpo["seq"] = len(righe)
    corpo.setdefault("ts", datetime.now(timezone.utc).isoformat(timespec="seconds"))
    corpo["prev"] = ultimo_hash()
    riga = {**corpo, "hash": anello(corpo["prev"], corpo)}
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(riga, ensure_ascii=False, sort_keys=True) + "\n")
    return riga


def verifica() -> bool:
    prev = GENESI
    for i, r in enumerate(leggi()):
        corpo = {k: v for k, v in r.items() if k != "hash"}
        if corpo.get("prev") != prev:
            print(f"ROTTA all'evento {i}: prev non corrisponde")
            return False
        if anello(prev, corpo) != r["hash"]:
            print(f"ROTTA all'evento {i}: hash non corrisponde")
            return False
        prev = r["hash"]
    print(f"catena integra — {len(leggi())} eventi — radice {prev[:16]}...")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    if sys.argv[1] == "--verifica":
        sys.exit(0 if verifica() else 1)
    if sys.argv[1] == "--radice":
        print(ultimo_hash())
        sys.exit(0)
    print(json.dumps(aggiungi(json.loads(sys.argv[1])), ensure_ascii=False))

#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Fabio Chinaglia
"""
The technical line of the disclosure note, generated from the register.

The note tells the reader two percentages. This line tells them where to go and
check: how many events the register holds, what its root is, and what sits next to
it. Without it the disclosure is a claim; with it the claim points at something.

Reads events.jsonl and prints the line. Never type this line by hand: a root copied
by hand goes stale the moment another event is recorded, and a stale root is worse
than no root.

    python3 build_note.py                 plain text
    python3 build_note.py --html          an HTML fragment to inject at render time
    python3 build_note.py --lang it       Italian wording

ONE RULE ABOUT ORDER. This line prints the root of the register as it stands.
Generate it AFTER the last event and after sealing, and generate it at render time,
from the register itself. Do not record the act of adding it as an event: the new
event would change the root, and the line would print a value that no longer holds.
The rendered document is not the measured artifact — the source text is — so adding
a generated line to the rendering changes nothing that the register attests.

THE LINE CLAIMS ONLY WHAT EXISTS. Signature, RFC 3161 timestamp and blockchain
anchor are detected separately, and each is named only if its file is on disk. A
disclosure that announces a signature nobody can find is worse than one that admits
there is none: the first is caught by the reader, the second by the author.

Usage: python3 build_note.py [--html] [--lang it|en] [events.jsonl]
"""
import argparse
import json
import os
import sys

LANGS = ("en", "it")

HEAD = {
    "en": "Register: {n} events, root {root}.",
    "it": "Registro: {n} eventi, radice {root}.",
}

# Named only when the corresponding file is present.
SEALS = {
    "en": {"sig": "Ed25519 signature", "tsr": "RFC 3161 timestamp",
           "ots": "Bitcoin anchoring"},
    "it": {"sig": "firma Ed25519", "tsr": "marca temporale RFC 3161",
           "ots": "ancoraggio su Bitcoin"},
}

TAIL = {
    "en": {
        "sealed": " {seals} alongside the register; verification instructions in {doc}.",
        "unsealed": " The register is not sealed: no signature or timestamp yet."
                    " Verification instructions in {doc}.",
        "nodoc": " The register is not sealed: no signature or timestamp yet.",
        "sealed_nodoc": " {seals} alongside the register.",
        "and": " and ",
    },
    "it": {
        "sealed": " {seals} accanto al registro; istruzioni di verifica in {doc}.",
        "unsealed": " Il registro non è sigillato: nessuna firma né marca temporale."
                    " Istruzioni di verifica in {doc}.",
        "nodoc": " Il registro non è sigillato: nessuna firma né marca temporale.",
        "sealed_nodoc": " {seals} accanto al registro.",
        "and": " e ",
    },
}

# The verification page is named by the author, in the author's language. Look for
# what is actually on disk instead of asserting a filename that may not exist.
DOC_NAMES = {
    "en": ("VERIFY.md", "VERIFICA.md"),
    "it": ("VERIFICA.md", "VERIFY.md"),
}


def join(items, lang):
    """Comma-separated list with a proper final conjunction."""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + TAIL[lang]["and"] + items[-1]


def upper_first(s):
    """Capitalise the first letter only.

    str.capitalize() lowercases everything after it, which turns Ed25519 into
    ed25519 and RFC 3161 into rfc 3161 — a technical line that misspells the
    primitives it names invites exactly the doubt it exists to remove.
    """
    return s[:1].upper() + s[1:]


def find_doc(base_dir, lang):
    for name in DOC_NAMES[lang]:
        if os.path.exists(os.path.join(base_dir, name)):
            return name
    return None


def line(log="events.jsonl", lang="en", html=False):
    if lang not in LANGS:
        raise SystemExit(f"unknown language {lang!r}: choose one of {', '.join(LANGS)}")
    if not os.path.exists(log):
        raise SystemExit(f"missing {log}")

    events = []
    for n, row in enumerate(open(log, encoding="utf-8"), 1):
        if not row.strip():
            continue
        try:
            events.append(json.loads(row))
        except json.JSONDecodeError as e:
            raise SystemExit(f"{log}: line {n} is not valid JSON ({e})")
    if not events:
        raise SystemExit(f"{log} is empty")
    if "hash" not in events[-1]:
        raise SystemExit(f"{log}: the last event has no hash — is this a register?")

    root = events[-1]["hash"]
    short = f"{root[:8]}…{root[-8:]}"
    base_dir = os.path.dirname(os.path.abspath(log))

    present = [SEALS[lang][k] for k in ("sig", "tsr", "ots")
               if os.path.exists(f"{log}.{k}")]
    doc = find_doc(base_dir, lang)

    text = HEAD[lang].format(n=len(events), root=short)
    t = TAIL[lang]
    if present and doc:
        text += t["sealed"].format(seals=upper_first(join(present, lang)), doc=doc)
    elif present:
        text += t["sealed_nodoc"].format(seals=upper_first(join(present, lang)))
    elif doc:
        text += t["unsealed"].format(doc=doc)
    else:
        text += t["nodoc"]

    if html:
        out = text.replace(short, f"<code>{short}</code>")
        if doc:
            out = out.replace(doc, f"<code>{doc}</code>")
        return f'<p class="technical">{out}</p>'
    return text


def main():
    p = argparse.ArgumentParser(
        description="Generate the technical line of the disclosure note.",
        epilog="Generate it after the last event and after sealing, at render time.")
    p.add_argument("log", nargs="?", default="events.jsonl",
                   help="register file (default: events.jsonl)")
    p.add_argument("--html", action="store_true",
                   help="emit an HTML fragment instead of plain text")
    p.add_argument("--lang", choices=LANGS, default="en",
                   help="wording language (default: en)")
    a = p.parse_args()
    print(line(a.log, a.lang, a.html))


if __name__ == "__main__":
    main()

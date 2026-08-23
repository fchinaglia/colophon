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
    python3 build_note.py --short-root    the root abbreviated, for a cramped layout
    python3 build_note.py --url URL       where the register is published

THE ROOT IS PRINTED IN FULL. All sixty-four characters, because the reader's job is
to compare it with what they compute themselves, and an abbreviation cannot be
compared — it can only be recognised. At 7pt it takes about ninety millimetres, so
it fits the column the note sits in. --short-root exists for a social card or a slide
and nowhere else.

AND WITH AN ADDRESS. A line that names VERIFY.md tells a reader standing in the case
folder where to look, and tells a reader on a social post nothing at all: "alongside
the register" presupposes that they have the register. Put the addresses in case.json
and the line carries one of them:

    "verification_url"  the published verification page — preferred, it is the artefact
                        written for a reader, and the register is reachable from it
    "register_url"      the case folder, used when there is no page

--url overrides both. Without any of them the line still prints, and the script says on
stderr what the reader will be missing.

THE ADDRESS IS A PROMISE. This line is generated at render time, so a PDF or a printed
page freezes whatever it said that day and will never update it. Choose an address you
are prepared to keep: do not move a case folder, do not rename it. A dead link under a
disclosure is worse than no link, because it looks like evidence from a distance.

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

Usage: python3 build_note.py [--html] [--lang it|en] [--url URL] [--short-root] [events.jsonl]
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

# Where the register is published. Read from the case metadata, so that the line stays
# generated and the address is written once, in the file that already describes the case.
CASE_FILES = ("case.json", "caso.json")
# Two addresses, and the line prints one. The verification page comes first: it is the
# artefact written for a reader, and the register is reachable from it. A reader sent
# straight to the raw files has been handed the evidence and not the door.
PAGE_KEYS = ("verification_url", "url_verifica")
URL_KEYS = ("register_url", "url_registro")

# Named only when the corresponding file is present.
SEALS = {
    "en": {"sig": "Ed25519 signature", "tsr": "RFC 3161 timestamp",
           "ots": "Bitcoin anchoring"},
    "it": {"sig": "firma Ed25519", "tsr": "marca temporale RFC 3161",
           "ots": "ancoraggio su Bitcoin"},
}

TAIL = {
    "en": {
        "seals": " {seals} alongside the register.",
        "unsealed": " The register is not sealed: no signature or timestamp yet.",
        "at_page": " Verification page, with the register alongside it: {where}.",
        "at_url": " Register and verification instructions: {where}.",
        "at_doc": " Verification instructions in {where}.",
        "and": " and ",
        "no_address": "no {keys} in {files}, and --url not given: the line names no place"
                      " to go. A reader who is not already inside the case folder cannot"
                      " reach the register.",
    },
    "it": {
        "seals": " {seals} accanto al registro.",
        "unsealed": " Il registro non è sigillato: nessuna firma né marca temporale.",
        "at_page": " Pagina di verifica, con il registro accanto: {where}.",
        "at_url": " Registro e istruzioni di verifica: {where}.",
        "at_doc": " Istruzioni di verifica in {where}.",
        "and": " e ",
        "no_address": "nessun {keys} in {files}, e --url non passato: la riga non indica"
                      " nessun posto dove andare. Un lettore che non sia già dentro la"
                      " cartella del caso non può raggiungere il registro.",
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


def find_url(base_dir, keys):
    """An address of the case, from its metadata file."""
    for name in CASE_FILES:
        path = os.path.join(base_dir, name)
        if not os.path.exists(path):
            continue
        try:
            case = json.load(open(path, encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        for key in keys:
            if case.get(key):
                return str(case[key]).strip()
    return None


def shown(url):
    """What the reader sees: the address without the scheme, which they do not type."""
    return url.split("://", 1)[-1].rstrip("/")


def line(log="events.jsonl", lang="en", html=False, url=None, short_root=False):
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
    printed_root = f"{root[:8]}…{root[-8:]}" if short_root else root
    base_dir = os.path.dirname(os.path.abspath(log))
    t = TAIL[lang]

    present = [SEALS[lang][k] for k in ("sig", "tsr", "ots")
               if os.path.exists(f"{log}.{k}")]
    page = None if url else find_url(base_dir, PAGE_KEYS)
    url = url or page or find_url(base_dir, URL_KEYS)
    doc = find_doc(base_dir, lang)

    text = HEAD[lang].format(n=len(events), root=printed_root)
    text += (t["seals"].format(seals=upper_first(join(present, lang))) if present
             else t["unsealed"])

    # An address beats a filename: the filename only helps a reader who already has
    # the folder, which is the one reader who did not need telling.
    where = shown(url) if url else doc
    if url:
        text += t["at_page" if page else "at_url"].format(where=where)
    elif doc:
        text += t["at_doc"].format(where=where)
    else:
        print("build_note.py: " + t["no_address"].format(
            keys=" / ".join(PAGE_KEYS + URL_KEYS), files=" or ".join(CASE_FILES)),
              file=sys.stderr)

    if html:
        out = text.replace(printed_root, f"<code>{printed_root}</code>")
        if url:
            out = out.replace(where, f'<a href="{url}">{where}</a>')
        elif doc:
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
    p.add_argument("--url", default=None,
                   help="where the register is published; overrides the case metadata")
    p.add_argument("--short-root", action="store_true",
                   help="abbreviate the root — for a social card or a slide, not for a page")
    a = p.parse_args()
    print(line(a.log, a.lang, a.html, a.url, a.short_root))


if __name__ == "__main__":
    main()

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
    python3 build_note.py --form full     one sentence naming every seal
    python3 build_note.py --attached      the register is enclosed, as a bundle

THE ROOT IS PRINTED IN FULL. All sixty-four characters, because the reader's job is
to compare it with what they compute themselves, and an abbreviation cannot be
compared — it can only be recognised. At 7pt it takes about ninety millimetres, so
it fits the column the note sits in. --short-root exists for a social card or a slide
and nowhere else.

AND WITH A ROUTE. A line that names VERIFY.md tells a reader standing in the case
folder where to look, and tells a reader on a social post nothing at all: "alongside
the register" presupposes that they have the register. There is one route, and it is
the bundle: the record travels with the document, and --attached says so.

    --attached          the register is enclosed, as colophon-<case_uid>.tar

Without it the line still prints, and the script says on stderr what the reader will
be missing.

THE ENCLOSURE IS A PROMISE ABOUT A FILE, so --attached refuses when the bundle it would
name is not on disk. A line telling a reader the record is enclosed while nothing is
enclosed is worse than a line admitting there is no route: it looks like evidence from
a distance. Build the bundle first, and the promise is one the folder can keep — which
is the whole reason the route is a file and not an address. Nothing has to stay online,
no domain has to be renewed, and nobody has to be alive in ten years.

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

Usage: python3 build_note.py [--html] [--lang it|en] [--attached] [--short-root] [events.jsonl]
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

# Read from the case metadata, so that the line stays generated and the name of the
# bundle is written once, in the file that already describes the case.
CASE_FILES = ("case.json", "caso.json")

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
        "at_doc": " Verification instructions in {where}.",
        "attached": " The register is enclosed with this document, as {tar}: drop it on"
                    " verify.html and everything above is checked offline.",
        "and": " and ",
        "no_route": "--attached not given: the line names no route to the record. A"
                    " reader who is not already inside the case folder cannot reach the"
                    " register.",
        "have_tar": " {tar} is on disk — pass --attached if it travels with the"
                    " document.",
    },
    "it": {
        "seals": " {seals} accanto al registro.",
        "unsealed": " Il registro non è sigillato: nessuna firma né marca temporale.",
        "at_doc": " Istruzioni di verifica in {where}.",
        "attached": " Il registro è accluso a questo documento, come {tar}: trascinalo"
                    " su verify.html e tutto quanto sopra è verificato offline.",
        "and": " e ",
        "no_route": "--attached non passato: la riga non indica nessuna via al record."
                    " Un lettore che non sia già dentro la cartella del caso non può"
                    " raggiungere il registro.",
        "have_tar": " {tar} è sul disco — passa --attached se viaggia con il documento.",
    },
}

# The compact form: three short lines instead of a sentence. It is the default because
# it is what goes under an article, where a paragraph of prose in a monospace face is
# not read. The long form stays available for a page that has room to explain itself.
# "signed and inspectable register" said two things at once and only checked one. A
# register with no route is not inspectable by the reader holding the document, and the
# line printed the claim anyway. The first line now states the seal; the second states
# the route, and there is one — the enclosure, or the admission that there is none.
COMPACT = {
    "en": {"attached": "signed register, enclosed",
           "held": "signed register, not enclosed",
           "unsealed": "register not sealed yet — no signature or timestamp",
           "retrieval": "verify offline: drop {tar} on verify.html",
           "root": "root {root}"},
    "it": {"attached": "registro firmato, accluso",
           "held": "registro firmato, non accluso",
           "unsealed": "registro non ancora sigillato — nessuna firma né marca temporale",
           "retrieval": "verifica offline: trascina {tar} su verify.html",
           "root": "radice {root}"},
}

# The verification page is named by the author, in the author's language. Look for
# what is actually on disk instead of asserting a filename that may not exist.
DOC_NAMES = {
    "en": ("VERIFY.md", "VERIFICA.md"),
    "it": ("VERIFICA.md", "VERIFY.md"),
}


def bundle_name(base_dir):
    """The tar is named after case_uid, which is why case_uid is fixed at the opening:
    once the file is detached from the folder that made it, its name is all that says
    which case it belongs to."""
    for fn in ("case.json", "caso.json"):
        try:
            uid = json.load(open(os.path.join(base_dir, fn), encoding="utf-8")).get("case_uid")
        except (OSError, ValueError):
            continue
        if uid:
            return f"colophon-{uid}.tar"
    return None


def find_bundle(base_dir, given, name):
    """A line that names an enclosure is a promise about a file, so look for the file.

    Without this, --attached is a flag: it prints `signed register, enclosed` and names a
    tar, and nothing anywhere checks that the tar was ever built. That is #16 in a new
    costume — a route under a disclosure that does not lead anywhere — and it is silent,
    which is what makes it worth a refusal rather than a warning.
    """
    if given:
        return given if os.path.exists(given) else False
    if not name:
        return False
    for cand in (os.path.join(os.path.dirname(base_dir), name),
                 os.path.join(base_dir, name),
                 name):
        if os.path.exists(cand):
            return cand
    return False


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


def warn_no_route(lang, found_tar):
    """Say what the reader will be missing — and, when the bundle is right there, say
    that too. Under-claiming is the safe failure of the two, but an author who built the
    tar and forgot the flag gets a line that denies the route they have."""
    msg = TAIL[lang]["no_route"]
    if found_tar:
        msg += TAIL[lang]["have_tar"].format(tar=os.path.basename(found_tar))
    print("build_note.py: " + msg, file=sys.stderr)


def html_escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def line(log="events.jsonl", lang="en", html=False,
         short_root=False, form="compact", attached=False, bundle=None):
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
    # The whole root, in either form: an abbreviation can be recognised but not
    # compared, and comparing is the reader's job. --short-root is for a card or a
    # slide, where the line has to survive at any cost.
    printed_root = f"{root[:8]}…{root[-8:]}" if short_root else root
    base_dir = os.path.dirname(os.path.abspath(log))
    t = TAIL[lang]

    present = [SEALS[lang][k] for k in ("sig", "tsr", "ots")
               if os.path.exists(f"{log}.{k}")]
    tar = bundle_name(base_dir)
    found = find_bundle(base_dir, bundle, tar)
    if attached and not found:
        raise SystemExit(
            f"! --attached names {tar or 'a bundle'} and there is none.\n"
            f"  The line would tell a reader the record is enclosed with the document,\n"
            f"  and nothing would be. Run build_bundle.py first, or pass --bundle PATH,\n"
            f"  or drop --attached and let the line say what is true."
            + ("" if tar else "\n  (case.json carries no case_uid, so the bundle has no"
                              " name to look for either.)"))
    doc = find_doc(base_dir, lang)

    where = doc

    if form == "compact":
        c = COMPACT[lang]
        if not present:
            rows = [c["unsealed"]]
        elif attached:
            rows = [c["attached"]]
        else:
            rows = [c["held"]]
        if attached:
            rows.append(c["retrieval"].format(tar=tar))
        # The event count is not here: the verification page inside the bundle prints
        # it, and the word that qualifies the hash matters more than the number that
        # precedes it. Without "root", the last line is an unidentified string.
        rows.append(c["root"].format(root=printed_root))
        if not attached and not doc:
            warn_no_route(lang, found)
        if html:
            body = "<br>".join(html_escape(r) for r in rows)
            return f'<p class="technical">{body}</p>'
        return "\n".join(rows)

    text = HEAD[lang].format(n=len(events), root=printed_root)
    text += (t["seals"].format(seals=upper_first(join(present, lang))) if present
             else t["unsealed"])

    # The enclosure beats a filename: the filename only helps a reader who already has
    # the folder, which is the one reader who did not need telling.
    if attached:
        text += t["attached"].format(tar=tar)
    elif doc:
        text += t["at_doc"].format(where=where)
    else:
        warn_no_route(lang, found)

    if html:
        out = text.replace(printed_root, f"<code>{printed_root}</code>")
        if not attached and doc:
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
    p.add_argument("--attached", action="store_true",
                   help="the record is enclosed with the document, as a bundle")
    p.add_argument("--bundle", default=None,
                   help="where that bundle is, if not beside the case")
    p.add_argument("--short-root", action="store_true",
                   help="abbreviate the root — for a card or a slide, not for a page")
    p.add_argument("--form", choices=("compact", "full"), default="compact",
                   help="compact: three short lines, the default. full: one sentence "
                        "naming every seal, with the root in full")
    a = p.parse_args()
    print(line(a.log, a.lang, a.html, a.short_root, a.form, a.attached, a.bundle))


if __name__ == "__main__":
    main()

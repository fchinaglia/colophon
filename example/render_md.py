#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Fabio Chinaglia
"""
The published document: the measured text, with the disclosure around it.

Takes the version the closing manifest covers, adds the level-1 marker under the title
and the level-2 block at the foot, and writes the markdown a reader receives. It adds;
it never rewrites. The body of the output is the body of the source, byte for byte.

WHY THIS IS A SCRIPT AND NOT AN INSTRUCTION. The alternative is assembling the document
by hand, and the hand-assembled one for the validation case carried `1096` where the
generator says `1.096`, an `<img src="icon.svg">` that breaks the moment the file travels
alone, and a technical line copied from a terminal. None of those is visible in the
finished document: they are all wrong in a way that still looks right.

THE GATE. Before anything, the source is hashed and compared against the manifest. A
document rendered from a file the measurement never saw would carry percentages about a
different text — and once a qualified signature is over it, the reader will read
*this file is unaltered* as *this text is the text that was measured*. Those are two
claims and only one of them is being made. The comparison is what keeps them apart, so
it is not optional and there is no flag to skip it.

WHY THIS IS NOT COVERED BY THE MANIFEST, and neither is what it writes. The block
carries the root; the root is the hash of the manifest event; the manifest covers the
source. A source cannot contain the fingerprint of a chain that fingerprints it. So the
published document is a rendering — derivable from what is covered, made after the seal —
and this script is a rendering script. The convention across the skill: **build_* is
covered by the manifest, render_* is not.**

    python3 render_md.py                    the document, from the covered version
    python3 render_md.py --lang it
    python3 render_md.py --gap "…"          the sentence that is a judgement
    python3 render_md.py --block md         plain lines instead of the prescribed table
    python3 render_md.py --no-marker        skip the line under the title
    python3 render_md.py -o articolo.md

THE ICON IS INLINED BY DEFAULT, because this file travels without the folder that holds
`icon.svg` — that is the whole point of it. `--linked-icon` restores the reference for a
document published inside its own case folder.

Usage: python3 render_md.py [--lang it|en] [-o OUT]
"""
import argparse
import hashlib
import json
import os
import sys

import build_block
import build_icon
import build_note

MARKER = {
    "en": ("*Written with the assistance of a language model and tracked with the "
           "Colophon method. The method note, with the contribution percentages, is "
           "at the bottom.*"),
    "it": ("*Scritto con l'assistenza di un modello linguistico e tracciato con il "
           "metodo Colophon. La nota sul metodo, con le percentuali di contributo, "
           "è in fondo.*"),
}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def manifest_of(log):
    rows = [json.loads(l) for l in open(log, encoding="utf-8") if l.strip()]
    if not rows:
        raise SystemExit(f"{log}: the register is empty")
    for r in reversed(rows):
        d = (r.get("payload") or {}).get("sha256")
        if isinstance(d, dict):
            return d, rows
    raise SystemExit(f"{log}: no closing manifest. The document would carry a root over "
                     f"a register that does not commit to the text — seal the case first.")


def covered_source(manifest, given):
    """The one version the manifest covers is the measured text: it is what measure.py
    reconstructed from the spans, and the only file whose percentages the block states."""
    if given:
        return given
    versions = sorted(k for k in manifest if k.startswith("versions/"))
    if len(versions) == 1:
        return versions[0]
    if not versions:
        raise SystemExit("the manifest covers no file under versions/ — name the source "
                         "with --source")
    raise SystemExit(f"the manifest covers {len(versions)} versions "
                     f"({', '.join(versions)}) — name the one to publish with --source")


def insert_after_title(body, block):
    """Under the title, which is where a reader meets the piece — never at the very top,
    above the thing they came for."""
    lines = body.split("\n")
    for i, l in enumerate(lines):
        if l.startswith("# "):
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            return "\n".join(lines[:j] + [block, ""] + lines[j:])
    return block + "\n\n" + body


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    p.add_argument("--log", default="events.jsonl")
    p.add_argument("--kpi", default="kpi.json")
    p.add_argument("--icon", default="icon.svg")
    p.add_argument("--case", default="case.json")
    p.add_argument("--source", default=None, help="the covered version to publish")
    p.add_argument("--lang", choices=sorted(MARKER), default="en")
    p.add_argument("--block", choices=("html", "md", "svg"), default="html")
    p.add_argument("--gap", default=None)
    p.add_argument("--byline", default=None, help="replace the author and date line")
    p.add_argument("--no-byline", action="store_true")
    p.add_argument("--no-marker", action="store_true")
    p.add_argument("--linked-icon", action="store_true",
                   help="reference icon.svg instead of inlining it")
    p.add_argument("--url", default=None)
    p.add_argument("-o", "--out", default=None)
    a = p.parse_args(argv)

    manifest, rows = manifest_of(a.log)
    src = covered_source(manifest, a.source)
    if not os.path.exists(src):
        raise SystemExit(f"missing {src}, which the manifest covers")

    got, want = sha256_file(src), manifest[src]
    if got != want:
        raise SystemExit(
            f"! {src} is not the file the manifest covers.\n"
            f"    manifest {want}\n"
            f"    on disk  {got}\n"
            f"  The measurement describes the covered bytes. Rendering these ones would\n"
            f"  publish percentages about a different text. Either restore the file, or\n"
            f"  reopen the case: a new event saying why, a new manifest, a new seal.")

    if not os.path.exists(a.log + ".sig"):
        print(f"  ! {a.log}.sig is missing: this document will carry the root of an "
              f"unsigned register.\n    The block says so to the reader, but seal first "
              f"and render after.", file=sys.stderr)

    kpi = json.load(open(a.kpi, encoding="utf-8"))
    build_icon.refuse_if_ungated(kpi, a.kpi)
    try:
        case = json.load(open(a.case, encoding="utf-8"))
    except (OSError, ValueError):
        case = {}

    lines, name, xl, yi = build_block.note_lines(kpi, a.lang, a.gap)
    alt = build_block.T[a.lang]["alt"].format(name=name, x=f"{xl:.0f}", y=f"{yi:.0f}")
    tech = build_block.technical(a.log, a.lang, a.url,
                                 "html" if a.block == "html" else "text", False)

    if a.block == "svg":
        svg, _ = build_icon.icon(xl / 100, yi / 100)
        out_svg = (os.path.splitext(a.out or "document.md")[0] + "-colophon.svg")
        open(out_svg, "w", encoding="utf-8", newline="\n").write(
            build_block.as_svg(lines, tech, svg, alt) + "\n")
        block = f'![{alt}]({os.path.basename(out_svg)})'
    elif a.block == "md":
        icon_ref = f'![{alt}]({a.icon})\n\n'
        # Two trailing spaces: consecutive lines are one paragraph in markdown, and
        # the five lines would arrive as a single run-on sentence.
        body = "  \n".join(build_block.render_line(t, b, "**", "**") for t, b in lines)
        block = icon_ref + body + "\n\n```\n" + tech + "\n```"
    else:
        if a.linked_icon:
            icon_src = f'<img src="{build_block.esc(a.icon)}" alt="{build_block.esc(alt)}">'
        else:
            if not os.path.exists(a.icon):
                raise SystemExit(f"missing {a.icon} — run build_icon.py first, or pass "
                                 f"--linked-icon")
            icon_src = open(a.icon, encoding="utf-8").read().strip()
        block = build_block.as_html(lines, tech, icon_src, alt)

    body = open(src, encoding="utf-8").read().rstrip("\n")
    head = []
    if not a.no_byline:
        head.append(a.byline if a.byline is not None else
                    f"*{case.get('author', '—')} · {case.get('date', '—')}*")
    if not a.no_marker:
        head.append(MARKER[a.lang])
    if head:
        body = insert_after_title(body, "\n\n".join(head) + "\n\n---")

    doc = body + "\n\n---\n\n" + block + "\n"
    out = a.out or f"{case.get('case_uid') or 'document'}.md"
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(doc)

    print(f"  {out}")
    print(f"  source    {src}  {want[:16]}…  matches the manifest")
    print(f"  block     {name}, {len(lines)} lines, {a.block}")
    print(f"  body      {len(body.encode('utf-8')):,} bytes, unchanged from the source")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Fabio Chinaglia
"""
The published PDF: the measured text, the disclosure block, printed through Chrome.

Same gate as render_md.py, and it is the point of both: the source is hashed against the
closing manifest before anything is rendered. Once a qualified signature is over a PDF,
the reader will read *this file is unaltered since signing* as *this text is the text
that was measured*. Those are two claims. The gate is what keeps them apart, so there is
no flag to skip it.

MARKDOWN, IN A DELIBERATELY SMALL SUBSET. Headings, paragraphs, bold, italic, code,
links, images, blockquotes, flat lists, rules, and raw HTML passed through — which is
how the disclosure block arrives. **Anything outside that subset is refused by line
number, never rendered approximately.** A converter that silently mangles a table
publishes something the author did not write under a signature that says they did, and
that failure is invisible in the finished PDF.

The one rule the converter obeys: it wraps, it never rewrites. `--check` asserts it —
every word of the source, in order, comes out the other side.

THIS IS A RENDERING and it is covered by no manifest, like the script that makes it:
build_* is covered, render_* is not. Both carry the root, which is the hash of the
manifest event, so neither can exist before the seal.

    python3 render_pdf.py                  the HTML and the PDF
    python3 render_pdf.py --html-only      stop before Chrome
    python3 render_pdf.py --lang it
    python3 render_pdf.py --gap "…"        the sentence that is a judgement

NOT PDF/A-3. Chrome's output has no output intent, no conformant XMP and no guaranteed
embedded fonts. Calling it PDF/A without a veraPDF run would be exactly the unbackable
compliance claim disclosures.md forbids, in the one artefact whose job is to be checkable.

Usage: python3 render_pdf.py [--lang it|en] [-o OUT]
"""
import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys

import build_block
import build_icon
import render_md

CHROMES = ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
           "/Applications/Chromium.app/Contents/MacOS/Chromium",
           "google-chrome", "chromium", "chromium-browser")

# Constructs the converter does not implement. Refused by line number rather than
# rendered approximately: a mangled table under a signature is worse than a stop.
UNSUPPORTED = [
    (re.compile(r"^\s*\|"), "a table"),
    (re.compile(r"^\s*={3,}\s*$"), "a setext heading — use `#`"),
    (re.compile(r"\[\^"), "a footnote"),
    (re.compile(r"^\s{2,}[-*+]\s"), "a nested list"),
    (re.compile(r"^\s*\[[^\]]+\]:\s"), "a reference link definition"),
]

INLINE = [
    (re.compile(r"`([^`]+)`"), r"<code>\1</code>"),
    (re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)"), r'<img src="\2" alt="\1">'),
    (re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)"), r'<a href="\2">\1</a>'),
    (re.compile(r"\*\*([^*]+)\*\*"), r"<strong>\1</strong>"),
    (re.compile(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])"), r"<em>\1</em>"),
    (re.compile(r"(?<![\w_])_([^_\n]+)_(?![\w_])"), r"<em>\1</em>"),
]

CSS = """
@page { size: A4; margin: 22mm 20mm 20mm; }
html { font-size: 10.5pt; }
body { font-family: Georgia, "Iowan Old Style", serif; line-height: 1.62;
       color: #16171a; background: #fcfcfb; margin: 0; }
h1 { font-size: 20pt; line-height: 1.22; margin: 0 0 4mm; text-wrap: balance;
     font-family: ui-sans-serif, -apple-system, sans-serif; letter-spacing: -.01em; }
h2 { font-size: 13pt; margin: 8mm 0 2mm; font-family: ui-sans-serif, sans-serif; }
h3 { font-size: 11pt; margin: 6mm 0 2mm; font-family: ui-sans-serif, sans-serif; }
p  { margin: 0 0 3.2mm; }
a  { color: inherit; text-decoration: underline; text-underline-offset: 2px; }
code { font-family: ui-monospace, monospace; font-size: .88em; }
pre  { font-family: ui-monospace, monospace; font-size: 8.5pt; line-height: 1.45;
       background: #f4f4f2; padding: 3mm 4mm; overflow-x: auto; }
blockquote { margin: 0 0 3.2mm; padding-left: 5mm; border-left: 2px solid #d8d8d4;
             color: #4a4b4e; }
ul, ol { margin: 0 0 3.2mm; padding-left: 6mm; }
li { margin: 0 0 1mm; }
hr { border: 0; border-top: 1px solid #e0e0dc; margin: 7mm 0; }
img { max-width: 100%; }
.byline { font-family: ui-sans-serif, sans-serif; font-size: 9pt; color: #6f7074;
          margin: 0 0 2mm; }
.marker { font-family: ui-sans-serif, sans-serif; font-size: 8.5pt; color: #6f7074;
          font-style: italic; margin: 0 0 6mm; }
"""


def refuse_unsupported(text):
    bad = []
    fenced = False
    for n, line in enumerate(text.split("\n"), 1):
        if line.startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        for rx, what in UNSUPPORTED:
            if rx.search(line):
                bad.append(f"    line {n}: {what}")
    if bad:
        raise SystemExit("! this source uses markdown the renderer does not implement:\n"
                         + "\n".join(bad) +
                         "\n  It refuses rather than rendering something you did not"
                         "\n  write. Rewrite those lines, or render the HTML yourself.")


def inline(s):
    s = html.escape(s, quote=False)
    for rx, rep in INLINE:
        s = rx.sub(rep, s)
    return s


def to_html(text):
    """Blocks, in the order a line can only be one of them."""
    out, buf, lines, i = [], [], text.split("\n"), 0

    def flush():
        if buf:
            out.append("<p>" + inline(" ".join(buf).strip()) + "</p>")
            buf.clear()

    while i < len(lines):
        l = lines[i]
        if l.startswith("```"):
            flush()
            i += 1
            code = []
            while i < len(lines) and not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            out.append("<pre>" + html.escape("\n".join(code)) + "</pre>")
        elif l.lstrip().startswith("<") and not l.lstrip().startswith("<http"):
            # Raw HTML, passed through: this is how the disclosure block arrives, and
            # rewriting it would defeat build_block.py having generated it.
            flush()
            out.append(l)
        elif re.match(r"^#{1,6} ", l):
            flush()
            n = len(l) - len(l.lstrip("#"))
            out.append(f"<h{n}>{inline(l[n:].strip())}</h{n}>")
        elif re.match(r"^\s*(\*\s*){3,}$|^\s*-{3,}\s*$|^\s*_{3,}\s*$", l):
            flush()
            out.append("<hr>")
        elif re.match(r"^\s*[-*+] ", l) or re.match(r"^\s*\d+\. ", l):
            flush()
            ordered = bool(re.match(r"^\s*\d+\. ", l))
            items = []
            while i < len(lines) and (re.match(r"^\s*[-*+] ", lines[i])
                                      or re.match(r"^\s*\d+\. ", lines[i])):
                items.append(inline(re.sub(r"^\s*([-*+]|\d+\.) ", "", lines[i])))
                i += 1
            i -= 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{x}</li>" for x in items) + f"</{tag}>")
        elif l.startswith("> "):
            flush()
            q = []
            while i < len(lines) and lines[i].startswith("> "):
                q.append(lines[i][2:])
                i += 1
            i -= 1
            out.append("<blockquote><p>" + inline(" ".join(q)) + "</p></blockquote>")
        elif not l.strip():
            flush()
        else:
            buf.append(l.rstrip())
        i += 1
    flush()
    return "\n".join(out)


def words(s):
    return re.findall(r"\w+", s, re.UNICODE)


def prose(source):
    """What the source says, with everything the converter is allowed to drop removed:
    the target of a link or an image, which becomes an attribute and not text; a raw HTML
    line, which passes through as markup; and the markers themselves."""
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r" \1 ", source)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r" \1 ", text)
    text = "\n".join(l for l in text.split("\n") if not l.lstrip().startswith("<"))
    return words(re.sub(r"[`*_#>\[\]()!-]", " ", text))


def check_nothing_was_rewritten(source, rendered):
    """The converter wraps; it never rewrites. Compared as word sequences, because the
    markers are what disappear and the words are what must not."""
    src = prose(source)
    got = words(re.sub(r"<[^>]+>", " ", html.unescape(rendered)))
    if src != got[:len(src)] and src != got:
        i = next((k for k in range(min(len(src), len(got))) if src[k] != got[k]),
                 min(len(src), len(got)))
        raise SystemExit(f"! the converter changed the text at word {i}:\n"
                         f"    source   …{' '.join(src[max(0,i-4):i+4])}…\n"
                         f"    rendered …{' '.join(got[max(0,i-4):i+4])}…\n"
                         f"  This is the one thing it may never do. Do not publish.")


def find_chrome():
    for c in CHROMES:
        if os.path.exists(c):
            return c
        w = shutil.which(c)
        if w:
            return w
    return None


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    p.add_argument("--log", default="events.jsonl")
    p.add_argument("--kpi", default="kpi.json")
    p.add_argument("--icon", default="icon.svg")
    p.add_argument("--case", default="case.json")
    p.add_argument("--source", default=None)
    p.add_argument("--lang", choices=sorted(render_md.MARKER), default="en")
    p.add_argument("--gap", default=None)
    p.add_argument("--byline", default=None)
    p.add_argument("--no-byline", action="store_true")
    p.add_argument("--no-marker", action="store_true")
    p.add_argument("--url", default=None)
    p.add_argument("--attached", action="store_true",
                   help="the record travels with this file, as a bundle")
    p.add_argument("--html-only", action="store_true", help="stop before Chrome")
    p.add_argument("-o", "--out", default=None, help="the PDF path")
    a = p.parse_args(argv)

    src, manifest, rows = render_md.gate(a.log, a.source)

    kpi = json.load(open(a.kpi, encoding="utf-8"))
    build_icon.refuse_if_ungated(kpi, a.kpi)
    try:
        case = json.load(open(a.case, encoding="utf-8"))
    except (OSError, ValueError):
        case = {}

    source = open(src, encoding="utf-8").read()
    refuse_unsupported(source)
    body = to_html(source)
    check_nothing_was_rewritten(source, body)

    lines, name, xl, yi = build_block.note_lines(kpi, a.lang, a.gap)
    alt = build_block.T[a.lang]["alt"].format(name=name, x=f"{xl:.0f}", y=f"{yi:.0f}")
    tech = build_block.technical(a.log, a.lang, a.url, "html", False, a.attached)
    if not os.path.exists(a.icon):
        raise SystemExit(f"missing {a.icon} — run build_icon.py first")
    block = build_block.as_html(lines, tech, open(a.icon, encoding="utf-8").read().strip(),
                                alt)

    head = []
    if not a.no_byline:
        head.append('<p class="byline">' + build_block.esc(
            a.byline if a.byline is not None else
            f"{case.get('author', '—')} · {case.get('date', '—')}") + "</p>")
    if not a.no_marker:
        head.append('<p class="marker">' + build_block.esc(
            render_md.MARKER[a.lang].strip("*")) + "</p>")

    # Under the title, never above it: the reader came for the piece.
    m = re.search(r"</h1>", body)
    if m and head:
        body = body[:m.end()] + "\n" + "\n".join(head) + body[m.end():]
    elif head:
        body = "\n".join(head) + "\n" + body

    uid = case.get("case_uid") or "document"
    out_pdf = a.out or f"{uid}.pdf"
    out_html = os.path.splitext(out_pdf)[0] + ".html"
    doc = (f'<!DOCTYPE html>\n<html lang="{a.lang}"><head><meta charset="utf-8">\n'
           f'<title>{build_block.esc(case.get("title", uid))}</title>\n'
           f"<style>{CSS}{build_block.CSS}</style></head><body>\n"
           f"{body}\n<hr>\n{block}\n</body></html>\n")
    with open(out_html, "w", encoding="utf-8", newline="\n") as f:
        f.write(doc)
    print(f"  {out_html}")
    print(f"  source    {src}  {manifest[src][:16]}…  matches the manifest")
    print(f"  block     {name}, {len(lines)} lines")

    if a.html_only:
        return 0
    chrome = find_chrome()
    if not chrome:
        print("  ! no Chrome or Chromium found. The HTML above is complete: print it\n"
              "    yourself, or pass --html-only to stop here without this warning.",
              file=sys.stderr)
        return 1
    subprocess.run([chrome, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={os.path.abspath(out_pdf)}",
                    os.path.abspath(out_html)], check=True, capture_output=True)
    print(f"  {out_pdf}  {os.path.getsize(out_pdf):,} bytes")
    print("  not PDF/A-3, and do not call it that: no output intent, no conformant XMP.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

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
    python3 render_pdf.py --embed          with the bundle inside it, as one file
    python3 render_pdf.py --html-only      stop before Chrome
    python3 render_pdf.py --lang it
    python3 render_pdf.py --gap "…"        the sentence that is a judgement

EMBEDDING IS AN INCREMENTAL UPDATE, and the order is fixed: **embed, then sign.** PAdES
is itself an incremental update, so a signature added after this covers the revision that
holds the attachment; signing first and embedding after leaves the signature over an
earlier revision, which Acrobat reports as *signed, then modified* — worse than broken,
because it reads as tampering. Verified here: poppler lists and extracts the bundle byte
for byte, the document still renders in poppler and PDFium, and the original bytes are
untouched. **What is not verified is what a real signing client does to it** — see the
four checks in docs/plan-local-first.md before relying on a signed embedded bundle.

NOT PDF/A-3. Chrome's output has no output intent, no conformant XMP and no guaranteed
embedded fonts. Calling it PDF/A without a veraPDF run would be exactly the unbackable
compliance claim disclosures.md forbids, in the one artefact whose job is to be checkable.

Usage: python3 render_pdf.py [--lang it|en] [-o OUT]
"""
import argparse
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import zlib

import build_block
import build_icon
import build_note
import render_md

# Two lists, because they answer two different questions and one of them used to be
# asked wrongly. Issue #39: every entry was tried with os.path.exists() first, and for a
# bare name that is a question about the working directory — a file called
# `google-chrome` beside a case was handed to subprocess.run as a browser.
#
# Absolute paths, for the installs the PATH does not reach: macOS keeps its browsers in
# /Applications, snap and flatpak put a launcher where a shell will not find it either.
CHROME_PATHS = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/snap/bin/chromium",
    "/var/lib/flatpak/exports/bin/org.chromium.Chromium",
    os.path.expanduser("~/.local/share/flatpak/exports/bin/org.chromium.Chromium"),
)
# Names to look for on the PATH. `google-chrome-stable` is what Google's own .deb and
# .rpm install; `google-chrome` is usually a symlink beside it and is not always there,
# which is how a Linux machine with Chrome installed reported having none — at the last
# step of a case whose register was already sealed.
CHROME_NAMES = ("google-chrome", "google-chrome-stable",
                "chromium", "chromium-browser")

# Kept as the flat sequence it always was: other code reads it.
CHROMES = CHROME_PATHS + CHROME_NAMES

# How long the rendering may take before it is treated as stalled rather than slow.
# Headless Chrome does not always exit — a stale profile lock, a crashpad handler that is
# never reaped — and `subprocess.run` with no deadline waits for it forever. That wait
# lands in the middle of closing a case, where the author sees a program that printed its
# progress and then stopped, with nothing to tell a hopeless wait from a slow one. Nine
# minutes is generous for a real render on unknown hardware and short enough that a stall
# is answered rather than sat through.
CHROME_SECONDS = 540

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


def promote_title(body, title):
    """A source written before the deliverable was markdown carries its title as an
    ordinary first paragraph, and the renderer would set it at body size with the
    marker above it — which is the one placement disclosures.md forbids.

    Promoted only when the first paragraph is *exactly* the title `case.json` declares.
    That is a fact check against a value the manifest covers, not a guess about
    structure: when they differ, nothing happens, and no word is ever touched.
    """
    if not title:
        return body
    m = re.match(r"\s*<p>(.*?)</p>", body, re.S)
    if m and html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() == title.strip():
        return body[:m.start()] + f"<h1>{m.group(1)}</h1>" + body[m.end():]
    return body


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


# ---------------------------------------------------------------- embedding, --embed
#
# An incremental update: the original bytes are not touched, new objects are appended
# after them, and a new cross-reference section points at both. That is the only shape
# that survives being signed afterwards — PAdES is itself an incremental update, so a
# signature added later covers this revision, while embedding into a signed file would
# make Acrobat report "signed, then modified", which reads as tampering rather than as
# breakage. **Embed first, sign second, always.**
#
# What is implemented is what headless Chrome writes and nothing else: PDF 1.4, a classic
# xref table, no object streams, no cross-reference streams, no encryption. Every one of
# those is checked and refused rather than guessed at. A malformed incremental update
# opens in some readers and not in others, silently, which is the worst failure available
# here — a document that looks fine on the author's machine and carries nothing on the
# reader's.

MAXOBJ = 8388607          # the PDF 1.4 limit on object numbers

# The `#2F` is an escaped slash: a PDF name cannot carry one literally.
MIME = {".tar": "application#2Fx-tar", ".html": "text#2Fhtml", ".txt": "text#2Fplain",
        ".p7m": "application#2Fpkcs7-mime", ".json": "application#2Fjson",
        ".pdf": "application#2Fpdf", ".zip": "application#2Fzip"}


def _balanced_dict(buf, start):
    """The extent of the << >> beginning at `start`, skipping literal strings.

    Written out rather than regexed because a regex cannot count, and the catalog is the
    one object here that has to be rewritten correctly or the file has no root."""
    assert buf[start:start + 2] == b"<<"
    i, depth = start + 2, 1
    while i < len(buf) and depth:
        c = buf[i:i + 1]
        if buf[i:i + 2] == b"<<":
            depth += 1; i += 2; continue
        if buf[i:i + 2] == b">>":
            depth -= 1; i += 2; continue
        if c == b"(":                       # a literal string may contain << or >>
            i += 1
            nest = 1
            while i < len(buf) and nest:
                if buf[i:i + 1] == b"\\":
                    i += 2; continue
                if buf[i:i + 1] == b"(":
                    nest += 1
                elif buf[i:i + 1] == b")":
                    nest -= 1
                i += 1
            continue
        i += 1
    if depth:
        raise SystemExit("! the catalog dictionary does not close — refusing to write "
                         "an incremental update over a file this script cannot read.")
    return i


def _pdf_string(s):
    return "(" + re.sub(r"([()\\])", r"\\\1", s) + ")"


# The file name is written as a literal string in /F, in /UF and as the key of the
# /EmbeddedFiles name tree. The specification prefers UTF-16BE for /UF; a literal string is
# a valid text string for an ASCII name and round-trips exactly, which is why the writer
# refuses a name that is not ASCII rather than mangling one.
#
# What was measured, and what it does not settle. Eight builds of the same document,
# differing one variable at a time — literal against UTF-16 names, with and without
# /Subtype, with and without /AF, a .zip name, an uncompressed stream — plus one written
# by poppler's own `pdfattach`, which never touched this code.
#
#     Firefox 154.0             downloads the attachment from every one of them
#     poppler 26.08.0           lists and extracts every one, byte-identical
#     Adobe Reader 2026.001.21789   shows the attachment and exports none of them,
#                               "Impossibile esportare … il file selezionato", after the
#                               click. macOS 25.5.
#
# Rendered by Chrome 151.0.7922.170; written and run on Python 3.9.6, the oldest version
# this project supports.
#
# Including the file poppler wrote. So this is not a property of what is written here, and
# no change to these objects has been shown to help; on that installation Acrobat does not
# export attachments at all. It is one machine and one installation, and it is left
# unexplained rather than guessed at. What follows from it is a documentation duty, not a
# code change: a reader on Acrobat may see the record and be unable to save it, and has to
# be told to use Firefox or `pdfdetach`. A route one reader cannot finish is a route that
# has to be declared.


def embed_bundle(pdf, attachments):
    """Return the PDF with each (path, description) embedded, as one incremental update.

    More than one, because the record and the tool that reads it are two things. A reader
    who saves both has the whole check in front of them; a reader who saves only the
    bundle finds the tool inside it, which works and reads like a riddle.
    """
    if isinstance(attachments, (str, bytes)):
        raise TypeError("embed_bundle takes a list of (path, description)")
    data = open(pdf, "rb").read()
    for path, _ in attachments:
        n = os.path.basename(path)
        if not n.isascii():
            raise SystemExit(f"! {n} is not an ASCII file name, and the literal-string "
                             f"form this writer\n  has to use for Adobe Reader cannot "
                             f"carry it safely. Rename it,\n  or give the case an ASCII "
                             f"case_uid.")

    for marker, why in ((b"/Encrypt", "it is encrypted"),
                        (b"/ObjStm", "it uses object streams"),
                        (b"/Type /XRef", "it uses a cross-reference stream"),
                        (b"/Type/XRef", "it uses a cross-reference stream")):
        if marker in data:
            raise SystemExit(f"! this PDF cannot be updated by this script: {why}.\n"
                             f"  Only the shape headless Chrome writes is implemented, "
                             f"and guessing at\n  the rest produces a file that opens "
                             f"in some readers and not others.")

    k = data.rfind(b"trailer")
    if k < 0:
        raise SystemExit("! no trailer: this is not a PDF with a classic xref table.")
    tstart = data.index(b"<<", k)
    trailer = data[tstart:_balanced_dict(data, tstart)]
    m_root = re.search(rb"/Root\s+(\d+)\s+0\s+R", trailer)
    m_size = re.search(rb"/Size\s+(\d+)", trailer)
    if not (m_root and m_size):
        raise SystemExit("! the trailer names no /Root or no /Size.")
    root, size = int(m_root.group(1)), int(m_size.group(1))

    m_sx = re.search(rb"startxref\s+(\d+)\s*%%EOF\s*$", data)
    if not m_sx:
        raise SystemExit("! no startxref at the end of the file.")
    prev = int(m_sx.group(1))

    m_cat = re.search(rb"(?m)^%d\s+0\s+obj\b" % root, data)
    if not m_cat:
        raise SystemExit(f"! object {root} (the catalog) is not a plain object in this "
                         f"file.")
    dstart = data.index(b"<<", m_cat.end())
    catalog = data[dstart:_balanced_dict(data, dstart)]
    for key in (b"/Names", b"/AF"):
        if key in catalog:
            raise SystemExit(f"! the catalog already carries {key.decode()}. Merging one "
                             f"in blindly would\n  break whatever is already there; this "
                             f"script refuses instead.")

    n_nm = size + 2 * len(attachments)          # the name tree comes after the pairs
    if n_nm > MAXOBJ:
        raise SystemExit("! too many objects in this PDF.")

    out = [data]
    if not data.endswith(b"\n"):
        out.append(b"\n")
    offsets = {}
    pos = sum(len(x) for x in out)

    def add(num, text, stream=None):
        nonlocal pos
        offsets[num] = pos
        chunk = f"{num} 0 obj\n{text}\n".encode("utf-8")
        if stream is not None:
            chunk += b"stream\n" + stream + b"\nendstream\n"
        chunk += b"endobj\n"
        out.append(chunk)
        pos += len(chunk)

    specs, names = [], []
    for i, (path, desc) in enumerate(attachments):
        payload = open(path, "rb").read()
        name = os.path.basename(path)
        n_ef, n_fs = size + 2 * i, size + 2 * i + 1
        body = zlib.compress(payload, 9)
        # /CheckSum is an MD5 by specification (PDF 32000-1, 7.11.4). It is a format
        # field, not a claim: what a reader checks a bundle against is the manifest in it.
        params = f"<< /Size {len(payload)} /CheckSum <{hashlib.md5(payload).hexdigest()}> >>"
        sub = MIME.get(os.path.splitext(name)[1].lower(), "application#2Foctet-stream")
        add(n_ef, f"<< /Type /EmbeddedFile /Subtype /{sub}"
                  f" /Filter /FlateDecode /Length {len(body)} /Params {params} >>", body)
        add(n_fs, f"<< /Type /Filespec /F {_pdf_string(name)} /UF {_pdf_string(name)}"
                  f" /EF << /F {n_ef} 0 R >> /AFRelationship /Supplement"
                  f" /Desc {_pdf_string(desc)} >>")
        specs.append(n_fs)
        names.append(f"{_pdf_string(name)} {n_fs} 0 R")
    # The name tree wants its keys sorted, and a reader that binary-searches it finds
    # nothing if they are not.
    add(n_nm, "<< /Names [ " + " ".join(sorted(names)) + " ] >>")
    add(root, (catalog[:-2].decode("latin-1")
               + f" /Names << /EmbeddedFiles {n_nm} 0 R >>"
               + " /AF [ " + " ".join(f"{n} 0 R" for n in specs) + " ] >>"))

    xref_at = pos
    rows = ["xref"]
    for first, count in _runs(sorted(offsets)):
        rows.append(f"{first} {count}")
        for n in range(first, first + count):
            rows.append(f"{offsets[n]:010d} 00000 n ")
    keep = re.sub(rb"/Prev\s+\d+", b"", trailer[2:-2]).decode("latin-1").strip()
    keep = re.sub(r"/Size\s+\d+", "", keep).strip()
    rows += ["trailer", f"<< /Size {n_nm + 1} {keep} /Prev {prev} >>",
             "startxref", str(xref_at), "%%EOF", ""]
    out.append("\n".join(rows).encode("latin-1"))
    return b"".join(out)


def _runs(nums):
    """Contiguous runs, because an xref subsection header is `first count`."""
    runs, start, last = [], None, None
    for n in nums:
        if start is None:
            start = last = n
        elif n == last + 1:
            last = n
        else:
            runs.append((start, last - start + 1)); start = last = n
    if start is not None:
        runs.append((start, last - start + 1))
    return runs


def find_chrome():
    """A path is checked as a path and a name is looked up on the PATH — each with the
    question it was written for. See the note on CHROME_PATHS."""
    for c in CHROME_PATHS:
        if os.path.isfile(c):
            return c
    for name in CHROME_NAMES:
        w = shutil.which(name)
        if w:
            return w
    return None


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    p.add_argument("--log", default="events.jsonl")
    p.add_argument("--kpi", default="kpi.json")
    p.add_argument("--icon", default="icon.svg")
    p.add_argument("--case", default="case.json")
    p.add_argument("--annotation", default="annotation.json")
    p.add_argument("--source", default=None)
    p.add_argument("--lang", choices=sorted(render_md.MARKER), default="en")
    p.add_argument("--gap", default=None)
    p.add_argument("--byline", default=None)
    p.add_argument("--no-byline", action="store_true")
    p.add_argument("--no-marker", action="store_true")
    p.add_argument("--attached", action="store_true",
                   help="the record is enclosed with this document, as a bundle")
    p.add_argument("--beside", action="store_true",
                   help="with --attached and no --embed: the bundle travels next to this "
                        "PDF rather than inside it, and you undertake to send both")
    p.add_argument("--bundle", default=None,
                   help="where that bundle is, if not beside the case")
    p.add_argument("--html-only", action="store_true", help="stop before Chrome")
    p.add_argument("--embed", nargs="*", default=None, metavar="FILE",
                   help="embed files in the PDF as an incremental update; with no "
                        "argument, the bundle --attached would name plus verify.html")
    p.add_argument("-o", "--out", default=None, help="the PDF path")
    a = p.parse_args(argv)

    # --attached writes the line; --embed puts the file in. They were independent, and a
    # PDF rendered with the first and not the second says `verify offline: drop
    # colophon-<uid>.tar on verify.html` while carrying nothing — to a reader who was
    # forwarded the document alone, a route that leads nowhere. It is the failure the
    # technical line exists to remove, wearing the costume of the fix, and it was silent.
    #
    # Not a hard rule, because `enclosed` means *travels with the document* and a PDF
    # mailed together with its tar is honestly described by it. That case now has to be
    # said out loud instead of being what you get by forgetting a flag.
    if a.attached and a.embed is None and not a.beside and not a.html_only:
        print("! --attached without --embed.\n"
              "  The disclosure would tell a reader to drop the bundle on verify.html,\n"
              "  and this PDF would not contain one. Two ways to be truthful:\n"
              "    --embed     put the bundle and the verifier inside the PDF\n"
              "    --beside    you are sending the tar alongside, in the same mail",
              file=sys.stderr)
        return 1
    # The mirror case under-claims rather than over-claims, so it is a warning: the
    # document carries the record and its own disclosure says it does not.
    if a.embed is not None and not a.attached:
        print("  ! --embed without --attached: the bundle goes into the PDF and the\n"
              "    technical line will say `not enclosed`. Add --attached.",
              file=sys.stderr)

    src, manifest, rows = render_md.gate(a.log, a.source)

    kpi = json.load(open(a.kpi, encoding="utf-8"))
    build_icon.refuse_if_ungated(kpi, a.kpi)
    try:
        case = json.load(open(a.case, encoding="utf-8"))
    except (OSError, ValueError):
        case = {}

    source = open(src, encoding="utf-8").read()
    refuse_unsupported(source)
    source, dropped = render_md.without_the_old_disclosure(source, a.annotation)
    body = to_html(source)
    check_nothing_was_rewritten(source, body)
    body = promote_title(body, case.get("title"))

    lines, name, xl, yi = build_block.note_lines(kpi, a.lang, a.gap)
    alt = build_block.T[a.lang]["alt"].format(name=name, x=f"{xl:.0f}", y=f"{yi:.0f}")
    tech = build_block.technical(a.log, a.lang, "html", False, a.attached,
                                 a.bundle)
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
    if dropped:
        print(f"  dropped   {len(dropped)} block(s) the annotation excludes — the "
              f"disclosure\n            the source carried by hand, which this "
              f"rendering generates")

    if a.html_only:
        return 0
    chrome = find_chrome()
    if not chrome:
        print("  ! no Chrome or Chromium found. The HTML above is complete: print it\n"
              "    yourself, or pass --html-only to stop here without this warning.",
              file=sys.stderr)
        return 1
    try:
        subprocess.run([chrome, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={os.path.abspath(out_pdf)}",
                        os.path.abspath(out_html)],
                       check=True, capture_output=True, timeout=CHROME_SECONDS)
    except subprocess.TimeoutExpired:
        # `run` kills the child on expiry, so the stalled Chrome does not outlive this.
        # The half-written PDF has to go with it: a truncated file sitting beside a
        # finished HTML is the one that gets picked up later and believed.
        partial = ""
        if os.path.exists(out_pdf):
            try:
                os.remove(out_pdf)
                partial = ("\n    A partly written %s was removed, so nothing "
                           "incomplete is left behind." % out_pdf)
            except OSError:
                partial = ("\n    ! %s may be partly written and could not be removed. "
                           "Delete it before using it." % out_pdf)
        print("  ! the rendering did not finish within %d seconds and was stopped.\n"
              "    Chrome does not always exit on its own. The HTML above is complete "
              "and\n    unaffected: print it yourself, or pass --html-only to stop "
              "there deliberately.%s" % (CHROME_SECONDS, partial), file=sys.stderr)
        return 1
    print(f"  {out_pdf}  {os.path.getsize(out_pdf):,} bytes")

    if a.embed is not None:
        base = os.path.dirname(os.path.abspath(a.log))
        if a.embed:
            files = [(f, os.path.basename(f)) for f in a.embed]
        else:
            tar = build_note.find_bundle(base, a.bundle, build_note.bundle_name(base))
            if not tar:
                print("! nothing to embed: run build_bundle.py first, or name the "
                      "files.", file=sys.stderr)
                return 1
            files = [(tar, "Colophon: the register, the seal and the measurement for "
                           "this document. Drop it on verify.html."),
                     (os.path.join(base, "verify.html"),
                      "The verifier. Open it in a browser with the network off and drop "
                      "the bundle on it.")]
        missing = [f for f, _ in files if not os.path.exists(f)]
        if missing:
            print(f"! not here: {', '.join(missing)}", file=sys.stderr)
            return 1
        before = open(out_pdf, "rb").read()
        merged = embed_bundle(out_pdf, files)
        if merged[:len(before)] != before:
            print("! the update rewrote existing bytes. Refusing to write it.",
                  file=sys.stderr)
            return 1
        with open(out_pdf, "wb") as f:
            f.write(merged)
        for f, _ in files:
            print(f"  embedded  {os.path.basename(f):<28} {os.path.getsize(f):>9,} bytes")
        print(f"  {out_pdf}  {len(merged):,} bytes")
        print("  the original bytes are untouched: this is an incremental update, so a\n"
              "  PAdES signature added AFTER this covers it. Signing first and embedding\n"
              "  after reads as tampering, not as breakage.")

    print("  not PDF/A-3, and do not call it that: no output intent, no conformant XMP.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

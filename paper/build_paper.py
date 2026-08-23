#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Fabio Chinaglia
"""
Render the method paper: colophon-method.md -> .html -> .pdf.

The PDF is what people read and the Markdown is what gets edited, so the two drift.
The first PDF in this repository was printed from an intermediate HTML that was never
committed, which left it impossible to re-render: this script is that missing step,
written down.

    python3 build_paper.py                 writes colophon-method.html
    python3 build_paper.py --pdf           and prints it through headless Chrome

Standard library only, like every other script here. It is not a general Markdown
implementation: it handles exactly what the paper uses — headings, paragraphs, tables,
lists, block quotes, fenced code, rules, images, and inline emphasis, code and links.
Anything else will come out as literal text, visibly, which is the failure mode to
prefer over silent mangling.

The HTML it writes is committed next to the paper. Keep it that way: it is what makes
the render reproducible by someone who is not you.
"""
import argparse
import html
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "colophon-method.md")
OUT_HTML = os.path.join(HERE, "colophon-method.html")
OUT_PDF = os.path.join(HERE, "colophon-method.pdf")

CHROMES = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome", "chromium", "chromium-browser",
)


# --- inline -----------------------------------------------------------------

def inline(text):
    """Emphasis, code, images and links, with the source escaped first."""
    slots = []

    def stash(markup):                      # keep generated markup out of later passes
        slots.append(markup)
        return f"\x00{len(slots) - 1}\x00"

    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", lambda m: stash(f"<code>{m.group(1)}</code>"), text)
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)",
                  lambda m: stash(f'<img src="{m.group(2)}" alt="{m.group(1)}">'), text)
    text = re.sub(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)",
                  lambda m: stash(f'<a href="{m.group(2)}">{m.group(1)}</a>'), text)
    def emphasise(t):
        return re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)",
                      lambda m: stash(f"<em>{m.group(1)}</em>"), t)

    # Bold runs first and non-greedily, because bold spans containing an italic are
    # common in this paper; its content goes through the italic pass before being
    # stashed, or the inner markers would survive into the output as literal stars.
    text = re.sub(r"\*\*(.+?)\*\*",
                  lambda m: stash(f"<strong>{emphasise(m.group(1))}</strong>"), text)
    text = emphasise(text)

    # Restore until nothing is left: a stashed span can contain another placeholder —
    # bold around an italic does exactly that — and a single pass would leave the inner
    # marker in the output as a bare number.
    while "\x00" in text:
        text = re.sub(r"\x00(\d+)\x00", lambda m: slots[int(m.group(1))], text)
    return text


# --- blocks -----------------------------------------------------------------

def is_table_sep(line):
    return bool(re.fullmatch(r"\|[\s:|-]+\|", line.strip()))


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def convert(md):
    out, lines, i = [], md.splitlines(), 0
    while i < len(lines):
        line = lines[i]

        if not line.strip():
            i += 1
            continue

        if line.startswith("```"):                                   # fenced code
            i += 1
            body = []
            while i < len(lines) and not lines[i].startswith("```"):
                body.append(html.escape(lines[i], quote=False))
                i += 1
            out.append("<pre><code>" + "\n".join(body) + "</code></pre>")
            i += 1
            continue

        if line.strip() == "---":                                    # rule
            out.append("<hr>")
            i += 1
            continue

        m = re.match(r"^(#{1,6}) (.*)$", line)                       # heading
        if m:
            level = len(m.group(1))
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            i += 1
            continue

        if line.startswith("|") and i + 1 < len(lines) and is_table_sep(lines[i + 1]):
            head = cells(line)
            i += 2
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append(cells(lines[i]))
                i += 1
            thead = "".join(f"<th>{inline(c)}</th>" for c in head)
            body = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
                           for r in rows)
            # A header row of empty cells is a layout table, not a labelled one.
            head_html = "" if not any(c.strip() for c in head) else f"<thead><tr>{thead}</tr></thead>"
            out.append(f"<table>{head_html}<tbody>{body}</tbody></table>")
            continue

        m = re.match(r"^([-*]|\d+\.) ", line)                        # list
        if m:
            tag = "ul" if m.group(1) in "-*" else "ol"
            items = []
            while i < len(lines) and re.match(r"^([-*]|\d+\.) ", lines[i]):
                items.append(re.sub(r"^([-*]|\d+\.) ", "", lines[i]))
                i += 1
                while i < len(lines) and lines[i].startswith("  ") and lines[i].strip():
                    items[-1] += " " + lines[i].strip()               # continuation
                    i += 1
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
            continue

        if line.startswith("> "):                                    # block quote
            body = []
            while i < len(lines) and lines[i].startswith("> "):
                body.append(lines[i][2:])
                i += 1
            out.append(f"<blockquote><p>{inline(' '.join(body))}</p></blockquote>")
            continue

        para = []                                                    # paragraph
        while i < len(lines) and lines[i].strip() and not re.match(
                r"^(#{1,6} |```|\||> |[-*] |\d+\. )", lines[i]) and lines[i].strip() != "---":
            para.append(lines[i].strip())
            i += 1
        out.append(f"<p>{inline(' '.join(para))}</p>")

    return "\n".join(out)


CSS = """
@page { size: A4; margin: 20mm 22mm 18mm; }
body { font-family: Georgia, "Liberation Serif", serif; font-size: 10pt;
       line-height: 1.5; color: #1a1a19; margin: 0; hyphens: auto; }
h1 { font-size: 19pt; line-height: 1.2; margin: 0 0 2mm; }
h2 { font-size: 12.5pt; margin: 9mm 0 2.5mm; page-break-after: avoid; }
h3 { font-size: 10.5pt; margin: 6mm 0 2mm; page-break-after: avoid; }
p  { margin: 0 0 3mm; text-align: justify; }
h1 + p { font-size: 11.5pt; font-style: italic; color: #3d3c39; text-align: left; }
hr { border: 0; border-top: .4pt solid #d8d7d3; margin: 6mm 0; }
ul, ol { margin: 0 0 3mm; padding-left: 6mm; }
li { margin-bottom: 1.5mm; text-align: justify; }
blockquote { margin: 0 0 3mm; padding-left: 5mm; border-left: 2pt solid #d8d7d3;
             font-style: italic; color: #3d3c39; }
blockquote p { margin: 0; }
code { font-family: ui-monospace, "DejaVu Sans Mono", monospace; font-size: 8.5pt; }
pre { background: #f4f3f0; padding: 3mm 4mm; font-size: 8pt; line-height: 1.45;
      overflow-x: auto; page-break-inside: avoid; margin: 0 0 4mm; }
pre code { font-size: 8pt; }
table { border-collapse: collapse; width: 100%; margin: 0 0 4mm; font-size: 9pt;
        page-break-inside: avoid; }
th, td { border-top: .4pt solid #d8d7d3; padding: 1.6mm 2.5mm; text-align: left;
         vertical-align: top; }
thead th { border-bottom: .8pt solid #a9a8a4; border-top: 0; font-size: 8.5pt;
           letter-spacing: .03em; }
tbody tr:last-child td { border-bottom: .4pt solid #d8d7d3; }
img { max-width: 42mm; height: auto; }
a { color: inherit; text-decoration: none; }
"""


def render(md):
    return ("<!DOCTYPE html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n"
            "<title>Colophon — a method for recording, measuring and declaring "
            "human and AI contribution in writing</title>\n<style>" + CSS +
            "</style></head><body>\n" + convert(md) + "\n</body></html>\n")


def find_chrome():
    for c in CHROMES:
        if os.path.exists(c):
            return c
        found = shutil.which(c)
        if found:
            return found
    return None


def main():
    p = argparse.ArgumentParser(description="Render the method paper.")
    p.add_argument("--pdf", action="store_true", help="also print the HTML to PDF")
    a = p.parse_args()

    md = open(SRC, encoding="utf-8").read()
    open(OUT_HTML, "w", encoding="utf-8").write(render(md))
    print(f"{os.path.relpath(OUT_HTML)} — {len(md.splitlines())} source lines")

    if not a.pdf:
        print("re-run with --pdf to print it, or open the HTML and print it yourself")
        return

    chrome = find_chrome()
    if not chrome:
        sys.exit("no Chrome or Chromium found: install one, or print the HTML by hand")
    subprocess.run([chrome, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={OUT_PDF}", OUT_HTML],
                   check=True, capture_output=True)
    print(f"{os.path.relpath(OUT_PDF)} — printed with {os.path.basename(chrome)}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Fabio Chinaglia
"""
Render the article for publication: versions/v22_final.txt -> post.html -> post.pdf.

The text comes from the measured version, verbatim — title, marker, body, and the
method note, which is a block of the article itself and is excluded from the count.
Nothing here rewrites it.

Everything under the rule goes with it: the icon on the left, the note beside it, and
the technical line below, in that order. The line is produced by build_note.py at render
time and never typed. The first rendering of this article typed it, and got a root that
had never been sealed — one event short on the day it was made. That is what this script
exists to prevent.

    python3 render_post.py             writes post.html
    python3 render_post.py --pdf       and prints it through headless Chrome

post.html and post.pdf are renderings and are listed in no manifest: they can be made
again from the artefacts the manifest does cover, and freezing them would mean reopening
a sealed case every time a rendering has to change.
"""
import argparse
import html
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "versions", "v22_final.txt")

# The publication date, which is editorial and not something the register measures: the
# register holds the writing dates, this is the day it goes out.
BYLINE_DATE = "22 agosto 2026"

CHROMES = ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
           "/Applications/Chromium.app/Contents/MacOS/Chromium",
           "google-chrome", "chromium", "chromium-browser")

CSS = """@page { size:A4; margin:24mm 24mm 18mm 24mm; }
body { font-family:Georgia,'Times New Roman',serif; color:#16171a; font-size:11pt;
  line-height:1.6; }
h1 { font-size:17.5pt; line-height:1.28; margin:0 0 2.5mm 0; font-weight:normal;
  letter-spacing:-.2px; }
.byline { font-family:Helvetica,Arial,sans-serif; font-size:8pt; color:#7a7975;
  letter-spacing:.11em; text-transform:uppercase; margin:0 0 8mm 0; }
.marker { font-style:italic; color:#55565a; font-size:9.5pt; line-height:1.5;
  border-left:2px solid #2a78d6; padding-left:4mm; margin:0 0 8mm 0; }
p.b { margin:0 0 4mm 0; text-align:justify; }
hr { border:0; border-top:1px solid #dcdcd8; margin:9mm 0 6.5mm 0; }
table.foot { width:100%; border-collapse:collapse; }
table.foot td { vertical-align:top; padding:0; }
td.ico { width:56mm; padding-right:8mm; }
td.ico img { width:54mm; }
.nota { font-style:italic; font-size:9pt; line-height:1.54; color:#33343a;
  text-align:justify; }
.chain { font-family:'DejaVu Sans Mono',monospace; font-size:7pt; color:#7a7975;
  margin-top:3.5mm; line-height:1.5; overflow-wrap:anywhere; }
"""


def esc(s):
    return html.escape(s, quote=False).replace("\n", " ")


def technical_line():
    """From build_note.py, at render time. Never typed: see the module docstring."""
    out = subprocess.run([sys.executable, "build_note.py", "--lang", "it"], cwd=HERE,
                         capture_output=True, text=True, check=True)
    return out.stdout.strip()


def icon_summary(kpi):
    """The three facts the icon states, in words, from the file that produced it."""
    words, ideas = 100 - kpi["ai_lexical"], 100 - kpi["ai_ideational"]
    name = ("human written" if words >= 50 and ideas >= 50 else
            "machine polished" if ideas >= 50 else
            "human edited" if words >= 50 else "machine generated")
    margin = min(abs(words - 50), abs(ideas - 50))
    line = (f"{name} · parole umane {words:.1f}% · idee umane {ideas:.0f}% · "
            f"{kpi['spans']} span · {kpi['words']} parole")
    if margin < 5:
        line += (f"<br>margine {margin:.1f} punti dal confine — leggere il punto, "
                 f"non la sola etichetta").replace(".", ",", 1)
    return line


def build():
    blocks = [b.strip() for b in open(SRC, encoding="utf-8").read().split("\n\n")
              if b.strip()]
    kpi = json.load(open(os.path.join(HERE, "kpi.json"), encoding="utf-8"))
    case = json.load(open(os.path.join(HERE, "case.json"), encoding="utf-8"))
    title, marker, body, note = blocks[0], blocks[1], blocks[2:-1], blocks[-1]

    paragraphs = "\n".join(f'<p class="b">{esc(p)}</p>' for p in body)
    return f"""<!DOCTYPE html>
<html lang="it"><head><meta charset="utf-8">
<title>{esc(title)}</title>
<style>{CSS}</style></head><body>
<h1>{esc(title)}</h1>
<div class="byline">{esc(case['author'])} &middot; {BYLINE_DATE}</div>
<div class="marker">{esc(marker)}</div>
{paragraphs}
<hr>
<table class="foot"><tr>
<td class="ico"><img src="icon.svg" alt="Quadrante di provenienza"></td>
<td>
<div class="nota">{esc(note)}</div>
<div class="chain">{icon_summary(kpi)}<br>{esc(technical_line())}</div>
</td>
</tr></table>
</body></html>
"""


def main():
    p = argparse.ArgumentParser(description="Render the article for publication.")
    p.add_argument("--pdf", action="store_true", help="also print the HTML to PDF")
    a = p.parse_args()

    out_html = os.path.join(HERE, "post.html")
    open(out_html, "w", encoding="utf-8").write(build())
    print("post.html")
    if not a.pdf:
        return

    chrome = next((c for c in CHROMES if os.path.exists(c) or shutil.which(c)), None)
    if not chrome:
        sys.exit("no Chrome or Chromium found: print post.html by hand")
    chrome = chrome if os.path.exists(chrome) else shutil.which(chrome)
    subprocess.run([chrome, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={os.path.join(HERE, 'post.pdf')}", out_html],
                   check=True, capture_output=True)
    print("post.pdf")


if __name__ == "__main__":
    main()

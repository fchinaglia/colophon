#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Fabio Chinaglia
"""Rende l'articolo con le figure: markdown -> HTML -> PDF (Chromium)."""
import asyncio
import sys

import markdown
from playwright.async_api import async_playwright

src = sys.argv[1] if len(sys.argv) > 1 else "articolo_frammentazione_dati_illustrato.md"
out_html = src.replace(".md", ".html")
out_pdf = src.replace(".md", ".pdf")

corpo = markdown.markdown(open(src, encoding="utf-8").read(),
                          extensions=["tables", "sane_lists", "md_in_html"])

CSS = """
@page { size: A4; margin: 24mm 22mm 22mm 22mm; }
body { font: 11pt/1.62 "Charter","Georgia","Times New Roman",serif; color:#16171a;
       margin:0; hyphens:auto; text-align:justify; }
h1 { font-size:20pt; line-height:1.2; margin:0 0 10pt; font-weight:700;
     text-align:left; hyphens:none; letter-spacing:-.01em; }
h1 + p em { color:#5a5c62; font-size:9.5pt; }
h1 + p { text-align:left; margin:0 0 20pt; padding-bottom:12pt;
         border-bottom:.5pt solid #d5d7dc; }
h2 { font-size:12.5pt; margin:20pt 0 7pt; font-weight:700; text-align:left;
     hyphens:none; break-after:avoid; }
p { margin:0 0 8pt; }
hr { border:0; border-top:.5pt solid #d5d7dc; margin:18pt 0 12pt; }
ul { margin:0 0 9pt; padding-left:16pt; } li { margin-bottom:3pt; }
strong { font-weight:700; } em { font-style:italic; }
p:last-of-type em { color:#3a3c42; font-size:9.5pt; line-height:1.5; }
.nota-prov { display:flex; gap:14pt; align-items:flex-start; margin-top:10pt;
             padding-top:10pt; border-top:.5pt solid #d5d7dc; break-inside:avoid; }
.nota-prov img { width:34mm; height:auto; flex:0 0 auto; }
.nota-prov p { margin:0; text-align:justify; }
.nota-col { flex:1 1 auto; min-width:0; }
.tecnica { margin:7pt 0 0; font-size:8pt; line-height:1.45; color:#7a7c82;
           font-style:normal; text-align:left; hyphens:none; }
.tecnica code { font-family:"SF Mono",Menlo,Consolas,monospace; font-size:7.6pt; }


figure { margin:16pt 0 18pt; break-inside:avoid; page-break-inside:avoid;
         text-align:center; }
figure img { width:100%; height:auto; display:block; }
figcaption { font: italic 9pt/1.45 "Charter","Georgia",serif; color:#5a5c62;
             text-align:left; margin-top:5pt; padding-top:4pt;
             border-top:.5pt solid #e2e2dd; hyphens:none; }
"""

# l'ultimo paragrafo e la nota sul metodo: le si affianca l'icona del quadrante
i = corpo.rfind("<p>")
if i >= 0 and "Nota sul metodo" in corpo[i:]:
    coda = corpo[i:]
    corpo = (corpo[:i] + '<div class="nota-prov">'
             '<img src="immagini/icona.svg" alt="Provenienza: human written">'
             '<div class="nota-col">'
             + coda.replace("</p>", "</p></div></div>", 1))

# riga tecnica: generata dal registro (cfr. build_note.py nella skill), mai scritta a mano
import json as _json, os as _os
_log = "../caso001/eventi.jsonl"
if _os.path.exists(_log):
    _ev = [_json.loads(r) for r in open(_log, encoding="utf-8") if r.strip()]
    _r = _ev[-1]["hash"]
    _s = "" if _os.path.exists(_log + ".sig") else " Il registro non \u00e8 ancora sigillato."
    _tec = ('<p class="tecnica">Registro: %d eventi, radice <code>%s\u2026%s</code>. '
            'Firma Ed25519 e marca temporale accanto al registro; istruzioni di '
            'verifica in <code>VERIFY.md</code>.%s</p>') % (len(_ev), _r[:8], _r[-8:], _s)
    corpo = corpo.replace("</p></div></div>", "</p>" + _tec + "</div></div>", 1)

open(out_html, "w", encoding="utf-8").write(
    f'<!DOCTYPE html><html lang="it"><head><meta charset="utf-8">'
    f'<style>{CSS}</style></head><body>{corpo}</body></html>')


async def pdf():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        pg = await b.new_page()
        await pg.goto("file://" + __import__("os").path.abspath(out_html))
        await pg.wait_for_timeout(900)
        await pg.pdf(path=out_pdf, format="A4", print_background=True,
                     display_header_footer=True, header_template="<div></div>",
                     footer_template='<div style="width:100%;text-align:center;'
                                     'font:8pt Georgia,serif;color:#8a8983;">'
                                     '<span class="pageNumber"></span></div>',
                     margin={"top": "24mm", "bottom": "18mm",
                             "left": "22mm", "right": "22mm"})
        await b.close()

asyncio.run(pdf())
print(out_html, out_pdf)

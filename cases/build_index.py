#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Fabio Chinaglia
"""
The door of a published case: cases/NNN/index.html.

A case folder holds a register, an annotation and a verification page. None of those is
a landing place: the verification page opens on span colours and percentages, which is
the wrong first screen for a reader who arrived from one line at the foot of an article.
This writes the screen before it — what the case is, the two numbers, and where to go.

It also fixes the address. A published URL must survive being clicked, and a link
detector cuts at the first underscore: .../cases/002/pagina_di_verifica.html reaches the
reader as .../cases/002/pagina, a 404. Served as index.html, the address ends at the
folder and there is nothing to truncate.

    python3 build_index.py 001 002        from the cases directory

Reads each case's own metadata, in whichever schema that case used — the numbers are
never typed here. Writes index.html into the case folder. That file is listed in no
manifest, so writing it moves no digest and breaks no signature: the measured artefacts
keep the names their seal covers.

Italian, because the audience is the readers of the two Italian articles these cases
document. The repository around them stays English.
"""
import html
import json
import os
import sys

# Each case names its files in the language it was made in.
SCHEMAS = [
    dict(kpi="kpi.json", case="case.json", log="events.jsonl", page="verification.html",
         icon="icon.svg", lex="ai_lexical", idea="ai_ideational",
         title="title", author="author", date="date"),
    dict(kpi="misura_kpi.json", case="caso.json", log="eventi.jsonl",
         page="pagina_di_verifica.html", icon="icona.svg",
         lex="ai_lessicale", idea="ai_ideativa",
         title="titolo", author="autore", date="data"),
]

REPO = "https://github.com/fchinaglia/colophon/tree/main/cases"

CSS = """
:root { color-scheme: light dark; }
* { box-sizing: border-box; }
body { font-family: Georgia, "Liberation Serif", serif; background: #fcfcfb;
       color: #1a1a19; margin: 0; padding: 7vh 1.5rem 4rem; line-height: 1.6; }
main { max-width: 40rem; margin: 0 auto; }
.kicker { font-family: ui-monospace, monospace; font-size: .72rem; letter-spacing: .1em;
          text-transform: uppercase; color: #2a78d6; margin: 0 0 .9rem; }
h1 { font-size: 1.5rem; line-height: 1.28; font-weight: 600; margin: 0 0 .9rem; }
.lede { font-size: 1rem; color: #3d3c39; margin: 0 0 2rem; }
.block { display: flex; gap: 1.8rem; align-items: flex-start; margin: 0 0 2rem;
         flex-wrap: wrap; }
.block img { width: 12rem; flex: none; }
.figs { flex: 1 1 14rem; margin: 0; }
.figs div { margin-bottom: .9rem; }
.n { font-size: 1.6rem; font-weight: 600; line-height: 1; }
.k { font-size: .85rem; color: #7a7975; }
.links { margin: 0 0 2rem; padding: 0; list-style: none; }
.links li { margin-bottom: .55rem; }
.links a { color: #2a78d6; text-decoration: none; border-bottom: 1px solid #cfe0f6; }
.links a:hover { border-bottom-color: #2a78d6; }
.links .what { color: #7a7975; font-size: .85rem; }
.note { font-size: .85rem; color: #7a7975; border-top: 1px solid #e5e4e0;
        padding-top: 1.2rem; }
.note strong { color: #1a1a19; }
code { font-family: ui-monospace, monospace; font-size: .8rem; word-break: break-all; }
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) body { background: #1a1a19; color: #f2f1ee; }
  :root:not([data-theme="light"]) .lede { color: #c9c7c1; }
  :root:not([data-theme="light"]) h1, :root:not([data-theme="light"]) .note strong
    { color: #f2f1ee; }
  :root:not([data-theme="light"]) .note { border-top-color: #33322f; }
}
"""


def load(case_dir):
    for s in SCHEMAS:
        if os.path.exists(os.path.join(case_dir, s["kpi"])):
            kpi = json.load(open(os.path.join(case_dir, s["kpi"]), encoding="utf-8"))
            meta = json.load(open(os.path.join(case_dir, s["case"]), encoding="utf-8"))
            last = [r for r in open(os.path.join(case_dir, s["log"]),
                                    encoding="utf-8") if r.strip()][-1]
            return s, kpi, meta, json.loads(last)["hash"], len(
                [r for r in open(os.path.join(case_dir, s["log"]),
                                 encoding="utf-8") if r.strip()])
    sys.exit(f"{case_dir}: no measurement file in any known schema")


def page(num, s, kpi, meta, root, events, caveat=""):
    words = 100 - kpi[s["lex"]]
    ideas = 100 - kpi[s["idea"]]
    return f"""<!DOCTYPE html>
<html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Caso {num} — come è stato scritto {html.escape(meta[s['title']])}</title>
<style>{CSS}</style></head><body><main>

<p class="kicker">Registro di provenienza · caso {num}</p>
<h1>{html.escape(meta[s['title']])}</h1>
<p class="lede">Di {html.escape(meta[s['author']])}, {html.escape(str(meta[s['date']]))}.
Ogni intervento fatto scrivendo questo testo — mio e del modello linguistico — è stato
registrato mentre accadeva, e poi misurato su due assi indipendenti.</p>

<div class="block">
  <img src="{s['icon']}" alt="Quadrante di provenienza del caso {num}">
  <div class="figs">
    <div><div class="n">{words:.0f}%</div>
         <div class="k">delle parole sono mie, {kpi[s['lex']]:.0f}% dell'AI</div></div>
    <div><div class="n">{ideas:.0f}%</div>
         <div class="k">del contenuto è mio, {kpi[s['idea']]:.0f}% dell'AI</div></div>
  </div>
</div>

<ul class="links">
  <li><a href="{s['page']}">Pagina di verifica</a>
      <span class="what">— il testo passaggio per passaggio, i numeri per fase, e cosa
      il metodo non dimostra</span></li>
  <li><a href="{REPO}/{num}">Registro e tutti i file</a>
      <span class="what">— {events} eventi concatenati, firma, marca temporale,
      ancoraggio, e le istruzioni per verificarli</span></li>
</ul>

{caveat}
<p class="note"><strong>Radice della catena</strong> <code>{root}</code><br>
La catena dimostra che nessun evento è stato alterato dopo essere stato registrato.
Non dimostra che il registro sia <em>completo</em>: nessun sistema volontario può
farlo, e il registro è compilato dal modello sul proprio contributo. Il valore di
questo registro non sta nella prova: sta nella responsabilità che mi assumo
pubblicandolo, e nel fatto che è ispezionabile.</p>

</main></body></html>
"""


CAVEATS = {
    "001": """<p class="note"><strong>Questo caso è stato riaperto due volte il 23 agosto 2026</strong>,
dopo che il suo manifesto lo aveva dichiarato definitivo. La pagina di verifica aveva un
difetto di resa — la nota finale spezzata in un paragrafo per carattere, per un bug nello
script che l'ha generata — e il registro nominava sedici modifiche che nessuno span
portava, senza dire perché. Entrambe le cose sono state corrette, e la riapertura è
registrata: un evento che la annuncia prima di toccare qualsiasi file, un manifesto nuovo,
una firma nuova, e il sigillo del 22 agosto conservato accanto. La seconda riapertura ha
rifatto il documento pubblicato, che portava una radice battuta a mano e mai sigillata, e
ha tolto le rese dall'elenco firmato: una resa si rigenera da ciò che è firmato, e
congelarla obbligava a riaprire il caso ogni volta. I numeri non sono cambiati.</p>
"""
}


def main():
    nums = sys.argv[1:] or ["001", "002"]
    here = os.path.dirname(os.path.abspath(__file__))
    for num in nums:
        d = os.path.join(here, num)
        if not os.path.isdir(d):
            sys.exit(f"missing {d}")
        s, kpi, meta, root, events = load(d)
        out = os.path.join(d, "index.html")
        open(out, "w", encoding="utf-8").write(
            page(num, s, kpi, meta, root, events, CAVEATS.get(num, "")))
        print(f"cases/{num}/index.html — {100-kpi[s['lex']]:.0f}% parole mie, "
              f"{100-kpi[s['idea']]:.0f}% idee mie, {events} eventi")


if __name__ == "__main__":
    main()

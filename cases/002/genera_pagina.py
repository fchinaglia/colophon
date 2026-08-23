#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Fabio Chinaglia
"""
Genera la pagina di verifica a partire dagli span annotati.

Legge misura_span.json, misura_kpi.json, eventi.jsonl e caso.json.
Scrive pagina_di_verifica.html: documento autonomo, nessuna dipendenza esterna.

caso.json:
  {"titolo": "...", "autore": "...", "data": "19 agosto 2026",
   "ricostruito": false, "note_extra": ["..."]}

Palette validata: blu #2a78d6 / grigio #7a7975 / rosso #e34948 su superficie
chiara #fcfcfb e scura #1a1a19. Separazione CVD (protanopia) ΔE 21.6 chiaro /
19.2 scuro; contrasto del testo sulle tinte di sfondo sempre sopra 11:1.
Codifica ridondante: sfondo + sottolineatura + etichetta accessibile.
"""
import html
import json
import os
import re

spans = json.load(open("misura_span.json", encoding="utf-8"))
kpi = json.load(open("misura_kpi.json", encoding="utf-8"))
caso = json.load(open("caso.json", encoding="utf-8")) if os.path.exists("caso.json") else {}
eventi = [json.loads(r) for r in open("eventi.jsonl", encoding="utf-8") if r.strip()] \
    if os.path.exists("eventi.jsonl") else []

radice = eventi[-1]["hash"] if eventi else "—"
n_dec = sum(1 for e in eventi if e.get("tipo") == "decisione_editoriale")
tot = kpi["parole"]

ETICHETTA = {"ricerca": "ricerca e documentazione", "struttura": "struttura",
             "prima_stesura": "prima stesura",
             "revisione_contenuto": "revisione di contenuto",
             "revisione_forma": "revisione di forma", "titolazione": "titolazione"}
ORIG = [("U", "umano"), ("UA", "misto"), ("A", "AI")]


def pct(x):
    return f"{x:.1f}".replace(".", ",")


def quota(chiave, sel=None):
    ss = [s for s in spans if sel is None or sel(s)]
    t = sum(s["parole"] for s in ss) or 1
    return {k: 100 * sum(s["parole"] for s in ss if s[chiave] == k) / t for k, _ in ORIG}, t


barre = []
for fk, dati in kpi["per_fase"].items():
    q, t = quota("lex", lambda s, f=fk: s["fase"] == f)
    seg = "".join(
        f'<div class="seg s-{k}" style="flex:{q[k]:.5f}" '
        f'data-tip="{ETICHETTA.get(fk, fk)} · {lbl}: {pct(q[k])}% '
        f'({round(q[k]*t/100)} parole)"></div>'
        for k, lbl in ORIG if q[k] > 0)
    barre.append(f'<div class="riga"><div class="etichetta">{ETICHETTA.get(fk, fk)}</div>'
                 f'<div class="barra">{seg}</div>'
                 f'<div class="valore">{pct(dati["ai"])}%</div>'
                 f'<div class="parole">{t}</div></div>')

blocchi, cur = [], None
for s in spans:
    if cur is None or s["blocco"] != cur[0]:
        cur = (s["blocco"], [])
        blocchi.append(cur)
    cur[1].append(s)


def inline(t):
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html.escape(t))


def marca(s, testo):
    tip = ETICHETTA.get(s["fase"], s["fase"])
    if s["evento"]:
        tip += f' · modifica {s["evento"]}'
    if s["nota"]:
        tip += f' — {s["nota"]}'
    lab = {"U": "umano", "A": "AI", "UA": "misto"}[s["lex"]]
    return (f'<span class="pv" data-lex="{s["lex"]}" data-idea="{s["idea"]}" '
            f'data-tip="{html.escape(tip)}" tabindex="0" '
            f'aria-label="origine {lab}">{inline(testo)}</span>')


out = []
for bi, ss in blocchi:
    t0 = ss[0]["testo"]
    if ss[0]["heading"]:
        liv = 1 if t0.startswith("# ") else 2
        titolo = re.sub(r"^#+\s*", "", t0)
        out.append(f'<h{liv}>{marca(ss[0], titolo)}</h{liv}>')
    elif t0.lstrip().startswith("-"):
        li = [f'<li>{marca(s, r.strip()[1:].strip())}</li>'
              for s in ss for r in s["testo"].split("\n") if r.strip().startswith("-")]
        out.append("<ul>" + "".join(li) + "</ul>")
    else:
        out.append("<p>" + " ".join(marca(s, s["testo"]) for s in ss) + "</p>")
articolo = "\n".join(out)

righe_tab = []
for fk, dati in kpi["per_fase"].items():
    q, t = quota("lex", lambda s, f=fk: s["fase"] == f)
    qi, _ = quota("idea", lambda s, f=fk: s["fase"] == f)
    righe_tab.append(f"<tr><td>{ETICHETTA.get(fk, fk)}</td><td class='n'>{t}</td>"
                     f"<td class='n'>{pct(q['U'])}</td><td class='n'>{pct(q['UA'])}</td>"
                     f"<td class='n'>{pct(q['A'])}</td>"
                     f"<td class='n'>{pct(qi['A'] + qi['UA']/2)}</td></tr>")

ai_lex, ai_idea = kpi["ai_lessicale"], kpi["ai_ideativa"]
ricostruito = caso.get("ricostruito", False)
avviso = ("<p class=\"nota\" style=\"border-left-color:var(--ai)\">Attenzione: questo "
          "registro è stato compilato <strong>dopo</strong> la stesura. Le percentuali "
          "sono una ricostruzione, non una misura del processo: vanno lette come ordini "
          "di grandezza dichiarati in buona fede.</p>") if ricostruito else ""
extra = "".join(f"<p>{html.escape(n)}</p>" for n in caso.get("note_extra", []))

HTML = f"""<!DOCTYPE html>
<html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Come è stato scritto — registro di provenienza</title>
<style>
:root {{ color-scheme:light;
  --surface-1:#fcfcfb; --surface-2:#f4f3f0; --line:#e2e0da;
  --text-primary:#0b0b0b; --text-secondary:#52514e; --text-muted:#7a7975;
  --umano:#2a78d6; --misto:#7a7975; --ai:#e34948;
  --bg-misto:#eaeae8; --bg-ai:#f8dfde; }}
@media (prefers-color-scheme:dark) {{ :root:where(:not([data-theme="light"])) {{
  color-scheme:dark;
  --surface-1:#1a1a19; --surface-2:#232322; --line:#3a3a37;
  --text-primary:#fff; --text-secondary:#c3c2b7; --text-muted:#8a8983;
  --umano:#3987e5; --misto:#8a8983; --ai:#e66767;
  --bg-misto:#333230; --bg-ai:#573130; }} }}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--surface-1);color:var(--text-primary);
 font:16px/1.65 ui-sans-serif,-apple-system,"Segoe UI",Roboto,sans-serif}}
.wrap{{max-width:780px;margin:0 auto;padding:40px 24px 96px}}
header.top{{border-bottom:1px solid var(--line);padding-bottom:24px;margin-bottom:32px}}
.kicker{{font-size:12px;letter-spacing:.08em;text-transform:uppercase;
 color:var(--text-muted);margin:0 0 8px}}
h1.page{{font-size:26px;line-height:1.25;margin:0 0 10px;font-weight:650}}
.sub{{color:var(--text-secondary);margin:0;font-size:15px}}
.meta{{display:flex;flex-wrap:wrap;gap:6px 20px;margin-top:18px;font-size:12.5px;
 color:var(--text-muted);font-variant-numeric:tabular-nums}}
.meta code{{font-size:12px;color:var(--text-secondary)}}
.tiles{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:0 0 12px}}
.tile{{background:var(--surface-2);border:1px solid var(--line);border-radius:10px;
 padding:18px 20px}}
.tile .n{{font-size:40px;font-weight:640;line-height:1;
 font-variant-numeric:tabular-nums;letter-spacing:-.02em}}
.tile .k{{font-size:13px;color:var(--text-secondary);margin-top:8px}}
.tile .d{{font-size:12.5px;color:var(--text-muted);margin-top:6px;line-height:1.45}}
.nota{{font-size:13.5px;color:var(--text-secondary);background:var(--surface-2);
 border-left:2px solid var(--line);padding:12px 16px;border-radius:0 8px 8px 0;margin:0 0 24px}}
h2.sez{{font-size:13px;letter-spacing:.06em;text-transform:uppercase;
 color:var(--text-muted);margin:44px 0 16px;font-weight:600}}
.riga{{display:grid;grid-template-columns:160px 1fr 52px 46px;align-items:center;
 gap:12px;margin-bottom:9px}}
.etichetta{{font-size:13px;color:var(--text-secondary)}}
.barra{{display:flex;gap:2px;height:20px}}
.seg{{min-width:2px}} .seg:first-child{{border-radius:4px 0 0 4px}}
.seg:last-child{{border-radius:0 4px 4px 0}} .seg:only-child{{border-radius:4px}}
.s-U{{background:var(--umano)}} .s-UA{{background:var(--misto)}} .s-A{{background:var(--ai)}}
.valore{{font-size:13px;text-align:right;font-variant-numeric:tabular-nums}}
.parole{{font-size:12px;color:var(--text-muted);text-align:right;
 font-variant-numeric:tabular-nums}}
.legenda{{display:flex;flex-wrap:wrap;gap:18px;margin:16px 0 0;font-size:13px;
 color:var(--text-secondary)}}
.chip{{display:inline-flex;align-items:center;gap:7px}}
.sw{{width:12px;height:12px;border-radius:3px;display:inline-block}}
.ctrl{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:0 0 20px;font-size:13px}}
button{{font:inherit;font-size:13px;padding:7px 13px;border-radius:7px;
 border:1px solid var(--line);background:var(--surface-2);color:var(--text-primary);
 cursor:pointer}}
button[aria-pressed="true"]{{background:var(--text-primary);color:var(--surface-1);
 border-color:var(--text-primary)}}
article h1{{font-size:23px;line-height:1.3;margin:0 0 24px;font-weight:650}}
article h2{{font-size:17px;line-height:1.35;margin:36px 0 14px;font-weight:620}}
article p{{margin:0 0 16px}} article ul{{margin:0 0 16px;padding-left:22px}}
article li{{margin-bottom:5px}}
.pv{{border-radius:2px;padding:.06em 0;box-decoration-break:clone;
 -webkit-box-decoration-break:clone}}
body[data-vista="lex"] .pv[data-lex="U"],
body[data-vista="idea"] .pv[data-idea="U"]{{background:transparent}}
body[data-vista="lex"] .pv[data-lex="UA"],
body[data-vista="idea"] .pv[data-idea="UA"]{{background:var(--bg-misto);
 text-decoration:underline dotted var(--misto) 2px;text-underline-offset:.2em}}
body[data-vista="lex"] .pv[data-lex="A"],
body[data-vista="idea"] .pv[data-idea="A"]{{background:var(--bg-ai);
 text-decoration:underline solid var(--ai) 2px;text-underline-offset:.2em}}
body[data-evid="off"] .pv{{background:transparent!important;text-decoration:none!important}}
.pv:focus-visible{{outline:2px solid var(--text-primary);outline-offset:1px}}
table{{width:100%;border-collapse:collapse;font-size:13.5px;
 font-variant-numeric:tabular-nums}}
th,td{{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line)}}
th{{font-weight:600;color:var(--text-secondary);font-size:12.5px}}
td.n,th.n{{text-align:right}}
details{{margin-top:12px;font-size:14px;color:var(--text-secondary)}}
summary{{cursor:pointer;color:var(--text-primary);font-size:13.5px}}
details p{{margin:12px 0}}
#tip{{position:fixed;z-index:9;max-width:330px;padding:8px 11px;font-size:12.5px;
 line-height:1.45;background:var(--text-primary);color:var(--surface-1);
 border-radius:7px;pointer-events:none;opacity:0;transition:opacity .1s}}
@media (max-width:620px){{ .tiles{{grid-template-columns:1fr}}
 .riga{{grid-template-columns:110px 1fr 48px}} .parole{{display:none}} }}
</style></head>
<body data-vista="lex" data-evid="on"><div class="wrap">

<header class="top">
<p class="kicker">Registro di provenienza</p>
<h1 class="page">Come è stato scritto <em>{html.escape(caso.get('titolo','—'))}</em></h1>
<p class="sub">Questo testo è stato scritto da una persona con l'assistenza di un
modello linguistico. Ogni intervento è stato registrato mentre accadeva. Qui sotto
c'è tutto: quanto, dove, e di chi è cosa.</p>
<div class="meta">
<span>{html.escape(caso.get('autore','—'))}</span>
<span>{html.escape(caso.get('data','—'))}</span>
<span>{tot} parole · {len(spans)} span</span>
<span>{len(eventi)} eventi · {n_dec} decisioni editoriali</span>
<span>radice della catena <code>{radice[:16]}…</code></span>
</div></header>

{avviso}
<div class="tiles">
<div class="tile"><div class="n">{pct(ai_lex)}%</div>
<div class="k">delle parole sono state scritte dall'AI</div>
<div class="d">Le parole che si leggono nel testo finale. Include le riformulazioni
di frasi il cui contenuto è dell'autore.</div></div>
<div class="tile"><div class="n">{pct(ai_idea)}%</div>
<div class="k">del contenuto proviene dall'AI</div>
<div class="d">Le idee che quelle parole esprimono, indipendentemente da chi le ha
messe in frase.</div></div>
</div>
<p class="nota">I due numeri differiscono di {pct(abs(ai_lex-ai_idea))} punti, e la
differenza è la cosa più informativa della pagina. Il misto è contato per metà.</p>

<h2 class="sez">Dove è intervenuta l'AI</h2>
{''.join(barre)}
<div class="legenda">
<span class="chip"><i class="sw" style="background:var(--umano)"></i>umano</span>
<span class="chip"><i class="sw" style="background:var(--misto)"></i>misto</span>
<span class="chip"><i class="sw" style="background:var(--ai)"></i>AI</span>
<span style="color:var(--text-muted)">la percentuale a destra è la quota AI</span>
</div>

<h2 class="sez">Il testo, span per span</h2>
<div class="ctrl">
<button id="b-lex" aria-pressed="true">parole</button>
<button id="b-idea" aria-pressed="false">idee</button>
<button id="b-off" aria-pressed="false">nessuna evidenziazione</button>
<span style="color:var(--text-muted)">passa sopra un passaggio per vedere fase e
intervento</span></div>
<article>{articolo}</article>

<p class="nota" style="margin-top:32px">Il testo non evidenziato è dell'autore.
L'evidenziazione non è una stima statistica: è la registrazione di quello che è
successo mentre il testo veniva scritto. Non dice nulla sulla qualità di ciò che è
evidenziato, né implica che l'autore non risponda di ogni parola: la responsabilità
editoriale del testo è interamente sua.</p>

<h2 class="sez">Tabella</h2>
<table><thead><tr><th>fase</th><th class="n">parole</th><th class="n">umano %</th>
<th class="n">misto %</th><th class="n">AI %</th><th class="n">AI ideativa %</th>
</tr></thead><tbody>{''.join(righe_tab)}</tbody></table>

<details><summary>Metodo, e cosa questa pagina non prova</summary>
<p><strong>Come è stata prodotta.</strong> Ogni richiesta dell'autore e ogni output
del modello sono stati registrati in un log append-only con catena di hash: ciascun
evento è legato al precedente, quindi modificare un evento passato invalida tutti gli
hash successivi. Le decisioni editoriali sono registrate una per una. L'attribuzione
degli span è stata compilata sulla base di quel registro, e la concatenazione degli
span riproduce esattamente il testo pubblicato.</p>
<p><strong>Cosa non prova.</strong> La catena dimostra <em>quando</em> un evento è
stato registrato e che non è stato alterato da allora. Non dimostra che il registro
sia <em>completo</em>: nessun sistema volontario può farlo, e il registro è compilato
dall'AI su sé stessa. Non è stata osservata la parte di lavoro avvenuta fuori dalla
conversazione registrata. L'attribuzione ideativa è un giudizio, non una misura: su
giudizi di questo tipo l'accordo fra annotatori indipendenti, in letteratura, si ferma
attorno a 0,66 di alfa. Prendete i due numeri in cima come ordini di grandezza
dichiarati in buona fede, non come cifre esatte.</p>
{extra}
</details>

</div><div id="tip" role="status"></div>
<script>
const b=document.body,tip=document.getElementById('tip');
const B={{lex:document.getElementById('b-lex'),idea:document.getElementById('b-idea'),
 off:document.getElementById('b-off')}};
function set(v){{b.dataset.evid=v==='off'?'off':'on';if(v!=='off')b.dataset.vista=v;
 for(const k in B)B[k].setAttribute('aria-pressed',k===v);}}
for(const k in B)B[k].onclick=()=>set(k);
function show(e,t){{tip.textContent=t;tip.style.opacity=1;
 const r=tip.getBoundingClientRect();let x=e.clientX+14,y=e.clientY+16;
 if(x+r.width>innerWidth-8)x=innerWidth-r.width-8;
 if(y+r.height>innerHeight-8)y=e.clientY-r.height-12;
 tip.style.left=x+'px';tip.style.top=y+'px';}}
document.querySelectorAll('[data-tip]').forEach(el=>{{
 el.addEventListener('mousemove',e=>show(e,el.dataset.tip));
 el.addEventListener('mouseleave',()=>tip.style.opacity=0);
 el.addEventListener('focus',()=>{{const r=el.getBoundingClientRect();
  show({{clientX:r.left,clientY:r.bottom}},el.dataset.tip);}});
 el.addEventListener('blur',()=>tip.style.opacity=0);}});
</script></body></html>"""

open("pagina_di_verifica.html", "w", encoding="utf-8").write(HTML)
print(f"pagina_di_verifica.html — AI lessicale {pct(ai_lex)}% · ideativa {pct(ai_idea)}%")

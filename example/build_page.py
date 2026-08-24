#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Fabio Chinaglia
"""
Generate the verification page from the annotated spans.

Reads spans.json, kpi.json, events.jsonl and case.json.
Writes index.html: a self-contained document, no external dependencies. The name
is the address — served as an index, a case's URL ends at the folder, which is
what survives a link detector that cuts at the first underscore. A page under any
other name answers 404 at the address the note beneath the article prints.

case.json:
  {"title": "...", "author": "...", "date": "19 August 2026",
   "reconstructed": false, "extra_notes": "..."}          # a string, or a list of them

Validated palette: blue #2a78d6 / grey #7a7975 / red #e34948 on a light #fcfcfb
and a dark #1a1a19 surface. CVD (protanopia) separation dE 21.6 light / 19.2
dark; contrast of the text over the background tints always above 11:1.
Redundant encoding: background + underline + accessible label.
"""
import html
import json
import os
import re
import sys

spans = json.load(open("spans.json", encoding="utf-8"))
kpi = json.load(open("kpi.json", encoding="utf-8"))
case = json.load(open("case.json", encoding="utf-8")) if os.path.exists("case.json") else {}
events = [json.loads(r) for r in open("events.jsonl", encoding="utf-8") if r.strip()] \
    if os.path.exists("events.jsonl") else []

root = events[-1]["hash"] if events else "—"
n_decisions = sum(1 for e in events if e.get("type") == "editorial_decision")
total = kpi["words"]

PHASE_LABEL = {"research": "Research", "outline": "Outline",
               "first_draft": "First draft",
               "content_revision": "Content revision",
               "copy_revision": "Copy revision", "titling": "Titling"}
ORIGINS = [("U", "human"), ("UA", "mixed"), ("A", "AI")]


def pct(x):
    return f"{x:.1f}"


def share(key, sel=None):
    ss = [s for s in spans if sel is None or sel(s)]
    t = sum(s["words"] for s in ss) or 1
    return {k: 100 * sum(s["words"] for s in ss if s[key] == k) / t for k, _ in ORIGINS}, t


bars = []
for pk, data in kpi["by_phase"].items():
    q, t = share("lex", lambda s, p=pk: s["phase"] == p)
    seg = "".join(
        f'<div class="seg s-{k}" style="flex:{q[k]:.5f}" '
        f'data-tip="{PHASE_LABEL.get(pk, pk)} · {lbl}: {pct(q[k])}% '
        f'({round(q[k]*t/100)} words)"></div>'
        for k, lbl in ORIGINS if q[k] > 0)
    # Two numbers per phase, because the bar shows one axis and a reader who takes the
    # figure beside it for the whole answer is reading the words as if they were the
    # ideas. The phases are exactly where the two come apart.
    bars.append(f'<div class="row"><div class="label">{PHASE_LABEL.get(pk, pk)}</div>'
                f'<div class="bar">{seg}</div>'
                f'<div class="value" data-tip="{PHASE_LABEL.get(pk, pk)} · AI share of '
                f'the words">{pct(data["ai_lexical"])}%</div>'
                f'<div class="value" data-tip="{PHASE_LABEL.get(pk, pk)} · AI share of '
                f'the ideas">{pct(data["ai_ideational"])}%</div>'
                f'<div class="words">{t}</div></div>')

blocks, cur = [], None
for s in spans:
    if cur is None or s["block"] != cur[0]:
        cur = (s["block"], [])
        blocks.append(cur)
    cur[1].append(s)


def inline(t):
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html.escape(t))


def mark(s, text):
    tip = PHASE_LABEL.get(s["phase"], s["phase"])
    if s["event"]:
        tip += f' · edit {s["event"]}'
    if s["note"]:
        tip += f' — {s["note"]}'
    lab = {"U": "human", "A": "AI", "UA": "mixed"}[s["lex"]]
    return (f'<span class="pv" data-lex="{s["lex"]}" data-idea="{s["idea"]}" '
            f'data-tip="{html.escape(tip)}" tabindex="0" '
            f'aria-label="origin {lab}">{inline(text)}</span>')


out = []
for bi, ss in blocks:
    t0 = ss[0]["text"]
    if ss[0]["heading"]:
        lvl = 1 if t0.startswith("# ") else 2
        title = re.sub(r"^#+\s*", "", t0)
        out.append(f'<h{lvl}>{mark(ss[0], title)}</h{lvl}>')
    elif t0.lstrip().startswith("-"):
        li = [f'<li>{mark(s, r.strip()[1:].strip())}</li>'
              for s in ss for r in s["text"].split("\n") if r.strip().startswith("-")]
        out.append("<ul>" + "".join(li) + "</ul>")
    else:
        out.append("<p>" + " ".join(mark(s, s["text"]) for s in ss) + "</p>")
article_html = "\n".join(out)

table_rows = []
for pk, data in kpi["by_phase"].items():
    q, t = share("lex", lambda s, p=pk: s["phase"] == p)
    # The ideational figure comes from kpi.json rather than being recomputed here, so
    # the page cannot print a per-phase number that differs from the measured one.
    table_rows.append(f"<tr><td>{PHASE_LABEL.get(pk, pk)}</td><td class='n'>{t}</td>"
                      f"<td class='n'>{pct(q['U'])}</td><td class='n'>{pct(q['UA'])}</td>"
                      f"<td class='n'>{pct(q['A'])}</td>"
                      f"<td class='n'>{pct(data['ai_ideational'])}</td></tr>")

ai_lex, ai_idea = kpi["ai_lexical"], kpi["ai_ideational"]
reconstructed = case.get("reconstructed", False)
warning = ("<p class=\"note\" style=\"border-left-color:var(--ai)\">Warning: this "
           "register was compiled <strong>after</strong> the text was written. The "
           "percentages are a reconstruction, not a measurement of the process: read "
           "them as orders of magnitude declared in good faith.</p>") if reconstructed else ""
# extra_notes is a string in every example and every case written so far. Iterating
# it as if it were a list yields one paragraph per character, which is what shipped:
# accept both shapes and let a plain string stay one note.
# The coverage result has lived in kpi.json and in the terminal of whoever ran the
# script, which is to say nowhere a reader could reach it. A check nobody can see is
# not a check a reader can rely on, and this method is not entitled to one of those.
# The technical line sends the reader here; here has to send them on to the files, or
# the door opens onto a wall. Nothing to show if the case does not say where it lives.
reg_url = case.get("register_url") or case.get("url_registro") or ""
reg_link = (f'<span><a href="{html.escape(reg_url, quote=True)}">the register and '
            f'every file</a></span>') if reg_url else ""

def refuse_if_ungated(kpi, path="kpi.json"):
    """A caller that ignores an exit status must not get past this.

    measure.py refuses to write a measurement that failed its checks, so a kpi.json
    saying otherwise means someone kept an old one, or edited it. Publishing from it
    would put numbers on a page that the checks never passed.
    """
    if kpi.get("unexplained"):
        sys.exit(f"{path}: {len(kpi['unexplained'])} declared changes with no span and "
                 f"no reason ({', '.join(kpi['unexplained'])}) — run measure.py first")
    if kpi.get("integrity") is False:
        sys.exit(f"{path}: the reconstruction check failed — run measure.py first")


refuse_if_ungated(kpi)

orphans = kpi.get("orphans") or []
explained = kpi.get("explained") or {}
# Derived here, not read from kpi.json: a measurement file written before the field
# existed has no "unexplained" key, and trusting its absence would print "all declared"
# over a table of changes nobody declared.
unexplained = [o for o in orphans if not explained.get(o)]
if not orphans:
    coverage_meta = "coverage: every declared change has a span"
    coverage_block = ""
else:
    coverage_meta = (f"coverage: {len(orphans)} changes without a span, "
                     + ("all declared" if not unexplained
                        else f"{len(unexplained)} undeclared"))
    rows = "".join(
        f"<tr><td><code>{html.escape(k)}</code></td><td>"
        f"{html.escape(explained.get(k) or '— not declared')}</td></tr>"
        for k in orphans)
    coverage_block = (
        '<h2 class="sect">Changes without a span</h2>'
        '<p class="note">The register declares these interventions and the annotation '
        'attaches none of them to a piece of the final text. That is expected for an '
        'edit a later one replaced, and for a diffuse pass recorded as an event without '
        'touching the attributions. Each is listed with the reason the author gave; '
        'anything marked as not declared is an open question about this measurement.</p>'
        f'<table><thead><tr><th>change</th><th>why it has no span</th></tr></thead>'
        f'<tbody>{rows}</tbody></table>')

notes = case.get("extra_notes") or []
if isinstance(notes, str):
    notes = [notes]
extra = "".join(f"<p>{html.escape(n)}</p>" for n in notes)

HTML = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>How this was written — provenance register</title>
<style>
:root {{ color-scheme:light;
  --surface-1:#fcfcfb; --surface-2:#f4f3f0; --line:#e2e0da;
  --text-primary:#0b0b0b; --text-secondary:#52514e; --text-muted:#7a7975;
  --human:#2a78d6; --mixed:#7a7975; --ai:#e34948;
  --bg-mixed:#eaeae8; --bg-ai:#f8dfde; }}
@media (prefers-color-scheme:dark) {{ :root:where(:not([data-theme="light"])) {{
  color-scheme:dark;
  --surface-1:#1a1a19; --surface-2:#232322; --line:#3a3a37;
  --text-primary:#fff; --text-secondary:#c3c2b7; --text-muted:#8a8983;
  --human:#3987e5; --mixed:#8a8983; --ai:#e66767;
  --bg-mixed:#333230; --bg-ai:#573130; }} }}
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
.note{{font-size:13.5px;color:var(--text-secondary);background:var(--surface-2);
 border-left:2px solid var(--line);padding:12px 16px;border-radius:0 8px 8px 0;margin:0 0 24px}}
h2.sect{{font-size:13px;letter-spacing:.06em;text-transform:uppercase;
 color:var(--text-muted);margin:44px 0 16px;font-weight:600}}
.row{{display:grid;grid-template-columns:160px 1fr 52px 52px 46px;align-items:center;
 gap:12px;margin-bottom:9px}}
.label{{font-size:13px;color:var(--text-secondary)}}
.bar{{display:flex;gap:2px;height:20px}}
.seg{{min-width:2px}} .seg:first-child{{border-radius:4px 0 0 4px}}
.seg:last-child{{border-radius:0 4px 4px 0}} .seg:only-child{{border-radius:4px}}
.s-U{{background:var(--human)}} .s-UA{{background:var(--mixed)}} .s-A{{background:var(--ai)}}
.value{{font-size:13px;text-align:right;font-variant-numeric:tabular-nums}}
.words{{font-size:12px;color:var(--text-muted);text-align:right;
 font-variant-numeric:tabular-nums}}
.legend{{display:flex;flex-wrap:wrap;gap:18px;margin:16px 0 0;font-size:13px;
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
body[data-view="lex"] .pv[data-lex="U"],
body[data-view="idea"] .pv[data-idea="U"]{{background:transparent}}
body[data-view="lex"] .pv[data-lex="UA"],
body[data-view="idea"] .pv[data-idea="UA"]{{background:var(--bg-mixed);
 text-decoration:underline dotted var(--mixed) 2px;text-underline-offset:.2em}}
body[data-view="lex"] .pv[data-lex="A"],
body[data-view="idea"] .pv[data-idea="A"]{{background:var(--bg-ai);
 text-decoration:underline solid var(--ai) 2px;text-underline-offset:.2em}}
body[data-highlight="off"] .pv{{background:transparent!important;text-decoration:none!important}}
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
 .row{{grid-template-columns:92px 1fr 46px 46px}} .words{{display:none}} }}
</style></head>
<body data-view="lex" data-highlight="on"><div class="wrap">

<header class="top">
<p class="kicker">Provenance register</p>
<h1 class="page">How <em>{html.escape(case.get('title','—'))}</em> was written</h1>
<p class="sub">This text was written by a person with the assistance of a language
model. Every intervention was recorded as it happened. It is all below: how much,
where, and whose is what.</p>
<div class="meta">
<span>{html.escape(case.get('author','—'))}</span>
<span>{html.escape(case.get('date','—'))}</span>
<span>{total} words · {len(spans)} spans</span>
<span>{len(events)} events · {n_decisions} editorial decisions</span>
<span>hash chain root <code>{root[:16]}…</code></span>
<span>{coverage_meta}</span>
{reg_link}
</div></header>

{warning}
<div class="tiles">
<div class="tile"><div class="n">{pct(ai_lex)}%</div>
<div class="k">of the words were written by the AI</div>
<div class="d">The words you read in the final text. Includes the rephrasing of
sentences whose content is the author's.</div></div>
<div class="tile"><div class="n">{pct(ai_idea)}%</div>
<div class="k">of the content comes from the AI</div>
<div class="d">The ideas those words express, regardless of who put them into
sentences.</div></div>
</div>
<p class="note">The two numbers differ by {pct(abs(ai_lex-ai_idea))} points, and the
difference is the most informative thing on this page. Mixed is counted as half.</p>

<h2 class="sect">Where the AI came in</h2>
{''.join(bars)}
<div class="legend">
<span class="chip"><i class="sw" style="background:var(--human)"></i>human</span>
<span class="chip"><i class="sw" style="background:var(--mixed)"></i>mixed</span>
<span class="chip"><i class="sw" style="background:var(--ai)"></i>AI</span>
<span style="color:var(--text-muted)">the bar is the words; the two percentages are the
AI share of the words and of the ideas</span>
</div>

<h2 class="sect">The text, span by span</h2>
<div class="ctrl">
<button id="b-lex" aria-pressed="true">words</button>
<button id="b-idea" aria-pressed="false">ideas</button>
<button id="b-off" aria-pressed="false">no highlighting</button>
<span style="color:var(--text-muted)">hover a passage to see its phase and the
intervention</span></div>
<article>{article_html}</article>

<p class="note" style="margin-top:32px">Text that is not highlighted is the author's.
The highlighting is not a statistical estimate: it is the record of what happened while
the text was being written. It says nothing about the quality of what is highlighted,
nor does it imply that the author does not answer for every word: editorial
responsibility for the text is entirely theirs.</p>

<h2 class="sect">Table</h2>
<table><thead><tr><th>phase</th><th class="n">words</th><th class="n">human words %</th>
<th class="n">mixed words %</th><th class="n">AI words %</th><th class="n">AI ideas %</th>
</tr></thead><tbody>{''.join(table_rows)}</tbody></table>
<p class="note" style="margin-top:16px">The three middle columns are the composition of
the words in that phase — the author's, indivisible mixed, the AI's — and they add up to
a hundred. The last column is on the other axis: the AI share of the ideas, with mixed
counted as half.</p>

{coverage_block}

<details><summary>Method, and what this page does not prove</summary>
<p><strong>How it was produced.</strong> Every request from the author and every output
from the model was recorded in an append-only log with a hash chain: each event is bound
to the previous one, so altering a past event invalidates every hash that follows it.
Editorial decisions are recorded one by one. The attribution of the spans was compiled
from that register, and the reconstruction check confirms that concatenating the spans
reproduces the published text exactly.</p>
<p><strong>What it does not prove.</strong> The chain proves <em>when</em> an event was
recorded and that it has not been altered since. It does not prove that the register is
<em>complete</em>: no voluntary system can, and the register is compiled by the AI about
itself. The part of the work that happened outside the recorded conversation was not
observed. Ideational attribution is a judgment, not a measurement: on judgments of this
kind, agreement between independent annotators, in the literature, stops at around 0.66
alpha. Take the two numbers at the top as orders of magnitude declared in good faith,
not as exact figures.</p>
{extra}
</details>

</div><div id="tip" role="status"></div>
<script>
const b=document.body,tip=document.getElementById('tip');
const B={{lex:document.getElementById('b-lex'),idea:document.getElementById('b-idea'),
 off:document.getElementById('b-off')}};
function set(v){{b.dataset.highlight=v==='off'?'off':'on';if(v!=='off')b.dataset.view=v;
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

# index.html, and nothing writes verification.html any more: two manifest-covered
# files with identical content are two things that can drift apart, and the one
# name the address needs is this one.
open("index.html", "w", encoding="utf-8").write(HTML)
print(f"index.html — AI lexical {pct(ai_lex)}% · ideational {pct(ai_idea)}%")
